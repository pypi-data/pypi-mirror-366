from peewee import IntegerField, CharField, AutoField, ForeignKeyField
from mxupy import TreeEntityX
import bigOAINet as bigo

class RightCategory(TreeEntityX):
    
    rightCategoryId = AutoField()
    
    # 名称、名称路径、编码、编码路径
    name = CharField()
    namePath = CharField()
    code = CharField()
    codePath = CharField()
    
    parent = ForeignKeyField('self', column_name='parentId', field='rightCategoryId', backref='children', on_delete='CASCADE', default=None, null=True)
    # parent = DeferredForeignKey('self', column_name='parentId', backref='children', on_delete='CASCADE', null=True,  field='rightCategoryId')
    
    
    @property
    def roleRightList(self):
        return self._roleRightList
    @roleRightList.setter
    def roleRightList(self, value):
        self._roleRightList = value
        
    # @classmethod
    # def bind_parent(cls):
    #     """在子类中绑定实际的外键关系"""
    #     # cls.parent.field = 'rightCategoryId'
    #     cls.parent.bind(cls, name="rightCategoryId")
    #     # def bind(self, model, name, set_attribute=True):
    
    class Meta:
        model_name = '权限分类'
        # id_field_name = 'rightCategoryId'
        database = bigo.db
    

# from ...db.Database import db
# RightCategory._meta.database = bigo.db
