import numpy as np
import mxupy as mu

class TextSimilarityProcessor(mu.ApiControl):
    """
        空间: bigOAINet.tools.TextSimilarityProcessor.TextSimilarityProcessor
        名称：文本相似度处理器
    """
    word2VecModel = None
    question_vectors = {}
    
    def __init__(self):
        
        # 读取配置信息
        heygem_ai_server = mu.read_config().get('text_similarity_processor', {})
        # 模型路径
        self.pretrained_model_path = heygem_ai_server.get('pretrained_model_path', 'nlp_starter/light_Tencent_AILab_ChineseEmbedding.bin')
    
    def preprocess_sentence(self, sentence):
        """
            使用 jieba 进行分词
            对句子进行预处理，将句子分词并转换为列表形式。

        Args:
            self: 类实例本身。
            sentence (str): 待处理的句子。

        Returns:
            list: 分词后的单词列表。
        """
        import jieba
        return list(jieba.cut(sentence))
    
    def sentence_to_vector(self, sentence, model):
        """
            将句子转换为向量表示。

        Args:
            self: 类实例本身。
            sentence (str): 待转换的句子。
            model: 用于获取词向量的模型。

        Returns:
            numpy.ndarray: 句子的向量表示。如果句子中没有词在模型中，则返回全零向量。
        """
        words = self.preprocess_sentence(sentence)
        vectors = [model[word] for word in words if word in model]
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return np.zeros(model.vector_size)

    def cosine_similarity(self, vec1, vec2):
        """
            计算两个向量之间的余弦相似度。

        Args:
            self: 类实例本身。
            vec1 (numpy.ndarray): 第一个向量。
            vec2 (numpy.ndarray): 第二个向量。

        Returns:
            float: 两个向量之间的余弦相似度，取值范围为 [-1, 1]。值越接近 1，表示向量越相似。
        """
        from scipy.spatial.distance import cosine
        return 1 - cosine(vec1, vec2)
    
    def find_most_similar_question(self, question, qs):
        """
            查找与给定问题最相似的问题及其相似度。

        Args:
            self: 类实例本身。
            question (str): 用户输入的问题。
            qs (list[str]): 问答集中的问题列表。

        Returns:
            tuple: 包含最相似问题和最高相似度的元组。
                most_similar_question (str): 与用户问题最相似的问题。
                highest_similarity (float): 最高相似度，取值范围为 [-1, 1]。值越接近 1，表示问题越相似。

        Raises:
            ValueError: 如果问答集为空。
        """
        from gensim.models import KeyedVectors
        # 加载预训练的词向量模型, 只加载一次, 避免重复加载, 加载时比较慢
        if TextSimilarityProcessor.word2VecModel is None:
            TextSimilarityProcessor.word2VecModel = KeyedVectors.load_word2vec_format(self.pretrained_model_path, binary=True)
        
        # 将问答集中的问题转换为向量
        vs = None   
        if str(qs) in TextSimilarityProcessor.question_vectors:
            vs = TextSimilarityProcessor.question_vectors[str(qs)]
        else:
            vs = [self.sentence_to_vector(q, TextSimilarityProcessor.word2VecModel) for q in qs]
            TextSimilarityProcessor.question_vectors[str(qs)] = vs
            
        # 将用户问题和问答集中的问题转换为向量
        user_question_vector = self.sentence_to_vector(question, TextSimilarityProcessor.word2VecModel)
        # 计算相似度
        similarities = [self.cosine_similarity(user_question_vector, vec) for vec in vs]
        # 获取相似度最高的问题
        most_similar_index = np.argmax(similarities)
        most_similar_question = qs[most_similar_index]
        highest_similarity = similarities[most_similar_index]
        
        return most_similar_question, highest_similarity
