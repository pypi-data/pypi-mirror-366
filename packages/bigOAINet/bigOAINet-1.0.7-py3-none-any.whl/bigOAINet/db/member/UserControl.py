import hashlib
import uuid as uid
import mxupy as mu
import bigOAINet as bigo

from cachetools import TTLCache
from playhouse.shortcuts import model_to_dict
from mxupy import IM, EntityXControl, AccessToken, dict_to_obj, accesstoken_user_id, skip_check_accesstoken

class UserControl(EntityXControl):
    
    # 登录缓存、最大失败次数
    _login_cache = None
    _login_fail_max_count = None
    
    class Meta:
        model_class = bigo.User
        
    def init_cache(self, config: dict):
        """
        初始化缓存，存储登陆次数
        
        Args:
            config (dict): 配置信息
        """
        config = dict_to_obj(config)
        self._login_cache = TTLCache(
            maxsize=config.cache_max_size, 
            ttl=config.cache_ttl
        )
        self._login_fail_max_count = config.login_fail_max_count
        
    def is_admin(self, userId):
        """ 管理员否

        Args:
            userId (str): 用户id
        """
        def _do():
            
            im = self.get_one_by_id(userId)
            if im.data is None:
                return im.set_error('用户不存在！')
            user = im.data
            im.data = user.roles.split(',').contains('admin')
            return im
        
        return self.run(_do)

    @skip_check_accesstoken
    def register(self, username, nickname, password):
        """ 注册

        Args:
            username (str): 用户名
            nickname (str): 昵称
            password (str): 密码，原码
        """
        def _do():
            
            # 校验密码强度
            im = mu.check_password_strong(password)
            if im.error:
                return im
            
            # 校验用户名是否存在
            im = self.exists({'username':username})
            if im.error:
                return im
            if im.data:
                return IM(False, '用户名已经存在，请使用其他用户名！')
            
            sha256_obj = hashlib.sha256()
            sha256_obj.update(password.encode('utf-8'))
            pwd = sha256_obj.hexdigest()
            
            im = self.add(
                bigo.User(
                    avatar="0",
                    username=username,
                    nickname=nickname,
                    password=pwd,
                    accessToken=uid.uuid4().hex,
                    roles="user"
                )
            )
            if im.error:
                return im
            user = im.data
            user.password = ''
            return IM(True, '恭喜！注册成功。', user)

        return self.run(_do)
    
    @skip_check_accesstoken
    def login(self, username, password, platform='pc'):
        """ 登录

        Args:
            username (str): 用户名
            password (str): 密码
            platform (str, optional): 登录平台. Defaults to 'pc'.
        """
        sup = super()
        def _do():
            
            # 1. 检查是否被锁定
            print(self._login_cache.get(username, 0))
            if self._login_cache.get(username, 0) >= self._login_fail_max_count:
                return IM(False, '登录失败次数过多，请稍后重试！')
            
            # 2. 基础验证
            if not password:
                return IM(False, '密码不能为空', code=500)
            
            # 3. 验证登录
            im = sup.get_one(where=[{'username':username}, {'password':password}])
            
            # 4. 处理失败情况
            if im.error or not im.data:
                self._login_cache[username] = self._login_cache.get(username, 0) + 1
                return IM(False, '用户名或密码错误！') if not im.error else im
            
            # 5. 登录成功处理
            user = im.data
            user.accessToken = mu.AccessToken().create(user.userId, 
                                                       user.roles.split(",") if user.roles else [], 
                                                       user.rights.split(",") if user.rights else [])
            user.password = ''
            self._login_cache[username] = 0
            
            # 6. 登录日志
            im = bigo.LoginControl.inst().add_or_update(user.userId, mu.get_ip(), platform, True)
            if im.error:
                return im
            
            return IM(msg='登录成功！', data=model_to_dict(user, recurse=False, extra_attrs=['accessToken']))
        
        return self.run(_do)

    @skip_check_accesstoken
    def register_and_login(self, username, nickname, password, platform='pc'):
        """ 注册并登录

        Args:
            username (str): 用户名
            nickname (str): 昵称
            password (str): 密码，原码
            platform (str, optional): 登录平台. Defaults to 'pc'.
        """
        im = IM()
        
        if (im := self.register(username, nickname, password)).error:
            return im
        
        sha256_obj = hashlib.sha256()
        sha256_obj.update(password.encode('utf-8'))
        pwd = sha256_obj.hexdigest()
        
        if (im := self.login(username, pwd, platform)).error:
            return im
        
        return im

    def reset_password(self, userId, min_length=8, require_uppercase=True, require_lowercase=True, 
                      require_digits=True, require_special_chars=True, 
                      max_consecutive_duplicates=2):
        """ 重置密码

        Args:
            userId (int): 用户id
        """
        def _do():
            
            pwd = mu.generate_password(min_length=min_length, require_uppercase=require_uppercase, 
                                       require_lowercase=require_lowercase, require_digits=require_digits, 
                                       require_special_chars=require_special_chars, max_consecutive_duplicates=max_consecutive_duplicates)
            
            im = self.update_by_id(userId, { 'password': pwd })
            if im.error:
                return im
            
            return IM(True, '密码重置成功！')

        return self.run(_do)
    
    def update_by_kv(self, userId, key, value):
        """ 用 key he value 修改用户

        Args:
            userId (int): 用户id
            key (str): 键，字段名
            value (any): 值
            
        Returns:
            IM: 结果
        """
        def _do():
            
            return self.update(where={
                'userId': userId
            }, model={
                key: value,
            }, fields=[key])

        return self.run(_do)
    
    def change_password(self, userId, oldPWD, newPWD):
        """ 修改密码

        Args:
            userId (int): 用户id
            oldPWD (str): 旧密码
            newPWD (str): 新密码，需要原码
        """
        def _do():
            
            im = self.exists({'userId':userId, 'password': oldPWD})
            if im.error:
                return im
            
            im = mu.check_password_strong(newPWD)
            if im.error:
                return im

            im = self.update(where={ 'userId': userId }, model={ 'password': newPWD }, fields=['password'])
            if im.error:
                return im
            
            return IM(True, '密码修改成功！')


        return self.run(_do)

    @accesstoken_user_id
    def logout(self, user_id = -1, platform='pc'):
        """ 登出

        Args:
            user_id (int): 用户id
        """

        def _do():
            
            if user_id <= 0:
                return IM(False, '登出失败，用户不存在。')
            
            # 从缓存中删除令牌
            AccessToken().remove(user_id)
            
            user = { 'isOnline': False }
            if (im := self.update_by_id(user_id, user, 'isOnline')).error:
                return im
            
            # 更新状态
            im = bigo.LoginControl.inst().add_or_update(user_id, mu.get_ip(), platform, False)
            if im.error:
                return im
            
            return IM(True, '登出成功。')

        return self.run(_do)
        
    def get_one(self, select=None, where=None, order_by=None, group_by=None, having=None, offset=None, 
                to_dict=False, recurse=False, backrefs=False, extra_attrs=None, max_depth=1):
        """ 获取单条记录【置空密码】

        Args:
            select (list[str]): 选中的字段集
            where (list[dict]|dict): 查询条件字典集
            order_by (list[dict]|dict, optional): 查询排序字典集
            group_by (list[str]|str, optional): 查询分组集
            having (list[dict]|dict, optional): 查询筛选字典集
            offset (int, optional): 从第几条开始
            to_dict (bool, optional): 是否将查询结果转为字典
            recurse (bool, optional): 是否递归地处理外键字段
            backrefs (bool, optional):是否递归地处理反向引用的字段
            extra_attrs (list[str]|str, optional):扩展项集，获取扩展属性
            max_depth (int, optional):是否递归的最大层级
            
        Returns:
            im: 单条记录
        """
        sup = super()
        def _do():
            im = sup.get_one(select=select, where=where, order_by=order_by, group_by=group_by, having=having, offset=offset, 
                        to_dict=to_dict, recurse=recurse, backrefs=backrefs, extra_attrs=extra_attrs, max_depth=max_depth)
            if im.error:
                return im
            
            im.data.password = ''
            return im

        return self.run(_do)
    
    def get_list(self, select=None, where=None, order_by=None, group_by=None, having=None, limit=None, offset=None, 
                 to_dict=False, recurse=False, backrefs=False, extra_attrs=None, max_depth=1):
        """ 获取记录集【置空密码】

        Args:
            select (list[str]): 选中的字段集
            where (list[dict]|dict): 查询条件字典集
            order_by (list[dict]|dict, optional): 查询排序字典集
            group_by (list[str]|str, optional): 查询分组集
            having (list[dict]|dict, optional): 查询筛选字典集
            limit (int, optional): 每页多少条
            offset (int, optional): 从第几条开始
            to_dict (bool, optional): 是否将查询结果转为字典
            recurse (bool, optional): 是否递归地处理外键字段
            backrefs (bool, optional):是否递归地处理反向引用的字段
            extra_attrs (list[str]|str, optional):扩展项集，获取扩展属性
            max_depth (int, optional):是否递归的最大层级
            
        Returns:
            im: 记录集
        """
        sup = super()
        def _do():
            
            im = sup.get_list(select=select, where=where, order_by=order_by, group_by=group_by, having=having, offset=offset, 
                        to_dict=to_dict, recurse=recurse, backrefs=backrefs, extra_attrs=extra_attrs, max_depth=max_depth)
            if im.error:
                return im
            
            # 置空密码
            users = []
            for u in im.data:
                u.password = ''
                users.append(u)
            im.data = users
            
            return im

        return self.run(_do)
    
    @accesstoken_user_id
    def update_self(self, user, fields=['nickname', 'realname', 'avatar'], user_id = -1):
        """ 修改密码

        Args:
            user (model|dict): 修改模型
            fields (list[str]|str, optional): 修改的字段集
            user_id (int): 用户id
        """
        def _do():
            
            im = IM()
            
            if user_id != user.userId:
                return im.set_error('您无权限修改此用户信息！', 403)
            
            fs = ['nickname', 'realname', 'email', 'phone', 'avatar', 'birthday', 'sex', 'address']
            # 只能修改个人信息类的信息，比如昵称、邮箱、手机、头像、生日、性别、地址
            if (im := self.update_by_id(user_id, user, fields=list(set(fields) | set(fs)))).error:
                return im
            
            return IM(True, '修改成功！')

        return self.run(_do)


    