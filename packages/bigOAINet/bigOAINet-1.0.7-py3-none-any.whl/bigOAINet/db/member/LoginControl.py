import mxupy as mu
import bigOAINet as bigo
from datetime import datetime
from mxupy import IM, EntityXControl

class LoginControl(EntityXControl):
    class Meta:
        model_class = bigo.Login
        
        
    def add_or_update(self, userId, ip, platform="pc", isOnline=True):
        """
        添加或修改登录记录
        唯一条件（平台 + userId）
        
        参数:
            userId: 用户ID
            ip: IP地址
            platform: 平台（默认"pc"）
            isOnline: 是否在线（默认True）
            
        返回:
            IM类型的结果对象
        """
        im = IM()  # 假设IM是您的结果类
        
        # 获取现有记录
        im = self.get_one(where=[{"userId": userId}, {"platform": platform}])
        if im.error:
            return im
        l = im.data
        
        if l is None:
            # 新建记录
            l = bigo.Login()
            l.userId = userId
            l.ip = ip
            l.isOnline = isOnline
            l.platform = platform
            
            if isOnline:
                l.loginTime = datetime.now()
            else:
                l.logoutTime = datetime.now()
            
            im = self.add(l)
            if im.error:
                return im
        else:
            # 更新现有记录
            l.isOnline = isOnline
            l.ip = ip
            
            if isOnline:
                l.loginTime = datetime.now()
            else:
                l.logoutTime = datetime.now()
            
            fields = ['isOnline','ip'].append(("loginTime" if isOnline else "logoutTime"))
            im = self.update_by_id(l.loginId, l, fields)
            if im.error:
                return im
        
        return im