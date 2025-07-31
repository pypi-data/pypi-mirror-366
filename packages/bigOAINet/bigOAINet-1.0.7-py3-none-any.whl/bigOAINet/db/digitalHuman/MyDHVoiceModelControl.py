import uuid
import requests
import mxupy as mu
import bigOAINet as bigo

from peewee import *
from mxupy import IM, accesstoken_user_id, get_attr


class MyDHVoiceModelControl(mu.EntityXControl):

    class Meta:
        model_class = bigo.MyDHVoiceModel
        
    def __init__(self, *args, **kwargs):
        self.sub_dir = 'digitalHuman/voiceModel/'
        super().__init__(*args, **kwargs)
        
    def split_string_by_length(self, src, chunk_length):
        return [src[i:i+chunk_length] for i in range(0, len(src), chunk_length)]
    
    

    def merge_wav_files(self, output_path, input_paths):
        import wave
        # 打开第一个 WAV 文件以获取参数
        with wave.open(input_paths[0], 'rb') as first_wav:
            params = first_wav.getparams()
            n_channels = first_wav.getnchannels()
            samp_width = first_wav.getsampwidth()
            frame_rate = first_wav.getframerate()

        # 创建一个新的 WAV 文件用于写入
        with wave.open(output_path, 'wb') as output_wav:
            output_wav.setparams(params)

            # 遍历所有输入的 WAV 文件并写入到输出文件中
            for path in input_paths:
                with wave.open(path, 'rb') as input_wav:
                    # 检查参数是否一致
                    if input_wav.getnchannels() != n_channels or input_wav.getsampwidth() != samp_width or input_wav.getframerate() != frame_rate:
                        print(f"警告：文件 '{path}' 的参数与第一个文件不一致，可能无法正确拼合。")
                    # 写入帧数据
                    output_wav.writeframes(input_wav.readframes(input_wav.getnframes()))

        print(f"拼合完成，输出文件已保存到 '{output_path}'。")

    # # 示例用法
    # input_files = ['file1.wav', 'file2.wav', 'file3.wav']  # 替换为你的 WAV 文件路径
    # output_file = 'merged_output.wav'  # 拼合后的输出文件路径
    # merge_wav_files(output_file, input_files)
        
    @accesstoken_user_id
    def train_my_voicemodel(self, model, text, accessToken = None, user_id = -1):
        """ 生成视频

        Args:
            code (str): 任务唯一码，可用于查询任务进度。
            model (MyDHVoiceModel): 语音模型。
            text (str): 语音文本。
            accessToken (str):访问令牌。
            sub_dir (str): 服务器子目录。
        Returns:
            IM: 响应结果
        """
        # 第一步：检查用户权限
        if (im := self.get_one_by_id(model.myDHVoiceModelId, select=['userId'])).error:
            return im
        if user_id != im.data.userId:
            return IM.set_error('无权操作。')
        
        # 第二步：读取配置信息
        spark_tts_server = mu.read_config().get('spark_tts', {})

        # 域名、端口、文件上传端口、功能函数
        host = spark_tts_server.get('host', '0.0.0.0')
        port = int(spark_tts_server.get('port', '7861'))
        file_port = int(spark_tts_server.get('file_port', '8089'))
        function = spark_tts_server.get('function', 'voice_clone')
        # 服务端子目录
        server_input_sub_dir = spark_tts_server.get('server_input_sub_dir', 'Spark-TTS/src/voice/')
        server_result_sub_dir = spark_tts_server.get('server_result_sub_dir', 'Spark-TTS/example/results')
        server_input_relative_sub_dir = spark_tts_server.get('server_input_relative_sub_dir', 'src/voice/')
      
        file_upload_url = f'http://{host}:{file_port}/file'
        # 本地目录
        # user_path = mu.file_dir('user', model.userId, sub_dir=self.sub_dir)
        
        parent_file_dir = mu.file_dir('user', model.userId)
        voiceModel_file_dir = parent_file_dir + self.sub_dir
        voice_file_dir = parent_file_dir + bigo.MyDHVoiceControl.inst().sub_dir
        
        # 第三步：上传语音文件到服务器
        im = mu.upload_file_to_server(url=file_upload_url, file_path=voiceModel_file_dir + model.referUrl, 
                                   user_id=model.userId, access_token=accessToken, sub_dir=server_input_sub_dir, override=True, keep=False)
        if im.error:
            return im
        voice_server_url = server_input_relative_sub_dir + mu.dict_to_obj(im.data).filename
        
        vs = []
        # 如果文字过多，目前tts生成有问题，现将文字截断为150个字，大约30秒
        chunks = self.split_string_by_length(text, 150)
        for chunk in chunks:
            im = self.gen_tts(chunk, model.text, host, port, file_port, function, server_result_sub_dir, voice_file_dir, voice_server_url)
            if im.error:
                return im
            vs.append(im.data)
        
        filename = ''
        if len(vs) == 1:
            filename = vs[0].split('/')[-1]
        else:
            # 合并
            filename = str(uuid.uuid4()) + '.wav'
            self.merge_wav_files(voice_file_dir + filename, vs)
        
        # 获取音频时长
        import moviepy as mpy
        voice_path = voice_file_dir + filename
        audio = mpy.AudioFileClip(voice_path)
        audio_duration = audio.duration
        
        # 第六步：入库
        im = bigo.MyDHVoiceControl.inst().add({
            'userId': model.userId,
            'name': model.name,
            'url': filename,
            'text': text,
            'duration': audio_duration,
            'myDHVoiceModelId': model.myDHVoiceModelId,
        })
        if im.error:
            return im
        
        return im
    
    def gen_tts(self, text, prompt_text, host, port, file_port, function, server_result_sub_dir, voice_file_dir, voice_server_url):
       
        
        # 第四步：调用远程接口，执行生成动作
        url = f"http://{host}:{port}/{function}"
        data = {
            'text': text,
            'prompt_text': prompt_text,
            'prompt_wav_upload': '',
            'prompt_wav_record': voice_server_url
        }
        im = mu.remote_call(lambda: requests.post(url, data=data))
        if im.error:
            return im
        filename = im.data.split('\\')[-1].replace('"', '')
        
        # http://192.168.2.19:8089/file?filename=20250415172029.wav&sub_dir=example/results&type=user&download=true
        # 第五步：下载
        url = f"http://{host}:{file_port}/file?filename={filename}&sub_dir={server_result_sub_dir}&type=user&download=true"
        im = mu.download_file_from_server(url, voice_file_dir + filename)
        if im.error:
            return im
        
        return im
        
    @accesstoken_user_id
    def get_my_voicemodel_list(self, user_id = -1, select=None, where = None, order_by=None, group_by=None, having=None, limit=None, offset=None, 

                 to_dict=False, recurse=False, backrefs=False, extra_attrs=None, max_depth=1):
        """ 获取我的语音模型列表

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
    def delete_my_voicemodel(self, id, recursive=True, user_id = -1):
        """ 删除我的语音模型

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
                return im.set_error('删除失败。语音模型不存在。')
            if im.data.userId != user_id:
                return im.set_error('删除失败。您没有权限删除此语音模型。')
            
            if (im := self.delete_by_id(id, recursive)).error: 
                return im
            
            return im

        return self.run(_do)
    
    @accesstoken_user_id
    def add_or_update_my_voicemodel(self, model, fields= ['name', 'referUrl', 'text'], user_id = -1):

        """ 
        新增或更新我的语音模型

        Args:
            model (dict): 模型数据
            fields (list): 更新字段
            user_id (int): 用户id
            
        Returns:
            IM: 删除结果
        """
        def _do():
            
            im = IM()
            
            id = get_attr(model, 'myDHVoiceModelId', -1)
            if id > 0:
                if (im := self.get_one_by_id(id, select='userId')).error: 
                    return im
                if not im.data:
                    return im.set_error('更新失败。语音模型不存在。')
                if im.data.userId != user_id:
                    return im.set_error('更新失败。您没有权限更新此语音模型。')
            
            model.userId = user_id
            if (im := self.add_or_update(model, fields)).error:
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
            
            cs = [{'myDHVoiceModelId': id}, {'userId': userId}]
            
            # 获取视频模型
            im = self.get_one(where=cs)
            if im.error:
                return im
            voiceModel = im.data
            
            # 视频是否引用了这个语音模型
            im = bigo.MyDHVideoControl.inst().exists(where=cs)
            if im.error:
                return im
            if im.data:
                return IM(False, '删除失败。已有视频选中了此语音模型。')
            
            # 名片是否引用了这个语音模型
            im = bigo.MyDHCardModelControl.inst().exists(where=cs)
            if im.error:
                return im
            if im.data:
                return IM(False, '删除失败。已有名片选中了此语音模型。')

            # 删除
            im = self.delete_by_id(id)
            if im.error:
                return im
            
            # filePathList = [voiceModel.trainFile]
            # if mu.isNN(voiceModel.previewFile):
            #     filePathList.append(voiceModel.previewFile)
                
            # # 删除文件
            # filePathListSet = list(set(filePathList))
            # mu.removeFileList(filePathListSet, mu.file_dir('user', userId) + '\\' )

            return im

        return self.run(_do)