# coding: utf-8
from . import __name__ as MODULE_NAME
from . import errors
from .column_metadata import ColumnMetaData
from .var import Var
from .driver import DbType


class Cursor(object):
    __module__ = MODULE_NAME
    _cyobj = None

    def __init__(self, connection):
        self.connection = connection
        self._cyobj = connection._cyobj.create_cursor_impl(False)
        
    def __del__(self):
        if self._cyobj is not None:
            self._cyobj.close(in_del=True)

    def __enter__(self):
        self._verify_open()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._verify_open()
        self._cyobj.close(in_del=True)
        self._cyobj = None

    def __repr__(self):
        cls_name = "{}.{}".format(self.__class__.__module__, self.__class__.__name__)
        return "<{} on {!r}>".format(cls_name, self.connection)

    def __iter__(self):
        return self

    def next(self):
        self._verify_fetch()
        row = self._cyobj.fetch_next_row(self)
        if row is not None:
            return row
        raise StopIteration

    def _get_gci_attr(self, attr_num, attr_type):
        self._verify_open()
        return self._cyobj._get_gci_attr(attr_num, attr_type)

    def _set_gci_attr(self, attr_num, attr_type, value):
        self._verify_open()
        self._cyobj._set_gci_attr(attr_num, attr_type, value)
        
        
    @staticmethod
    def _check_proc_args(parameters, keyword_parameters):
        if parameters is not None and not isinstance(parameters, (list, tuple)):
            errors.raise_error(errors.ERR_ARGS_MUST_BE_LIST_OR_TUPLE)
        if keyword_parameters is not None and not isinstance(
            keyword_parameters, dict
        ):
            errors.raise_error(errors.ERR_KEYWORD_ARGS_MUST_BE_DICT)

    def _call(
        self,
        name,
        parameters,
        keyword_parameters,
        return_value=None,
    ):
        self._check_proc_args(parameters, keyword_parameters)
        self._verify_open()
        statement, bind_values = self._call_get_execute_args(
            name, parameters, keyword_parameters, return_value
        )
        return self.execute(statement, bind_values)

    def _call_get_execute_args(
        self,
        name,
        parameters,
        keyword_parameters,
        return_value=None,
    ):
        bind_names = []
        bind_values = []
        statement_parts = ["begin "]
        if return_value is not None:
            statement_parts.append(":retval := ")
            bind_values.append(return_value)
        statement_parts.append(name + "(")
        if parameters:
            bind_values.extend(parameters)
            bind_names = [":%d" % (i + 1) for i in range(len(parameters))]
        if keyword_parameters:
            for arg_name, arg_value in keyword_parameters.items():
                bind_values.append(arg_value)
                bind_names.append("{} => :{}".format(arg_name, len(bind_names) + 1))
        statement_parts.append(",".join(bind_names))
        statement_parts.append("); end;")
        statement = "".join(statement_parts)
        return (statement, bind_values)    
    
    def _prepare(
        self, statement, tag=None, cache_statement=True
    ):
        self._cyobj.prepare(statement, tag, cache_statement)

    def _prepare_for_execute(
        self, statement, parameters, keyword_parameters=None
    ):
        self._verify_open()
        self._cyobj._prepare_for_execute(
            self, statement, parameters, keyword_parameters
        )

    def _verify_fetch(self):
        self._verify_open()
        if not self._cyobj.is_query(self):
            errors.raise_error(errors.ERR_NOT_A_QUERY)

    def _verify_open(self):
        if self._cyobj is None:
            errors.raise_error(errors.ERR_CURSOR_NOT_OPEN)
        self.connection._verify_connected()

    def _convert_unicode(self, value):
        if isinstance(value, unicode):
            return value.encode(self.connection.client_locale)
        return value

    def _convert_parameters(self, parameters):
        if hasattr(parameters, '__iter__'):
            new_parameters = []
            for params in parameters:
                if isinstance(params, (tuple, list)):
                    new_params = [self._convert_unicode(param) for param in params]
                    new_parameters.append(new_params)
                elif isinstance(params, dict):
                    new_params = {key: self._convert_unicode(param) for key, param in params.items()}
                    new_parameters.append(new_params)
                else:
                    new_parameters.append(params)
            return new_parameters
        return parameters
    

    def callproc(
        self,
        name,
        parameters=None,
        keyword_parameters=None,
        keywordParameters=None,
    ):
        if keywordParameters is not None:
            if keyword_parameters is not None:
                errors.raise_error(
                    errors.ERR_DUPLICATED_PARAMETER,
                    deprecated_name="keywordParameters",
                    new_name="keyword_parameters",
                )
            keyword_parameters = keywordParameters
        self._call(name, parameters, keyword_parameters)
        if parameters is None:
            return []
        return [
            v.get_value(0) for v in self._cyobj.bind_vars[: len(parameters)]
        ]

    def execute(
        self,
        statement,
        parameters=None,
        **keyword_parameters
    ):
        statement = self._convert_unicode(statement)
        if isinstance(parameters, (list, tuple)):
            parameters = [self._convert_unicode(p) for p in parameters]
        if isinstance(keyword_parameters, dict):
            keyword_parameters = {
                k: self._convert_unicode(v)
                for k, v in keyword_parameters.items()
            }
        self._prepare_for_execute(statement, parameters, keyword_parameters)
        impl = self._cyobj
        impl.execute(self)
        if impl.fetch_vars is not None:
            return self

    def executemany(
        self,
        statement,
        parameters,
        batcherrors=False,
        arraydmlrowcounts=False,
    ):
        self._verify_open()        
        statement = self._convert_unicode(statement)
        parameters = self._convert_parameters(parameters)
        num_execs = self._cyobj._prepare_for_executemany(
            self, statement, parameters
        )
        self._cyobj.executemany(
            self, num_execs, bool(batcherrors), bool(arraydmlrowcounts)
        )

    def fetchall(self):
        self._verify_fetch()
        result = []
        fetch_next_row = self._cyobj.fetch_next_row
        while True:
            row = fetch_next_row(self)
            if row is None:
                break
            result.append(row)
        return result

    def fetchmany(self, size=None, numRows=None):
        self._verify_fetch()
        if size is None:
            if numRows is not None:
                size = numRows
            else:
                size = self._cyobj.arraysize
        elif numRows is not None:
            errors.raise_error(
                errors.ERR_DUPLICATED_PARAMETER,
                deprecated_name="numRows",
                new_name="size",
            )
        result = []
        fetch_next_row = self._cyobj.fetch_next_row
        while len(result) < size:
            row = fetch_next_row(self)
            if row is None:
                break
            result.append(row)
        return result

    def fetchone(self):
        self._verify_fetch()
        return self._cyobj.fetch_next_row(self)

    def parse(self, statement):
        self._verify_open()
        self._prepare(statement)
        self._cyobj.parse(self)

    def bindnames(self):
        self._verify_open()
        if self._cyobj.statement is None:
            errors.raise_error(errors.ERR_NO_STATEMENT_PREPARED)
        return self._cyobj.get_bind_names()

    def close(self):
        self._verify_open()
        self._cyobj.close()
        self._cyobj = None

    def setinputsizes(self, *args, **kwargs):
        if args and kwargs:
            errors.raise_error(errors.ERR_ARGS_AND_KEYWORD_ARGS)
        elif args or kwargs:
            self._verify_open()
            return self._cyobj.setinputsizes(self.connection, args, kwargs)
        return []

    def setoutputsize(self, size, column=0):
        pass

    def prepare(
        self, statement, tag=None, cache_statement=True
    ):
        self._verify_open()
        self._prepare(statement, tag, cache_statement)

    def var(
        self,
        typ,
        size=0,
        arraysize=1,
        inconverter=None,
        outconverter=None,
        encoding_errors=None,
        bypass_decode=False,
        convert_nulls=False,
        encodingErrors=None,
    ):
        self._verify_open()
        if encodingErrors is not None:
            if encoding_errors is not None:
                errors.raise_error(
                    errors.ERR_DUPLICATED_PARAMETER,
                    deprecated_name="encodingErrors",
                    new_name="encoding_errors",
                )
            encoding_errors = encodingErrors
        return self._cyobj.create_var(
            self.connection,
            typ,
            size,
            arraysize,
            inconverter,
            outconverter,
            encoding_errors,
            bypass_decode,
            convert_nulls=convert_nulls,
        )

    def arrayvar(
        self,
        typ,
        value,
        size=0,
    ):
        self._verify_open()
        if isinstance(value, list):
            num_elements = len(value)
        elif isinstance(value, int):
            num_elements = value
        else:
            raise TypeError("expecting integer or list of values")
        var = self._cyobj.create_var(
            self.connection,
            typ,
            size=size,
            num_elements=num_elements,
            is_array=True,
        )
        if isinstance(value, list):
            var.setvalue(0, value)
        return var

    @property
    def arraysize(self):
        self._verify_open()
        return self._cyobj.arraysize

    @arraysize.setter
    def arraysize(self, value):
        self._verify_open()
        if not isinstance(value, int) or value <= 0:
            errors.raise_error(errors.ERR_INVALID_ARRAYSIZE)
        self._cyobj.arraysize = value

    @property
    def bindvars(self):
        self._verify_open()
        return self._cyobj.get_bind_vars()

    @property
    def description(self):
        self._verify_open()
        if self._cyobj.is_query(self):
            return [
                ColumnMetaData._create_with_cyobj(i) for i in self._cyobj.column_metadata_impls
            ]

    @property
    def fetchvars(self):
        self._verify_open()
        return self._cyobj.get_fetch_vars()

    @property
    def inputtypehandler(self):
        self._verify_open()
        return self._cyobj.inputtypehandler

    @inputtypehandler.setter
    def inputtypehandler(self, value):
        self._verify_open()
        self._cyobj.inputtypehandler = value

    @property
    def lastrowid(self):
        self._verify_open()
        lastrowid = self._cyobj.get_lastrowid()
        return int(lastrowid) if lastrowid else None

    @property
    def outputtypehandler(self):
        self._verify_open()
        return self._cyobj.outputtypehandler

    @outputtypehandler.setter
    def outputtypehandler(self, value):
        self._verify_open()
        self._cyobj.outputtypehandler = value

    @property
    def prefetchrows(self):
        self._verify_open()
        return self._cyobj.prefetchrows

    @prefetchrows.setter
    def prefetchrows(self, value):
        self._verify_open()
        self._cyobj.prefetchrows = value


    @property
    def rowcount(self):
        if self._cyobj is not None and self.connection._cyobj is not None:
            return self._cyobj.rowcount
        return -1

    @property
    def rowfactory(self):
        self._verify_open()
        return self._cyobj.rowfactory

    @rowfactory.setter
    def rowfactory(self, value):
        self._verify_open()
        self._cyobj.rowfactory = value

    @property
    def scrollable(self):
        self._verify_open()
        return False
    
    @property
    def statement(self):
        if self._cyobj is not None:
            return self._cyobj.statement

    @property
    def warning(self):
        self._verify_open()
        return self._cyobj.warning
