# coding: utf-8

from . import __name__ as MODULE_NAME
from . import errors
from .driver import DB_TYPE_BLOB



class LOB(object):
    __module__ = MODULE_NAME
    
    def __str__(self):        
        return str(self.read())

    def __del__(self):
        self._cyobj.free_lob()

    def __reduce__(self):
        value = self.read()
        return (type(value), (value,))

    
    @classmethod
    def _create_with_cyobj(cls, cyobj):
        lob = cls.__new__(cls)
        lob._cyobj = cyobj
        return lob

    def _check_value_to_write(self, value):
        if isinstance(value, bytes):
            return value
        elif isinstance(value, unicode):
            return value.encode(self.encoding)
        else:
            raise TypeError("expecting string or bytes")        

    def close(self):
        self._cyobj.close()

    def getchunksize(self):
        return self._cyobj.get_chunk_size()

    def isopen(self):
        return self._cyobj.get_is_open()

    def open(self):
        self._cyobj.open()

    def read(self, offset=1, amount=None):
        if amount is None:
            amount = self._cyobj.get_max_amount()
            if amount >= offset:
                amount = amount - offset + 1
            else:
                amount = 1
        elif amount <= 0:
            errors.raise_error(errors.ERR_INVALID_LOB_AMOUNT)
        if offset <= 0:
            errors.raise_error(errors.ERR_INVALID_LOB_OFFSET)
        return self._cyobj.read(offset, amount)

    def size(self):
        return self._cyobj.get_size()

    def trim(self, new_size=0, newSize=None):
        if newSize is not None:
            if new_size != 0:
                errors.raise_error(
                    errors.ERR_DUPLICATED_PARAMETER,
                    deprecated_name="newSize",
                    new_name="new_size",
                )
            new_size = newSize
        self._cyobj.trim(new_size)

    def write(self, data, offset=1):
        self._cyobj.write(self._check_value_to_write(data), offset)

    @property
    def type(self):
        return self._cyobj.dbtype

    @property
    def encoding(self):
        if not self._encoding:
            self._encoding = 'utf-8'
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value