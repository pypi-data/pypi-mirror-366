from peewee import CharField, IntegerField, AutoField, BooleanField, ForeignKeyField, TextField
from mxupy import EntityX
import bigOAINet as bigo

class Rule(EntityX):
    class Meta:
        database = bigo.db
        name = '访问规则'
        
    ruleId = AutoField()
    
    # 优先级
    level = IntegerField()
    # 类型：用户、角色、权限
    type = CharField(default='user')
    # 存入的是数组 如 ['bigo/superadmin', 'bigo/admin']
    # 匿名用户（anonymous）
    # 角色码（bigo/superadmin）（bigo/admin）
    # 权限码（bigOAINet/db/member/User/add）（bigOAINet/db/chat/Chat/delete）
    codes = TextField(default='anonymous')
    
    # true：容许访问，false：禁止访问，注意：禁止访问优先级高于允许访问
    allow = BooleanField(default=True)
    # 停用否
    stop = BooleanField(default=False)
    
    # 访问频率，单位（毫秒）；-1：不限
    frequency = IntegerField(default=1000)
    # 单次最大返回数量
    maxReturnCount = IntegerField(default=1000)
    # 返回数量参数名称，如：limit
    countParamName = CharField(null=True)
    
    # 描述
    desc = TextField(null=True)
    
    # 函数id
    api = ForeignKeyField(bigo.Api, backref='rules', on_delete='CASCADE', column_name='apiId', null=True)
    
    @property
    def typeText(self):
        types = {
            'user': '用户',
            'role': '角色',
            'right': '权限'
        }
        return types.get(self.type, '用户')
    