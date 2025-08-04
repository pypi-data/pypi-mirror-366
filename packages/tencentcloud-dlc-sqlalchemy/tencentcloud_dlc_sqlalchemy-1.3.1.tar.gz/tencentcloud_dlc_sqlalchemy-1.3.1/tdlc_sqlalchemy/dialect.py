from tdlc_connector import constants
from sqlalchemy.engine import default, reflection
from sqlalchemy.sql import text


from tencentcloud.common import credential
from tencentcloud.dlc.v20210125 import dlc_client, models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

import sqlalchemy.types as sqltypes
import re


from .base import (
    DlcCompiler,
    DlcDDLCompiler,
    DlcExecutionContext,
    DlcIdentifierPreparer,
    DlcTypeCompiler,
)
from . import types


COMPATIBLE_TYPES = {
    "TINYINT"           :types.TINYINT,
    "SMALLINT"          :types.SMALLINT,
    "BIGINT"            :types.BIGINT,
    "INT"               :types.INT,
    "INTEGER"           :types.INTEGER,
    "FLOAT"             :types.FLOAT,
    "DOUBLE"            :types.DOUBLE,
    "DECIMAL"           :types.DECIMAL,

    "BOOLEAN"           :types.BOOLEAN,
    "CHAR"              :types.CHAR,
    "VARCHAR"           :types.VARCHAR,
    "STRING"            :types.String,
    "TEXT"              :types.TEXT,
    "TINYTEXT"          :types.TEXT,
    "MEDIUMTEXT"        :types.TEXT,
    "LONGTEXT"          :types.TEXT,



    "DATE"              :types.DATE,
    "TIME"              :types.TIME,
    "TIMESTAMP"         :types.TIMESTAMP,
    "DATETIME"          :types.DATETIME,

    "JSON"              :types.JSON,
    "ARRAY"             :types.ARRAY,
    "STRUCT"            :types.STRUCT,
    "MAP"               :types.JSON,

    "BOOL"              :types.BOOLEAN,
    "BOOLEAN"           :types.BOOLEAN,
}

TYPE_REGEXP = r'(\w+)(\((\d+)(.+(\d+))?\))?'
def get_column_type(_type):

    m = re.match(TYPE_REGEXP, _type)

    name = m.group(1).upper()
    arg1 = m.group(3)
    arg2 = m.group(5)

    col_type = COMPATIBLE_TYPES.get(name, sqltypes.NullType)
    col_type_kw = {}

    if name in ('CHAR', 'STRING', 'VARCHAR') and arg1 is not None:
        col_type_kw['length'] = int(arg1)
    
    elif name in ('DECIMAL',) and arg1 is not None and arg2 is None:
        col_type_kw['precision'] = int(arg1)
        col_type_kw['scale'] = int(arg2)
    
    return col_type(**col_type_kw)



class DlcDialect(default.DefaultDialect):

    name = "dlc"

    driver = "dlc"

    max_identifier_length = 255

    cte_follows_insert = True

    supports_statement_cache = False

    encoding = 'UTF8'

    default_paramstyle = "pyformat"

    convert_unicode = True

    supports_unicode_statements = True
    
    supports_unicode_binds = True

    description_encoding = None

    postfetch_lastrowid = False

    supports_sane_rowcount = True

    implicit_returninga = False

    supports_sane_multi_rowcount = True

    supports_native_decimal = True

    supports_native_boolean = True

    supports_alter = True

    supports_multivalues_insert = True

    supports_comments = True

    supports_default_values = False

    supports_sequences = False



    preparer = DlcIdentifierPreparer
    ddl_compiler = DlcDDLCompiler
    type_compiler = DlcTypeCompiler
    statement_compiler = DlcCompiler
    execution_ctx_cls = DlcExecutionContext

    catalog = None

    schema = None

    def _get_default_schema_name(self, connection):
        return self.schema

    @classmethod
    def dbapi(cls):
        import tdlc_connector
        return  tdlc_connector
    
    @classmethod
    def import_dbapi(cls):
        import tdlc_connector
        return  tdlc_connector

    def create_connect_args(self, url):
        '''
        RFC1738: https://www.ietf.org/rfc/rfc1738.txt
        dialect+driver://username:password@host:port/database

        支持两种配置方式:

        1. dlc://ak:sk(:token)@region/database?engine=engineName&engine-type&arg1=value1
        2. dlc:///?secretId=1&secretKey=2&token

        {'host': 'ap-shanghai', 'database': 'public-engine:spark', 'username': 'ak', 'password': 'sk:token'}

        '''
        opts = url.translate_connect_args()
        query = dict(url.query)

        region = opts.get('host')
        secret_id = opts.get('username') 
        secret_key = opts.get('password')
        token = opts.pop('token', None)

        if secret_key and secret_key.find(':') > 0:
            secrets = secret_key.split(':')
            secret_key = secrets[0]
            token = secrets[-1]
        
        cred = credential.Credential(
            secret_id=secret_id,
            secret_key=secret_key,
            token=token
        )

        self.dlc_client = dlc_client.DlcClient(cred, region)


        self.schema = opts.get('database')

        self.catalog = opts.get('catalog', None) or query.get('catalog', None) or constants.Catalog.DATALAKECATALOG

        kwargs = {
            'region': region or query.pop('region', None),
            'secret_id': secret_id or query.pop('secretId', None),
            'secret_key': secret_key or query.pop('secretKey', None),
            'token': token or query.pop('token', None),
            'endpoint': query.pop('endpoint', None),
            'engine': query.pop('engine', None),
            'engine_type': query.pop('engineType', constants.EngineType.SPARK),
            'download': query.pop('download', True),
            'mode': query.pop('mode', constants.Mode.ALL),
            'catalog': self.catalog
        }

        return[[], kwargs]
    
    
    
    @reflection.cache
    def get_schema_names(self, connection, **kw):
        """
        Gets all schema names.
        """

        request = models.DescribeDatabasesRequest()
        request.Limit = 1000
        response = self.dlc_client.DescribeDatabases(request)

        return [self.normalize_name(row.DatabaseName) for row in response.DatabaseList]


    def _get_table_names(self, schema, table_type):
        request = models.DescribeTablesNameRequest()
        request.DatabaseName = schema
        request.TableType = table_type
        request.Limit = 1000
        response = self.dlc_client.DescribeTablesName(request)
        return [self.normalize_name(row) for row in response.TableNameList]


    @reflection.cache
    def get_table_names(self, connection, schema=None, **kw):
        """
        Gets all table names.
        """
        schema = schema or self.default_schema_name

        ret = []
        if schema:
            ret = self._get_table_names(schema, "TABLE")

        return ret
    

    @reflection.cache
    def get_view_names(self, connection, schema=None, **kw):
        """
        Gets all view names
        """
        ret = []
        schema = schema or self.default_schema_name

        if schema:
            ret = self._get_table_names(schema, "VIEW")

        return ret
    

    def _get_table(self, table_name, schema):
        request = models.DescribeTableRequest()
        request.DatabaseName = schema
        request.TableName = table_name
        request.DatasourceConnectionName = self.catalog
        response = self.dlc_client.DescribeTable(request)

        table = {}
        table['name'] = response.Table.TableBaseInfo.TableName
        table['schema'] = response.Table.TableBaseInfo.DatabaseName
        table['comment'] = response.Table.TableBaseInfo.TableComment
        table['columns'] = []
        for column in response.Table.Columns:
            table['columns'].append({
                'name': column.Name,
                'type': column.Type,
                'comment': column.Comment,
                'nullable': column.Nullable,
            })
        return table
    
    @reflection.cache
    def get_table_comment(self, connection, table_name, schema, **kw):

        schema = schema or self.default_schema_name

        ret = ""
        if schema:

            table = self._get_table(table_name, schema)
            return {
                "text": table.get("comment", None)
            }

    @reflection.cache
    def get_columns(self, connection, table_name, schema, **kw):

        schema = schema or self.default_schema_name
        ret = []
        if schema:

            table = self._get_table(table_name, schema)

            for row in table['columns']:

                column = {
                    'name': row['name'],
                    'type': get_column_type(row['type'])
                }
                ret.append(column)

        return ret

    def get_indexes(self, connection, table_name, schema, **kw):
        ''' 不支持 '''
        return []
    
    def get_pk_constraint(self, connection, table_name, schema, **kw):
        ''' 不支持 '''
        return []
    
    def get_foreign_keys(self, connection, table_name, schema, **kw):
        ''' 不支持 '''
        return []
    
    def has_table(self, connection, table_name, schema, **kw) -> None:

        schema = schema or self.default_schema_name


        try:
            self._get_table(table_name, schema)
        except TencentCloudSDKException as e:
            code = e.get_code()
            if code and code.startswith("ResourceNotFound"):
                return False
            else:
                raise e
        except Exception as e:
            raise e
        
        return True
    
    def has_index(self, connection, table_name, index_name, schema, **kw):
        return False
    
    def has_sequence(self, connection, sequence_name, schema, **kw) -> None:
        return False



dialect = DlcDialect