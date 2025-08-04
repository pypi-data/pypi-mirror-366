from sqlalchemy.sql.sqltypes import *
from sqlalchemy.ext.compiler import compiles


class TINYINT(SmallInteger):

    __visit_name__ = 'TINYINT'

@compiles(TINYINT, "dlc")
def compile_double(element, compiler, **kwargs):
    return "TINYINT"

class STRUCT(JSON):

    __visit_name__ = 'STRUCT'

@compiles(STRUCT, "dlc")
def compile_double(element, compiler, **kwargs):
    return "STRUCT"

class DOUBLE(Float):

    __visit_name__ = 'DOUBLE'

@compiles(DOUBLE, "dlc")
def compile_double(element, compiler, **kwargs):
    return "DOUBLE"





