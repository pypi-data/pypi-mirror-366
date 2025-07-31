from peewee import CharField, IntegerField, AutoField, TextField
from mxupy import EntityX
import bigOAINet as bigo

class Api(EntityX):
    class Meta:
        database = bigo.db
        name = 'API'
        
    apiId = AutoField()
    
    # 名称、空间，不支持正则、编码，支持正则、排序、描述
    name = CharField()
    space = CharField()
    codes = TextField()
    sort = IntegerField()
    desc = TextField(null=True)


