from datetime import datetime
from peewee import IntegerField, CharField, DateTimeField, ForeignKeyField, AutoField, FloatField, BooleanField
from mxupy import EntityX
import bigOAINet as bigo

# 新闻
class LiteNews(bigo.EntityDataX):
    
    liteNewsId = AutoField()

    # 标题、作者、正文、分类、时间
    title = CharField()
    author = CharField()
    content = CharField()
    category = CharField()
    addTime = DateTimeField(default=datetime.now)

    class Meta:
        database = bigo.db
        name = '新闻'