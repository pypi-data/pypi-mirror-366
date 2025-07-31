import uuid as uid
from peewee import *
from datetime import datetime, timedelta
import mxupy as mu
from playhouse.shortcuts import model_to_dict
import bigOAINet as bigo
from mxupy import IM, EntityXControl, accesstoken_user_id

class MyDHVoiceControl(EntityXControl):

    class Meta:
        model_class = bigo.MyDHVoice
        
    def __init__(self, *args, **kwargs):
        self.sub_dir = 'digitalHuman/voice/'
        super().__init__(*args, **kwargs)
        
    @accesstoken_user_id
    def get_my_voice_list(self, user_id = -1, where = None, select=None, order_by=None, group_by=None, having=None, limit=None, offset=None, 

                 to_dict=False, recurse=False, backrefs=False, extra_attrs=None, max_depth=1):
        """ 获取我的语音列表

        Args:
            user_id (int): 用户id
            select (str, optional): 查询字段. Defaults to None.
            where (str, optional): 查询条件. Defaults to None.
            order_by (str, optional): 排序字段. Defaults to None.
            group_by (str, optional): 分组字段. Defaults to None.
            having (str, optional): having条件. Defaults to None.
            limit (int, optional): 查询数量. Defaults to None.
            offset (int, optional): 偏移量. Defaults to None.
            to_dict (bool, optional): 是否转为字典. Defaults to False.
            recurse (bool, optional): 是否递归. Defaults to False.
            backrefs (bool, optional): 是否返回引用. Defaults to False.
            extra_attrs (list, optional): 额外的属性. Defaults to None.
            max_depth (int, optional): 最大深度. Defaults to 1.
            
        Returns:
            IM: 查询结果
            
        """
        def _do():
            
            im = IM()
            
            w = [{'userId': user_id}, *(([where] if isinstance(where, dict) else where if isinstance(where, list) else []))]
            
            if (im := self.get_list(select=select, where=w, 
                order_by=order_by, group_by=group_by, having=having, limit=limit, offset=offset, 
                to_dict=to_dict, recurse=recurse, backrefs=backrefs, extra_attrs=extra_attrs, max_depth=max_depth)).error: 
                return im
            
            return im

        return self.run(_do)
    
    @accesstoken_user_id
    def delete_my_voice(self, id, recursive=True, user_id = -1):
        """ 删除我的语音

        Args:
            user_id (int): 用户id
            id (int): 主键id
            recursive (bool): 是否同时删除被引用项
            
        Returns:
            IM: 删除结果
        """
        def _do():
            
            im = IM()
            
            if (im := self.get_one_by_id(id, select='userId')).error: 
                return im
            if not im.data:
                return im.set_error('删除失败。语音不存在。')
            if im.data.userId != user_id:
                return im.set_error('删除失败。您没有权限删除此语音。')
            
            if (im := self.delete_by_id(id, recursive)).error: 
                return im
            
            return im

        return self.run(_do)

    def delete1(self, id, userId, accessToken):
        """
            删除

        Args:
            self: 当前对象的引用。
            id (int): 要删除的资源的唯一标识符。
            userId (int): 请求删除操作的用户的唯一标识符。
            accessToken (str): 用于身份验证的访问令牌。

        Returns:
            IM：结果
        """
        def _do():
            im = IM()
            
            # 检验访问令牌
            im = bigo.UserControl.inst().check_accesstoken(userId, accessToken)
            if im.error:
                return im
            
            cs = [{'myDHVoiceId': id}, {'userId': userId}]
            
            # 查询是否存在 voiceId 这条数据
            im = self.get_one(where=cs)
            if im.error:
                return im
            voice = im.data
            
            # 查询项目是否引用了这个语音模型
            im = bigo.MyDHVideoControl.inst().exists(where=cs)
            if im.error:
                return im
            if im.data:
                return IM(False, '删除失败。已有视频选中了此语音。')

            # 删除
            im = self.delete_by_id(id)
            if im.error:
                return im
            
            return im
            
            # # 删除文件
            # mu.removeFile(mu.file_dir('user',userId) + '\\'  + voice.url)

        return self.run(_do)