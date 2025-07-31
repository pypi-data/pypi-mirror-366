from datetime import datetime
from peewee import AutoField, IntegerField, CharField, DateTimeField, ForeignKeyField
from mxupy import TreeEntityX
import bigOAINet as bigo

class LogCategory(TreeEntityX):
    class Meta:
        database = bigo.db
        name = '日志分类'
        
    logCategoryId = AutoField()
    
    parent = ForeignKeyField('self', column_name='parentId', backref='children', on_delete='CASCADE', default=None, null=True)
    
    name = CharField()
    namePath = CharField()
    logCount = IntegerField()
    addTime = DateTimeField(default=datetime.now)

    