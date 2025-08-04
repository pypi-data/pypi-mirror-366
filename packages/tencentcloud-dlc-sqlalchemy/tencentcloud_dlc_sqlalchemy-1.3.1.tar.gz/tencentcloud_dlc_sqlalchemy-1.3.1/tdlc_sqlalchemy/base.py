
from sqlalchemy.sql import compiler
from sqlalchemy.engine import default



#https://cloud.tencent.com/document/product/1342/61765
RESERVED_WORDS = frozenset(
    [
        "ALL",
        "ALTER",
        "AND",
        "ANY",
        "AS",
        "AUTHORIZATION",
        "BETWEEN",
        "BOTH",
        "BY",
        "CALL",
        "CASE",
        "CAST",
        "CHECK",
        "CLUSTER",
        "COLLATE",
        "COLUMN",
        "CONSTRAINT",
        "CREATE",
        "CROSS",
        "CUBE",
        "CURRENT_DATE",
        "CURRENT_TIME",
        "CURRENT_TIMESTAMP",
        "CURRENT_USER",
        "CURSOR",
        "DEALLOCATE",
        "DEFAULT",
        "DELETE",
        "DESCRIBE",
        "DISTINCT",
        "DISTRIBUTE",
        "DROP",
        "ELSE",
        "END",
        "ESCAPE",
        "EXCEPT",
        "EXECUTE",
        "EXISTS",
        "EXPLAIN",
        "EXTRACT",
        "FETCH",
        "FILTER",
        "FOR",
        "FOREIGN",
        "FROM",
        "FULL",
        "FALSE",
        "GRANT",
        "GROUP",
        "GROUPING",
        "HAVING",
        "IN",
        "INNER",
        "INSERT",
        "INTERSECT",
        "INTERVAL",
        "INTO",
        "IS",
        "JOIN",
        "LATERAL",
        "LEADING",
        "LEFT",
        "LIKE",
        "LIMIT",
        "LOCALTIME",
        "LOCALTIMESTAMP",
        "MERGE",
        "MINUS",
        "NATURAL",
        "NEW",
        "NEXT",
        "NORMALIZE",
        "NOT",
        "NULL",
        "OFFSET",
        "ONLY",
        "OR",
        "ORDER",
        "OUTER",
        "OVER",
        "OVERLAPS"
        "PARTITION",
        "PATTERN",
        "PERCENTILE_CONT",
        "PERCENTILE_DISC",
        "PERMUTE",
        "PREPARE",
        "PRIMARY",
        "RANGE",
        "RECURSIVE",
        "REFERENCES",
        "RIGHT",
        "ROLLUP",
        "ROW",
        "ROWS",
        "SELECT",
        "SEMI",
        "SESSION_USER",
        "SET",
        "SOME",
        "TABLE",
        "THEN",
        "TIME",
        "TO",
        "TRAILING",
        "TRUE",
        "UESCAPE",
        "UNION",
        "UNIQUE",
        "UNKNOWN",
        "UNNEST",
        "UPDATE",
        "USER",
        "USING",
        "VALUES",
        "WHEN",
        "WHERE",
        "WINDOW"
        "WITH",
        "WITHIN"
    ]
)

class DlcIdentifierPreparer(compiler.IdentifierPreparer):

    reserved_words = { x.lower() for x in RESERVED_WORDS }

    def __init__(self, dialect, **kwargs):
        super().__init__(dialect, initial_quote="`", escape_quote="'")
    
    
    
class DlcCompiler(compiler.SQLCompiler):
    pass
    

class DlcExecutionContext(default.DefaultExecutionContext):
    pass


class DlcDDLCompiler(compiler.DDLCompiler):
    pass


class DlcTypeCompiler(compiler.GenericTypeCompiler):
    pass

