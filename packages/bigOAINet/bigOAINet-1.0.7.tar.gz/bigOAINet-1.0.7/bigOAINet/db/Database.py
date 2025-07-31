import bigOAINet as bigo
import mxupy as mu 

@mu.singleton
def get_database():
    return mu.DatabaseHelper.init()

db, dh = get_database()

def get_inner_tables():
    """
    获取内部表
    """
    # 共 54 张表
    tables = [
        # 公用数据【5】
        bigo.KeyValue, bigo.ValueEx, bigo.Industry, bigo.Attachment, bigo.Card,
        # 地理数据【4】
        bigo.Country, bigo.Province, bigo.City, bigo.County,
        # 安全【2】
        bigo.Api, bigo.Rule,
        # 企业部门【4】
        bigo.Enterprise, bigo.EnterpriseUser, bigo.DepartmentType, bigo.Department,
        # 用户【4】
        bigo.User, bigo.UserBind, bigo.UserNoBind, bigo.Login,
        # 部门 【3】
        bigo.DepartmentUser, bigo.DepartmentManager, bigo.DepartmentAndSubject,
        # 会员相关 【11】
        bigo.Duty, bigo.DutyUser, bigo.Muster, bigo.MusterDepartment, bigo.ProRank, bigo.ProRankUser,
        bigo.Group, bigo.GroupUser, bigo.FriendGroup, bigo.Friend,
        bigo.Invitation,
        # 注册表与日志【4】
        bigo.RegistryCategory, bigo.RegistryItem, bigo.LogCategory, bigo.Log,
        # 权限相关【9】
        bigo.RightCategory, bigo.Right, bigo.RightAndData,
        bigo.RoleCategory, bigo.Role, bigo.RoleAndSubject,
        bigo.RoleAndRight, bigo.RoleExclusive, bigo.RoleInherit,
        # 智能体【4】
        bigo.AgentCatalog, bigo.Agent, bigo.KB, bigo.AgentUser,
        # 聊天【4】
        bigo.Room, bigo.Session, bigo.Chat, bigo.RoomUser,
    ]
    return tables

@mu.singleton
def create_inner_tables():
    """
    创建内部表
    """
    im = mu.IM()
    
    tables = get_inner_tables()
    # 创建所有的表
    for table in tables:
        control_class_name = table.__name__ + "Control"
        control_class = getattr(bigo, control_class_name)
        im = control_class.inst().create_table()
        if im.error:
            print(im.msg)
            return im
        else:
            print(f"表 {table.__name__} 创建成功")
            
    return im
    
@mu.singleton
def drop_inner_tables():
    """
    删除内部表【慎用】
    """
    im = mu.IM()
    
    tables = get_inner_tables()[::-1]
    # 创建所有的表
    for table in tables:
        control_class_name = table.__name__ + "Control"
        control_class = getattr(bigo, control_class_name)
        im = control_class.inst().drop_table()
        if im.error:
            print(im.msg)
            return im
        else:
            print(f"表 {table.__name__} 删除成功")
            
    return im
    
@mu.singleton
def init_inner_data():
    """
    初始化内部数据
    注册表、安全、用户
    """
    im = mu.IM()
    
    # 初始化配置
    name_paths = []
    cfss = []
    # 配置服务器
    name_path = 'bigo/apiServer'
    cfs = [
        {
            "key": "host",
            "value": "0.0.0.0",
            "type": "string",
            "desc": "服务监听地址"
        },
        {
            "key": "port",
            "value": 8089,
            "type": "int",
            "desc": "服务监听端口"
        },
        {
            "key": "ssl_certfile",
            "value": "",
            "type": "string",
            "desc": "SSL证书文件路径"
        },
        {
            "key": "ssl_keyfile",
            "value": "",
            "type": "string",
            "desc": "SSL密钥文件路径"
        },
        {
            "key": "allow_credentials",
            "value": True,
            "type": "bool",
            "desc": "是否允许跨域凭据"
        },
        {
            "key": "allow_origins",
            "value": ["*"],
            "type": "list",
            "desc": "允许的跨域来源"
        },
        {
            "key": "allow_methods",
            "value": ["*"],
            "type": "list",
            "desc": "允许的HTTP方法"
        },
        {
            "key": "allow_headers",
            "value": ["*"],
            "type": "list",
            "desc": "允许的HTTP头部"
        },
        {
            "key": "debug",
            "value": True,
            "type": "bool",
            "desc": "调试模式开关"
        },
        {
            "key": "user_file_path",
            "value": "F://T",
            "type": "string",
            "desc": "用户文件存储路径"
        },
        {
            "key": "sys_file_path",
            "value": "F://T",
            "type": "string",
            "desc": "系统文件存储路径"
        },
        {
            "key": "web_file_path",
            "value": "",
            "type": "string",
            "desc": "Web文件存储路径"
        },
        {
            "key": "upload_file_size",
            "value": '{"image":3072, "audio":10240, "video":1024000}',
            "type": "dict",
            "desc": "上传文件大小限制(KB)"
        },
        {
            "key": "can_access_file_exts",
            "value": ['image','text'],
            "type": "list",
            "desc": "允许访问的文件扩展名"
        },
        {
            "key": "can_access_file_types",
            "value": ["*"],
            "type": "list",
            "desc": "允许访问的文件类型"
        },
        {
            "key": "access_file_max_age",
            "value": 31536000,
            "type": "int",
            "desc": "文件访问缓存最大年龄(秒)"
        }
    ]
    name_paths.append(name_path)
    cfss.append(cfs)
    
    name_path = 'bigo/apiServer/accessToken'
    cfs = [
        {
            "key": "expire_seconds",
            "value": 86400,
            "type": "int",
            "desc": "访问令牌过期时间（秒）"
        },
        {
            "key": "secret",
            "value": "fy,brysj198",
            "type": "string",
            "desc": "JWT签名密钥"
        },
        {
            "key": "algorithm",
            "value": "HS256",
            "type": "string",
            "desc": "JWT签名算法"
        },
        {
            "key": "issuer",
            "value": "bigoainet.com",
            "type": "string",
            "desc": "令牌签发者"
        },
        {
            "key": "audiences",
            "value": ["bigoainet.com", "bigoainet2.com"],
            "type": "list",
            "desc": "允许访问的域名列表"
        },
        {
            "key": "cache_max_size",
            "value": 1000,
            "type": "int",
            "desc": "令牌缓存最大数量"
        },
        {
            "key": "cache_ttl",
            "value": 86400,
            "type": "int",
            "desc": "令牌缓存有效期（秒）"
        }
    ]
    name_paths.append(name_path)
    cfss.append(cfs)
    
    name_path = 'bigo/apiServer/member/user'
    cfs = [
        {
            "key": "login_fail_max_count",
            "value": 6,
            "type": "int",
            "desc": "登录失败最大次数"
        },
        {
            "key": "cache_max_size",
            "value": 1000,
            "type": "int",
            "desc": "登录缓存最大数量"
        },
        {
            "key": "cache_ttl",
            "value": 600,
            "type": "int",
            "desc": "登录缓存有效期（秒）"
        }
    ]
    
    name_paths.append(name_path)
    cfss.append(cfs)
    
    # 批量添加/更新配置项
    for name_path, cfs in zip(name_paths, cfss):
        for config in cfs:
            config = mu.dict_to_obj(config)
            im = bigo.RegistryItemControl.inst().add_or_update_item(
                name_path=name_path,
                key=config.key,
                value=config.value,
                item_type=config.type,
                desc=config.desc,
                mode='overwrite'
            )
            
            if im.error:
                print(f"配置项 {config.key} 更新失败: {im.msg}")
                return im
            else:
                print(f"配置项 {config.key} 更新成功")

    # # 安全
    # if (im := bigo.ApiControl.inst().add_api('bigo', 'bigOAINet', '*', 1, 'bigo')).error:
    #     print(f"添加 API 失败: {im.msg}")
    #     return im
    # print(f"添加 API 成功 bigOAINet")
    
    # apiId = im.data.apiId
    # if (im := bigo.RuleControl.inst().add_rule(apiId, 'user', 'logined', 1, True, False, 10, 'limit', 1000, '登录才能调用bigo')).error:
    #     print(f"添加规则失败: {im.msg}")
    #     return im
    # print(f"添加规则成功 bigOAINet")
    
    # if (im := bigo.ApiControl.inst().add_api('bigo add,delete,update', 'bigOAINet', 'add,delete,update', 1, 'bigo 增、删、改')).error:
    #     print(f"添加 API 失败: {im.msg}")
    #     return im
    # print(f"添加 API 成功, bigOAINet 增、删、改相关接口")

    
    # apiId = im.data.apiId
    # if (im := bigo.RuleControl.inst().add_rule(apiId, 'user', 'anonymous,logined', 100, False, False, 10, 'limit', 1000, '普通用户不能调用 bigo 增、删、改')).error:
    #     print(f"添加规则失败: {im.msg}")
    #     return im
    # print(f"添加规则成功, bigOAINet 增、删、改相关接口")
    
    # if (im := bigo.ApiControl.inst().add_api('bigo safe', 'bigOAINet.db.safe', 'safe', 1, 'bigo 安全')).error:
    #     print(f"添加 API 失败: {im.msg}")
    #     return im
    # print(f"添加 API 成功, bigo 安全相关接口")

    
    # apiId = im.data.apiId
    # if (im := bigo.RuleControl.inst().add_rule(apiId, 'user', 'anonymous,logined', 1000, False, False, 10, 'limit', 1000, '普通用户不能调用 bigo 安全相关接口')).error:
    #     print(f"添加规则失败: {im.msg}")
    #     return im
    # print(f"添加规则成功, bigo 安全相关接口")

    
    # if (im := bigo.ApiControl.inst().add_api('bigo member', 'bigOAINet.db.member', 'member', 1, 'bigo 会员')).error:
    #     print(f"添加 API 失败: {im.msg}")
    #     return im
    # print(f"添加 API 成功, bigo 会员相关接口")
    
    # apiId = im.data.apiId
    # if (im := bigo.RuleControl.inst().add_rule(apiId, 'user', 'anonymous,logined', 1000, False, False, 10, 'limit', 1000, '普通用户不能调用 bigo 会员相关接口')).error:
    #     print(f"添加规则失败: {im.msg}")
    #     return im
    # print(f"添加规则成功, bigo 会员相关接口")
    
    # 定义API和规则的配置列表
    api_configs = [
        {
            'name': 'bigo',
            'space': 'bigOAINet',
            'codes': '*',
            'sort': 1,
            'desc': 'bigo',
            'rules': [
                {
                    'type': 'user',
                    'codes': 'logined',
                    'level': 1,
                    'allow': True,
                    'stop': False,
                    'maxReturnCount': 10,
                    'countParamName': 'limit',
                    'frequency': 1000,
                    'desc': '登录才能调用 bigo'
                }
            ]
        },
        {
            'name': 'bigo add,delete,update',
            'space': 'bigOAINet',
            'codes': 'add,delete,update',
            'sort': 1,
            'desc': 'bigo 增、删、改',
            'rules': [
                {
                    'type': 'user',
                    'codes': 'anonymous,logined',
                    'level': 100,
                    'allow': False,
                    'stop': False,
                    'maxReturnCount': 10,
                    'countParamName': 'limit',
                    'frequency': 1000,
                    'desc': '普通用户不能调用 bigo 增、删、改'
                }
            ]
        },
        {
            'name': 'bigo safe',
            'space': 'bigOAINet.db.safe',
            'codes': 'safe',
            'sort': 1,
            'desc': 'bigo 安全',
            'rules': [
                {
                    'type': 'user',
                    'codes': 'anonymous,logined',
                    'level': 1000,
                    'allow': False,
                    'stop': False,
                    'maxReturnCount': 10,
                    'countParamName': 'limit',
                    'frequency': 1000,
                    'desc': '普通用户不能调用 bigo 安全相关接口'
                }
            ]
        },
        {
            'name': 'bigo member',
            'space': 'bigOAINet.db.member',
            'codes': 'member',
            'sort': 1,
            'desc': 'bigo 会员',
            'rules': [
                {
                    'type': 'user',
                    'codes': 'anonymous,logined',
                    'level': 1000,
                    'allow': False,
                    'stop': False,
                    'maxReturnCount': 10,
                    'countParamName': 'limit',
                    'frequency': 1000,
                    'desc': '普通用户不能调用 bigo 会员相关接口'
                }
            ]
        }
    ]

    # 遍历配置并添加API和规则
    for api_config in api_configs:
        # 将字典转换为对象
        api_config = mu.dict_to_obj(api_config)
        
        # 添加API（通过对象属性访问）
        if (im := bigo.ApiControl.inst().add_api(
            name=api_config.name,
            space=api_config.space,
            codes=api_config.codes,
            sort=api_config.sort,
            desc=api_config.desc
        )).error:
            print(f"添加 API 失败: {im.msg}")
            return im
        print(f"添加 API 成功, {api_config.desc}")
        
        api_id = im.data.apiId
        
        # 添加规则（如果存在规则）
        for rule_config in getattr(api_config, 'rules', []):
            rule_config = mu.dict_to_obj(rule_config)
            if (im := bigo.RuleControl.inst().add_rule(
                apiId=api_id,
                type=rule_config.type,
                codes=rule_config.codes,
                level=rule_config.level,
                allow=rule_config.allow,
                stop=rule_config.stop,
                maxReturnCount=rule_config.maxReturnCount,
                countParamName=rule_config.countParamName,
                frequency=rule_config.frequency,
                desc=rule_config.desc
            )).error:
                print(f"添加规则失败: {im.msg}")
                return im
            print(f"添加规则成功: {rule_config.desc}")

    
    # 用户
    if (im := bigo.UserControl.inst().register('admin', 'admin', 'Fy12#$%^')).error:
        print(f"注册用户失败: {im.msg}")
        return im
    print(f"注册用户成功, admin of bigo")

    
    return im

if __name__ == "__main__":
    if (im := create_inner_tables()).error:
        print(f"创建内部表失败: {im.msg}")
        exit(1)
    
    if (im := init_inner_data()).error:
        print(f"初始化内部数据失败: {im.msg}")
        exit(1)
    
    
        
