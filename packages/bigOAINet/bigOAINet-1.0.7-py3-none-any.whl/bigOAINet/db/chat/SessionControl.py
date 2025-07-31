from mxupy import IM, EntityXControl, accesstoken_user_id
import bigOAINet as bigo

class SessionControl(EntityXControl):
    class Meta:
        model_class = bigo.Session
    @accesstoken_user_id
    def add_my_session(self, agentId, user_id):
        """ 
            通过智能体id获取最后一个会话，如果不存在，则创建一个会话

            Args:
                agentId (int): 智能体id
                user_id (int): 房间创建人id
            Returns:
                IM: 会话
        """
        sup = super()
        def _do():
            
            cs = [{'createUserId':user_id}, {'agentId':agentId}]
            
            # 获取房间
            if (im := bigo.RoomControl.inst().get_one(where=cs)).error:
                return im
            
            # 不存在，则创建
            if im.data is None:
                if (im := bigo.AgentControl.inst().get_one(where={'agentId':agentId})).error:
                    return im
                if im.data is None:
                    return im.set_error('智能体不存在。')
                agent = im.data
                
                
                im = bigo.RoomControl.inst().add(bigo.Room(name=agent.name, thumb=agent.logo, createUser=user_id, desc=agent.desc, agent=agent.agentId))
                if im.error:
                    return im
                room = im.data
                
            room = im.data
            
            # 添加会话
            im = bigo.SessionControl.inst().add(bigo.Session(title=room.name, logo=room.thumb, room=room.roomId, createUser=user_id))
            
            return im
        
        return self.run(_do)
    
    
    @accesstoken_user_id
    def get_my_session_list(self, roomId = -1, user_id = -1, select=None, order_by=None, group_by=None, having=None, limit=None, offset=None, 
                 to_dict=False, recurse=False, backrefs=False, extra_attrs=None, max_depth=1):
        """ 获取我的聊天记录

        Args:
            roomId (int): 房间id
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
            where = {}
            if roomId == -1:
                if (im := bigo.RoomControl.inst().get_one(select='createUserId', where={'createUserId':user_id })).error:
                    return im
                where = {'createUserId':user_id}
            else:
                if (im := bigo.RoomControl.inst().get_one_by_id(roomId, select='createUserId')).error:
                    return im
                where = {'roomId':roomId}
            
            if not im.data:
                return im.set_error('房间不存在！')
            
            if im.data.createUserId != user_id:
                return im.set_error('您无权限查看当前房间！')
            
            if (im := self.get_list(select=select, where=where, 
                order_by=order_by, group_by=group_by, having=having, limit=limit, offset=offset, 
                to_dict=to_dict, recurse=recurse, backrefs=backrefs, extra_attrs=extra_attrs, max_depth=max_depth)).error: 
                return im
            
            return im

        return self.run(_do)