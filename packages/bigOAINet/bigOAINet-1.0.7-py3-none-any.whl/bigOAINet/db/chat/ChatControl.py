from mxupy import IM, EntityXControl, accesstoken_user_id, dict_to_obj

import bigOAINet as bigo

class ChatControl(EntityXControl):
    class Meta:
        model_class = bigo.Chat
    
    @accesstoken_user_id
    def add_my_chat(self, sessionId, content, type='text', conversationId='', user_id = -1):
        """ 
            添加聊天记录

            Args:
                sessionId (str): 会话的唯一标识符，用于标识当前聊天所属的会话。
                content (str): 聊天内容，即用户或系统在聊天中发送的具体文本或其他类型的内容。
                type (str, optional): 聊天内容的类型，默认为 'text'，表示文本内容。其他类型包括：
                    - 'html': HTML 格式的内容
                    - 'markdown': MarkDown 格式的内容
                    - 'table': 表格形式的内容
                    - 'code': 代码形式的内容
                    - 'form': 表单形式的内容
                    - 'chart': 报表形式的内容
                    - 'image': 图片内容
                    - 'audio': 语音内容
                    - 'video': 视频内容
                    - 'download': 下载内容
                    - 'file': 文件内容
                conversationId (str, optional): dify 会话的唯一标识符，用于标识当前聊天所属的会话。
                user_id (int): 用户的唯一标识符，用于标识发送消息的用户。
            Returns:
                IM: 添加结果，通常是一个包含添加操作结果的对象，可能包含成功或失败的状态、错误信息（如果有）、以及添加的聊天记录的唯一标识符或其他相关数据。
        """
        sup = super()
        def _do():
            
            # 获取会话
            if (im := bigo.SessionControl.inst().get_one(select=['roomId','lastChat', 'createUserId'], where={'sessionId':sessionId})).error:
                return im
            if im.data is None:
                return im.set_error('会话不存在')
            session = im.data
            if session.createUserId != user_id:
                return im.set_error('您没有权限。')
            
            # 添加聊天记录
            roomId = im.data.roomId
            rim = sup.add(bigo.Chat(roomId=roomId, content=content, type=type, userId=user_id, session=session))
            if rim.error:
                return rim
            chat = rim.data
            
            # 更新会话的 conversationId
            if conversationId != '':
                session.conversationId = conversationId
                im = bigo.SessionControl.inst().update(model=session, where={'sessionId':sessionId}, fields='conversationId')
                if im.error:
                    return im
            
            # 按道理是要更新会话的 lastChatId 的，但是这个字段在to_dict方法会被干掉，所以这里就用 lastChat 替代
            # 更新会话的 lastChatId
            # 如果是第一次聊天，则更新session的标题
            fields=['lastChat']
            if not session.lastChat:
                session.title = chat.content[:40]
                fields.append('title')
            session.lastChat = chat
            im = bigo.SessionControl.inst().update(model=session, where={'sessionId':sessionId}, fields=fields)
            if im.error:
                return im
            
            im.data = chat
            return im
        
        return self.run(_do)
    
    @accesstoken_user_id
    def get_my_chat_list(self, sessionId, user_id = -1, select=None, order_by=None, group_by=None, having=None, limit=None, offset=None, 
                 to_dict=False, recurse=False, backrefs=False, extra_attrs=None, max_depth=1):
        """ 获取我的聊天记录

        Args:
            sessionId (int): 会话ID
            user_id (int): 用户id
            select (str, optional): 查询字段. Defaults to None.
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
            
        """
        def _do():
            
            im = IM()
            
            if (im := bigo.SessionControl.inst().get_one_by_id(sessionId, select='createUserId')).error:
                return im
            
            if not im.data:
                return im.set_error('会话不存在！')
            
            if im.data.createUserId != user_id:
                return im.set_error('您无权限查看当前会话！')
            
            if (im := self.get_list(select=select, where=[{'sessionId': sessionId}], 
                order_by=order_by, group_by=group_by, having=having, limit=limit, offset=offset, 
                to_dict=to_dict, recurse=recurse, backrefs=backrefs, extra_attrs=extra_attrs, max_depth=max_depth)).error: 
                return im
            
            return im

        return self.run(_do)
    
    @accesstoken_user_id
    def add_bot_chat(self, sessionId, content, type='text', conversationId='', user_id = -1):
        """ 
            添加聊天记录

            Args:
                sessionId (str): 会话的唯一标识符，用于标识当前聊天所属的会话。
                content (str): 聊天内容，即用户或系统在聊天中发送的具体文本或其他类型的内容。
                type (str, optional): 聊天内容的类型，默认为 'text'，表示文本内容。其他类型包括：
                    - 'html': HTML 格式的内容
                    - 'markdown': MarkDown 格式的内容
                    - 'table': 表格形式的内容
                    - 'code': 代码形式的内容
                    - 'form': 表单形式的内容
                    - 'chart': 报表形式的内容
                    - 'image': 图片内容
                    - 'audio': 语音内容
                    - 'video': 视频内容
                    - 'download': 下载内容
                    - 'file': 文件内容
                conversationId (str, optional): dify 会话的唯一标识符，用于标识当前聊天所属的会话。
                user_id (int): 用户的唯一标识符，用于标识发送消息的用户。
            Returns:
                IM: 添加结果，通常是一个包含添加操作结果的对象，可能包含成功或失败的状态、错误信息（如果有）、以及添加的聊天记录的唯一标识符或其他相关数据。
        """
        sup = super()
        def _do():
            
            # 获取会话
            if (im := bigo.SessionControl.inst().get_one(select=['roomId','lastChat', 'createUserId'], where={'sessionId':sessionId})).error:
                return im
            if im.data is None:
                return im.set_error('会话不存在')
            session = im.data
            if session.createUserId != user_id:
                return im.set_error('您没有权限。')
            
            # 添加聊天记录
            roomId = im.data.roomId
            if (im := bigo.RoomControl.inst().get_one(where={'roomId':roomId}, to_dict=True, recurse=True)).error: 
                return im
            
            bot_user_id = dict_to_obj(im.data).agent.botUser
            rim = sup.add(bigo.Chat(roomId=roomId, content=content, type=type, userId=bot_user_id, session=session))
            if rim.error:
                return rim
            chat = rim.data
            
            # 更新会话的 conversationId
            if conversationId != '':
                session.conversationId = conversationId
                im = bigo.SessionControl.inst().update(model=session, where={'sessionId':sessionId}, fields='conversationId')
                if im.error:
                    return im
            
            # 按道理是要更新会话的 lastChatId 的，但是这个字段在to_dict方法会被干掉，所以这里就用 lastChat 替代
            # 更新会话的 lastChatId
            # 如果是第一次聊天，则更新session的标题
            fields=['lastChat']
            if not session.lastChat:
                session.title = chat.content[:40]
                fields.append('title')
            session.lastChat = chat
            im = bigo.SessionControl.inst().update(model=session, where={'sessionId':sessionId}, fields=fields)
            if im.error:
                return im
            
            im.data = chat
            return im
        
        return self.run(_do)
    