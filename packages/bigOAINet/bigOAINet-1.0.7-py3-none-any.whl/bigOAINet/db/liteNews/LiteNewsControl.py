import uuid as uid
from peewee import *
from datetime import datetime, timedelta
import mxupy as mu
from playhouse.shortcuts import model_to_dict
import bigOAINet as bigo

class LiteNewsControl(mu.EntityXControl):

    class Meta:
        model_class = bigo.LiteNews