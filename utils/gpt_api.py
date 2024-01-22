import os
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI,OpenAIError
from config import Config
class Chat_gpt():
    def __init__(self):


        self.api_key_list=[Config.openai_key]
        self.model = Config.openai_model

    def gpt_respond(self, question, sys_prompt=None,response_format="text"):
        if response_format not in ["text","json_object"]:
            raise ValueError("response_format错误")
        response_format = {"type": response_format}
        # os.environ["http_proxy"] = "http://127.0.0.1:10809"
        # os.environ["https_proxy"] = "http://127.0.0.1:10809"
        messages = [{"role": "system", "content": sys_prompt}]
        messages.append({"role": "user", "content": question})
        api_key_index = 0
        while True:
            api_key = self.api_key_list[api_key_index]
            try:
                os.environ["OPENAI_API_KEY"] = api_key
                client = OpenAI()
                chat_completion = client.chat.completions.create(model=self.model, messages=messages,
                response_format=response_format)
                unicode_str = chat_completion.choices[0].message.content
                return unicode_str
            except OpenAIError as e:
                print(e)
                api_key_index += 1
                if api_key_index == len(self.api_key_list):
                    return "当前Key池所有key都失效"
                # print("当前api_key{api_key}访问限制".format(api_key=api_key))

    def get_embedding(self,text):
        api_key_index = 0
        while True:
            api_key = self.api_key_list[api_key_index]
            try:
                os.environ["OPENAI_API_KEY"] = api_key
                client = OpenAI()
                response = client.embeddings.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                embedding = response.data[0].embedding
                return embedding
            except OpenAIError as e:
                # print("openai，报错:", e)
                api_key_index += 1
                if api_key_index == len(self.api_key_list):
                    break
                # print("当前api_key{api_key}访问限制".format(api_key=api_key))

    def answer_question(self,question , paragraphs , paragraph_embeddings , num_results=3): #参数分别是：问题，拆分文本 ，向量集 ， 寻找组数
        question_embedding = self.get_embedding(question) #获取对应向量
        similarity_scores = []
        for paragraph_embedding in paragraph_embeddings:
            # 使用余弦相似度计算问题和段落之间的相似性
            similarity_score = cosine_similarity([question_embedding], [paragraph_embedding])[0][0]
            similarity_scores.append(similarity_score)

        # 找到最相似的段落索引
        #most_similar_index = similarity_scores.index(max(similarity_scores))

        # 找到最相似的 num_results 个段落索引
        most_similar_indexes = sorted(range(len(similarity_scores)), key=lambda i: similarity_scores[i], reverse=True)[:num_results]
        similar_doc_list = [paragraphs[i] for i in most_similar_indexes]
        return similar_doc_list