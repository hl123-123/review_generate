from utils import Chat_gpt
import json
def get_search_keywords(paper_title,language="English"):
    '''
    输入论文主题生成一些相关的检索关键词，便于相关文献检索调研
    :param paper_title: 论文标题
    :param language: 输出的关键词语言，默认英语
    :return: 返回一个list,list中每个元素都是一个检索关键词
    '''
    chat_gpt = Chat_gpt()
    sys_prompt = """
你是一个专业的学者，很擅长基于一个论文主题进行相应的文献检索。
我需要请你帮我基于一篇论文题目进行相应的文献调研检索，你需要以json字典的格式输出相关的检索关键词,字典的key是"keywords",value是一个list，list每个元素都是相应的检索关键词.
请你保证这个list中的所有检索关键词不存在语义高度重合的，去除一些语义高度重复的关键词，以便提供更为精准和多样的检索选项。

输出格式：
{"keywords":["keyword1"，"keywords2"]}
"""
    query_prompt = f"""论文题目：{paper_title}
    无论前面输入的语言是什么，请你用{language}输出对应的检索关键词。
    """
    keywords_dict_str = chat_gpt.gpt_respond(query_prompt,sys_prompt,"json_object")
    keywords_list = json.loads(keywords_dict_str)["keywords"]
    return keywords_list

if __name__=="__main__":
    keywords_list= get_search_keywords("面向城市治理的政务文本挖掘与分类研究")
    print(keywords_list)