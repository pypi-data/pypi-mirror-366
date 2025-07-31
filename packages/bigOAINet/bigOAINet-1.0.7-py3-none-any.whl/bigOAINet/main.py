import asyncio
import bigOAINet as bigo

from mxupy import ApiServer, AccessToken

chatServer = None

async def startup_event():
    global chatServer
    print("HI, I am BigOAI!\nLong time no see.")
    # 必须在unicorn.run之后执行
    chatServer = bigo.ChatServer()
    asyncio.create_task(chatServer.run())


async def shutdown_event():
    print("ApiServer: bye bye!")
    chatServer.stop()


def go():
    
    apiServerConfig = None
    accessTokenConfig = None
    userConfig = None
    
    name_paths = ['bigo/apiServer', 'bigo/apiServer/accessToken', 'bigo/apiServer/member/user']
    for name_path in name_paths:
        im = bigo.RegistryItemControl.inst().get_as_dict(name_path)
        if im.error:
            print(f"获取配置项 {name_path} 失败: {im.msg}")
            return
        config = im.data
        
        if name_path == 'bigo/apiServer':
            apiServerConfig = config
        elif name_path == 'bigo/apiServer/accessToken':
            accessTokenConfig = config
        elif name_path == 'bigo/apiServer/member/user':
            userConfig = config
    
    # 注入配置信息 并启动
    bigo.UserControl.inst().init_cache(userConfig)
    AccessToken(accessTokenConfig)
    ApiServer(apiServerConfig).run(startup_event, shutdown_event)
