from peewee import CharField, ForeignKeyField, AutoField
from mxupy import TreeEntityX
import bigOAINet as bigo

class RoleCategory(TreeEntityX):
    
    roleCategoryId = AutoField()
    # 父亲
    parent = ForeignKeyField('self', column_name='parentId', backref='children', on_delete='CASCADE', default=None, null=True)
    
    # 编码、编码路径、名称、名称路径、排序
    code = CharField(max_length=200)
    codePath = CharField(max_length=200, null=True)
    name = CharField(max_length=200)
    namePath = CharField(max_length=200, null=True)
    
    
    
    class Meta:
        database = bigo.db
        name = '角色分类'
