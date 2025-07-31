import threading
import bigOAINet as bigo

from typing import List
from datetime import datetime
from mxupy import IM, EntityXControl, get_ip, get_attr, to_int, dict_to_obj, obj_to_dict

class RuleControl(EntityXControl):
    """规则控制类（使用类属性存储缓存）"""
    
    # 类属性存储缓存（全局共享）
    _cache_lock = threading.Lock()
    # 匿名用户用 ip 作为 key，用户用 userId 作为 key
    # {'bigOAINet.db.member.UserControl.logout:ip:127.0.0.1': datetime.datetime(2025, 7, 17, 10, 0, 58, 162890)}
    # {'bigOAINet.db.member.UserControl.logout:user:1': datetime.datetime(2025, 7, 17, 10, 0, 58, 162890)}
    _cache_last_access_time = {}
    # 只存储最终计算后的规则
    # 匿名用户 key 统一为 anonymous，用户用 userId 作为 key
    # 'bigOAINet.db.member.UserControl.logout:user:1' = {'allow': False, 'min_frequency': 0, 'min_max_return': 0, 'count_param_name': None, 'deny_reason': '无权限'}
    # 'bigOAINet.db.member.UserControl.logout' = {'allow': False, 'min_frequency': 0, 'min_max_return': 0, 'count_param_name': None, 'deny_reason': '无权限'}
    _cache_rule = {}
    
    class Meta:
        model_class = bigo.Rule

    def add_rule(self, apiId: int, type: str = "role", codes: str = '*', 
                 level = 1, allow: bool = True, stop: bool = False, 
                 maxReturnCount: int = 1000, countParamName: str = None, frequency: int = 1000, desc: str = "") -> IM:
        """添加访问规则
        
        Args:
            apiId: 关联的API ID
            type: 类型(role/right/user)
            codes: 编码
            
            level: 等级
            allow: 是否允许访问
            stop: 是否停用
            
            maxReturnCount: 单次最大返回数量
            countParamName: 计数参数名
            frequency: 访问频率(毫秒)
            desc: 描述
            
        Returns:
            IM: 操作结果
        """
        sup = super()
        
        def _do():
            im = IM()

            if not codes:
                return im.set_error("添加失败，编码不能为空。")

            # 检查类型是否有效
            if type not in ['user', 'role', 'right']:
                return im.set_error("添加失败，类型必须是user/role/right。")

            return sup.add({
                'apiId': apiId,
                'type': type,
                'level': level,
                'codes': codes,
                'allow': allow,
                'stop': stop,
                'maxReturnCount': maxReturnCount,
                'countParamName': countParamName,
                'frequency': frequency,
                'desc': desc
            }, False)
            
        return self.run(_do)
        
    def check_access(self, functionName: str, params: object = None, 
        user_id: int = -1, user_roles: list[str] = None, user_rights: list[str] = None):
        """检查是否允许访问
        
        Args:
            functionName: 函数名称
            params: 参数
            user_id: 用户ID(-1表示未登录)
            user_roles: 用户角色列表
            user_rights: 用户权限列表
            
        Returns:
            IM: 操作结果(包含是否允许访问及原因)
        """
        im = IM()
        
        cls = self.__class__
        now = datetime.now()
        
        # 获取上次访问时间（使用类属性）
        with cls._cache_lock:
            # 生成缓存键（匿名用户用ip区分）
            ip = '' if user_id > 0 else get_ip()
            last_access_key = f"{functionName}:user:{user_id}" if user_id > 0 else f"{functionName}:ip:{ip}"
            last_access_time = cls._cache_last_access_time.get(last_access_key, datetime(2000, 1, 1))
            cls._cache_last_access_time[last_access_key] = now
        
        # 得到规则
        compiled_rule = self.get_compiled_rule(
            functionName, user_id, user_roles if user_id > 0 else [], user_rights if user_id > 0 else []
        )
        
        # 规则检查逻辑
        if not compiled_rule:
            return im.set_error("访问被拒绝。原因: 无权限，无匹配规则。", 403)

        # 检查是否允许访问
        if not compiled_rule.allow:
            return im.set_error(f"访问被拒绝。原因: {compiled_rule.deny_reason}", 403)
        
        # 频率检查
        if compiled_rule.min_frequency > 0:
            elapsed_ms = (now - last_access_time).total_seconds() * 1000
            if elapsed_ms < compiled_rule.min_frequency:
                return im.set_error(f"访问频率过高。请等待 {compiled_rule.min_frequency - elapsed_ms} 毫秒后再试。", 429)

        # 数量限制检查
        if params and compiled_rule.min_max_return > 0 and compiled_rule.count_param_name:
            request_count = to_int(get_attr(params, compiled_rule.count_param_name, 0))
            if request_count > compiled_rule.min_max_return:
                return im.set_error(f"单次请求最多返回{compiled_rule.min_max_return}条数据。", 400)

        return im
    
    def compile_rules(self, rules):
        """ 编译规则，返回最小频率、最小数量限制和最终是否允许
        
        Args:
            rules (list): 规则列表
            
        return (object): 最小频率、最小数量限制和最终是否允许
        """
        if not rules:
            return None
        
        compiled_rule = dict_to_obj({
            'allow': True,
            'min_frequency': 0,
            'min_max_return': 0,
            'count_param_name': None,
            'deny_reason': ''
        })

        # 1. 排序规则：先按 level 降序，再按 allow 升序（False优先）
        rules_sorted = sorted(rules, key=lambda x: (x.level, x.allow), reverse=True)

        # 2. 直接取排序后的第一条规则作为最终决定
        # 因为排序后高优先级+拒绝规则已经排在前面
        final_rule = rules_sorted[0]

        # 3. 处理拒绝规则
        if not final_rule.allow:
            compiled_rule.allow = False
            compiled_rule.deny_reason = final_rule.desc or '无权限'
            return compiled_rule

        # 4. 处理允许规则
        allow_rules = [r for r in rules_sorted if r.allow]

        # 5. 计算最小频率（取所有允许规则中最严格的值）
        if frequency_rules := [r for r in allow_rules if r.frequency > 0]:
            compiled_rule.min_frequency = max(r.frequency for r in frequency_rules)

        # 6. 计算返回数量限制
        if count_rules := [r for r in allow_rules if r.maxReturnCount > 0 and r.countParamName]:
            strict_rule = min(count_rules, key=lambda x: x.maxReturnCount)
            compiled_rule.min_max_return = strict_rule.maxReturnCount
            compiled_rule.count_param_name = strict_rule.countParamName

        return compiled_rule
    
    def get_compiled_rule(self, functionName, user_id, user_roles, user_rights):
        """ 通用缓存处理逻辑
            同一个函数、同一个用户第一次从数据库中获取规则后，再计算，后面直接从缓存中获取计算好的规则
        
        Args:
            functionName (str): 函数名
            user_id (int): 用户id
            user_roles (list): 用户角色列表
            user_rights (list): 用户权限列表
        """
        cls = self.__class__
        # 统一缓存（认证用户和匿名用户共用，但用不同的 cache_key 区分）
        cache_key = f"{functionName}:user:{user_id}" if user_id > 0 else f"{functionName}"
        with cls._cache_lock:
            cached_rule = cls._cache_rule.get(cache_key, "__MISSING__")
        
        # 说明是第一次访问
        if cached_rule == "__MISSING__":
            if (im := self.get_list_by_name(functionName, user_id, user_roles, user_rights)).error:
                return im
            compiled_rule = self.compile_rules(im.data)
            
            with cls._cache_lock:
                cls._cache_rule[cache_key] = obj_to_dict(compiled_rule)
        else:
            # 从缓存中获取
            compiled_rule = dict_to_obj(cached_rule)
        
        return compiled_rule
    
    def get_list_by_name(self, functionName: str, user_id: int = -1, user_roles: List[str] = None, user_rights: List[str] = None) -> IM:
        """获取适用的规则列表
        
        Args:
            functionName: 函数名称
            user_id: 用户ID(-1表示未登录)
            user_roles: 用户角色列表
            user_rights: 用户权限列表
            
        Returns:
            IM: 操作结果(包含规则列表)
        """
        # 未登录用户
        if user_id == -1:
            return self.get_list_by_codes(functionName, ['anonymous'], 'user')

        # 已登录用户
        rules = []
        # 所有登陆用户
        if (im := self.get_list_by_codes(functionName, ['logined'], 'user')).error: 
            return im
        rules.extend(im.data)
        # 按角色、权限
        if user_roles:
            if (im := self.get_list_by_codes(functionName, user_roles, 'role')).error: 
                return im
            rules.extend(im.data)
        if user_rights:
            if (im := self.get_list_by_codes(functionName, user_rights, 'right')).error:
                return im
            rules.extend(im.data)

        return IM(True, '', rules)

    def get_list_by_codes(self, functionName: str, codes: List[str], ruleType: str = "role") -> IM:
        """ 根据编码列表和规则类型获取规则
        
        Args:
            functionName: 函数名称
            codes: 编码列表, ['A','B'] 能匹配上 ['C', 'D', 'B']， 只要匹配一个即可
            ruleType: 规则类型(role/right/user)
            
        Returns:
            List[Rule]: 规则列表
        """
        if not functionName or not codes:
            return IM(True, '', [])

        # 获取函数对应的API ID列表
        apiIds = bigo.ApiControl.inst().get_ids(functionName)
        if not apiIds:
            return IM(True, '', [])
        
        where = [{'apiId': ('in', apiIds)}, {'type': ruleType}, {'stop': False}]
        if (im := self.get_list(where=where)).error:
            return im
        
        if im.data is None or len(im.data) == 0:
            return IM(True, '', [])
        
        # 只要匹配一个即可
        rules = []
        for rule in im.data:
            if set(rule.codes.split(",")) & set(codes):
                rules.append(rule)
                
        return IM(True, '', rules)  
    

















    @classmethod
    def clear_cache(cls, clear_anonymous=False):
        """清除缓存（类方法）
        :param clear_anonymous: 是否清除匿名用户缓存
        """
        with cls._cache_lock:
            cls._compiled_rules_cache.clear()
            cls._cache_last_access_time.clear()
            if clear_anonymous:
                cls._anonymous_rules = None
                
    def check_access2(self, functionName: str, params: object = None, ip: str = "", 
        user_id: int = -1, user_roles: List[str] = None, user_rights: List[str] = None) -> IM:
        """检查是否允许访问
        
        Args:
            functionName: 函数名称
            params: 参数
            ip: 客户端IP(未登录用户使用)
            user_id: 用户ID(-1表示未登录)
            user_roles: 用户角色列表
            user_rights: 用户权限列表
            
        Returns:
            IM: 操作结果(包含是否允许访问及原因)
        """
        sup = super()
        
        def _do():
            
            im = IM()
            now = datetime.now()
            
            ip = get_ip()
                
            # 生成缓存键
            key = f"{functionName}[{user_id if user_id > 0 else ip}]"

            with self._cache_lock:
                # 获取上次访问时间 (默认为2000-01-01)\更新访问时间
                last_access_time = self._cache_last_access_time.get(key, datetime(2000, 1, 1))
                self._cache_last_access_time[key] = now

            # 获取适用的规则
            if (im := self.get_list_by_name(functionName, user_id, user_roles, user_rights)).error:
                return im
            rules = im.data
            
            # 如果没有设置规则，默认允许访问
            if not rules:
                return im

            # 1. 检查拒绝规则（存在即拒绝）
            deny_rules = [r for r in rules if not r.allow]
            if deny_rules:
                return im.set_error(f"访问被拒绝。原因: {deny_rules[0].desc or '无权限'}", 403)
            
            # 2. 剩余的都是允许规则，直接使用（无需排序）
            allow_rules = rules

            # 3. 检查频率限制（取允许规则中最严格的）
            frequency_rules = [r for r in allow_rules if r.frequency > 0]
            if frequency_rules:
                min_frequency = min(r.frequency for r in frequency_rules)
                elapsed_ms = (now - last_access_time).total_seconds() * 1000
                if elapsed_ms < min_frequency:
                    return im.set_error(f"访问频率过高。请等待{min_frequency - elapsed_ms}毫秒后再试。")

            # 4. 检查返回数量限制
            if not params:
                return im
            
            count_rules = [r for r in allow_rules if r.maxReturnCount > 0 and r.countParamName]
            if count_rules:
                strict_rule = min(count_rules, key=lambda x: x.maxReturnCount)
                request_count = to_int(get_attr(params, strict_rule.countParamName, 0))
                if request_count > strict_rule.maxReturnCount:
                    return im.set_error(f"单次请求最多返回{strict_rule.maxReturnCount}条数据。")

            return im
            
        return self.run(_do)

    def compile_rules2(self, rules):
        """编译规则，返回最小频率、最小数量限制和最终是否允许
        
        Args:
            rules (list): 规则列表
            
        return (object): 最小频率、最小数量限制和最终是否允许
        """
        if not rules:
            return None
            
        compiled_rule = dict_to_obj({
            'allow': True,
            'min_frequency': 0,
            'min_max_return': 0,
            'count_param_name': None,
            'deny_reason': ''
        })
        
        # 检查拒绝规则
        deny_rules = [r for r in rules if not r.allow]
        if deny_rules:
            compiled_rule.allow = False
            compiled_rule.deny_reason = deny_rules[0].desc or '无权限'
            return compiled_rule
        
        # 处理允许规则
        allow_rules = rules
        
        # 计算最小频率
        frequency_rules = [r for r in allow_rules if r.frequency > 0]
        if frequency_rules:
            compiled_rule.min_frequency = min(r.frequency for r in frequency_rules)
        
        # 计算最小返回数量限制
        count_rules = [r for r in allow_rules if r.maxReturnCount > 0 and r.countParamName]
        if count_rules:
            strict_rule = min(count_rules, key=lambda x: x.maxReturnCount)
            compiled_rule.min_max_return = strict_rule.maxReturnCount
            compiled_rule.count_param_name = strict_rule.countParamName
        
        return compiled_rule
    