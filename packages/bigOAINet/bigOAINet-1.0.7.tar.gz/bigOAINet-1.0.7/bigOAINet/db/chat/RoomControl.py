from mxupy import IM, EntityXControl, accesstoken_user_id
import bigOAINet as bigo

class RoomControl(EntityXControl):
    class Meta:
        model_class = bigo.Room
    @accesstoken_user_id
    def get_last_session(self, agentId, sessionId = -1, user_id = -1):
        """ 
            通过智能体id获取最后一个会话，如果不存在，则创建一个会话

            Args:
                agentId (int): 智能体id
                sessionId (int): 会话id
                user_id (int): 房间创建人id
            Returns:
                IM: 会话
        """
        sup = super()
        def _do():
            
            if sessionId > 0:
                if (im := bigo.SessionControl.inst().get_one_by_id(sessionId)).error:
                    return im
                if im.data is None:
                    return im.set_error('会话不存在。')
                if im.data.createUserId != user_id:
                    return im.set_error('您没有权限访问此会话。')
                return im
            
            cs = [{'createUserId':user_id}, {'agentId':agentId}]
            
            # 获取会话
            im = bigo.RoomControl.inst().get_one(where=cs)
            if im.error:
                return im
            
            # 不存在，则创建房间
            if im.data is None:
                im = bigo.AgentControl.inst().get_one(where={'agentId':agentId})
                if im.error:
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
            im = bigo.SessionControl.inst().get_one(where={'roomId':room.roomId}, order_by={'createTime':'desc'})
            if im.error:
                return im
            
            # 不存在，则创建
            if im.data is None:
                im = bigo.SessionControl.inst().add(bigo.Session(title=room.name, logo=room.thumb, room=room.roomId, createUser=user_id))
            
            return im
        
        return self.run(_do)
        
        
    
        