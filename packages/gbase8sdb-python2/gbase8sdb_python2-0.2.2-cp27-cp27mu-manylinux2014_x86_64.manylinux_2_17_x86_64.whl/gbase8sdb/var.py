# coding: utf-8

from .driver import DbType


class Var(object):
    def __repr__(self):
        value = self._cyobj.get_all_values()
        if not self._cyobj.is_array and len(value) == 1:
            value = value[0]
        typ = self._type
        return "<gbase8sdb.Var of type {} with value {}>".format(typ.name, repr(value))

    @classmethod
    def _create_with_cyobj(cls, impl, typ=None):
        var = cls.__new__(cls)
        var._cyobj = impl
        if typ is not None:
            var._type = typ
        else:
            var._type = impl.dbtype
        return var

    @property
    def actual_elements(self):
        if self._cyobj.is_array:
            return self._cyobj.num_elements_in_array
        return self._cyobj.num_elements

    @property
    def actualElements(self):
        return self.actual_elements

    @property
    def buffer_size(self):
        return self._cyobj.buffer_size

    @property
    def bufferSize(self):
        return self.buffer_size

    @property
    def convert_nulls(self):
        return self._cyobj.convert_nulls

    def getvalue(self, pos=0):
        return self._cyobj.get_value(pos)

    @property
    def inconverter(self):
        return self._cyobj.inconverter

    @property
    def num_elements(self):
        return self._cyobj.num_elements

    @property
    def numElements(self):
        return self.num_elements

    @property
    def outconverter(self):
        return self._cyobj.outconverter

    def setvalue(self, pos, value):
        self._cyobj.set_value(pos, value)

    @property
    def size(self):
        return self._cyobj.size

    @property
    def type(self):
        return self._type

    @property
    def values(self):
        return self._cyobj.get_all_values()
