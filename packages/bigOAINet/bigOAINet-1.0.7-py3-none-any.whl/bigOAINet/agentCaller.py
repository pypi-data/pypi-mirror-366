import requests
import time
import json
from mxupy import read_config
import bigOAINet as bigo

# dify 调用
class AgentCaller:
    '''
        智能体调用
    '''
    def __init__(self, agentId, userId, sessionId):

        self.url = read_config().get('dify_api_url', {})
        self.agentId = agentId
        self.agent = bigo.AgentControl.inst().get_one_by_id(agentId).data
        self.userId = userId
        self.sessionId = sessionId
        # self.conversationId = conversationId
        self.headers = {
            'Authorization': f'Bearer { self.agent.apiKey }',
            'Content-Type': 'application/json'
        }

    def call(self, msg):
        """ 调用智能体

        Args:
            msg (_type_): 消息
                input: 输入
                query: 问题
                files: 文件
                userId: 用户id
        Returns:
            requests.models.Response: 
        """

        # file 数据结构
        # {
        #     'type': 'image',
        #     'transfer_method': 'remote_url',
        #     'url': 'https://cloud.dify.ai/logo/logo-site.png'
        # }
        
        payload = json.dumps({
            'inputs': msg.get('input', {}),
            'query': msg.get('query', ''),
            'response_mode': 'streaming',
            'conversation_id': msg.get('conversationId', ''),
            'user': str(self.userId),
            'files': msg.get('files', [])
        })
        # response = requests.request('POST', self.url + 'chat-messages', headers=self.headers, data=payload)
        # return response
        
        
        
        # def mock_response(data):
        #     class MockResponse:
        #         def iter_lines(self, decode_unicode=True):
        #             for line in data:
        #                 if decode_unicode:
        #                     # 确保 line 是字节串类型
        #                     if isinstance(line, bytes):
        #                         yield line
        #                     else:
        #                         yield line
        #                 else:
        #                     yield line

        #     return MockResponse()

        # def stream_data():
        #     """生成器，模拟从服务器接收数据"""
        #     for i in range(5):
        #         # 模拟从网络接收到的字节串数据
        #         yield f"Line {i}\n".encode('utf-8')
        #         time.sleep(0.1)  # 模拟网络延迟

        # # 使用模拟的响应对象
        # mock_response_obj = mock_response(stream_data())
        
        def mock_response(data):
            """模拟 requests.Response 对象，具有 iter_lines 方法"""
            class MockResponse:
                def iter_lines(self, decode_unicode=True):
                    for line in data:
                        if decode_unicode:
                            # 确保 line 是字节串类型
                            if isinstance(line, bytes):
                                yield line
                            else:
                                yield line
                        else:
                            yield line

            return MockResponse()

        def stream_data():
            """生成器，模拟从服务器接收数据"""
            
            message_start = 'data: {"event": "message", "answer": "<think>", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_start
            message_content = 'data: {"event": "message", "answer": "让我深受触动。", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "书中孙少安和", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "孙少平两兄弟", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "在艰难环境中", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "拼搏奋斗，他们", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "的坚韧不拔和对", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "生活的热爱", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "让我明白，平凡的人生也能绽放光芒。", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "无论身处何种境地，只要心怀希望，", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "努力前行，就能在自己的世", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "界里书写不平凡的篇章。", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_start = 'data: {"event": "message", "answer": "</think>", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_start
            
            message_content = 'data: {"event": "message", "answer": "《平凡的世界》", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "让我深受触动。", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "书中孙少安和", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "孙少平两兄弟", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "在艰难环境中", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "拼搏奋斗，他们", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "的坚韧不拔和对", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "生活的热爱", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "让我明白，平凡的人生也能绽放光芒。", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "无论身处何种境地，只要心怀希望，", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "努力前行，就能在自己的世", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            message_content = 'data: {"event": "message", "answer": "界里书写不平凡的篇章。", "conversation_id":"888888"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_content
            
            message_end = 'data: {"event": "message_end"}\n'.encode('utf-8')
            time.sleep(0.1)
            yield message_end
            

        # 使用模拟的响应对象
        mock_response_obj = mock_response(stream_data())
    
        return mock_response_obj
    

    def upload(self):
        # url = self.url + "/files/upload"

        # payload = {}
        # files = [('file', ('file', open('/path/to/file', 'rb'), 'application/octet-stream'))]
        # headers = {
        #     'Authorization': 'Bearer {self.agent.apiKey}'
        # }

        # response = requests.request("POST", url, headers=headers, data=payload, files=files)

        # # print(response.text)
        # return response
        pass
