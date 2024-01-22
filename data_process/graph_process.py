#encoding=utf-8
import copy
from config import Config
import os
import json
from collections import defaultdict
from utils import Chat_gpt
from datetime import datetime
def get_search_query_list():
    pdf_info_json_path = os.path.join(Config.project_path,Config.pdf_info_json_path)
    with open(pdf_info_json_path,"r",encoding="utf-8") as f:
        pdf_info_json = json.load(fp=f)

    # print(pdf_info_json)
    search_query_list = list(set([i["search_query"] for i in pdf_info_json]))
    return search_query_list

def paper_classification(paper_info,classify_list):
    chat_gpt = Chat_gpt()
    sys_prompt = """
你是一个专业的学者，很擅长给一篇论文进行分类。
我会给你该篇论文的有关信息，同时告诉你该篇论文可能属于的全部类别，需要请你帮我对于这篇论文进行分类（如果我给你的论文你觉得严重不属于我给你的任何一个类别，请你自行生成一个对应的类别），你需要以json字典的格式输出对应的分类结果,字典的key是"class",value是这篇文章的类别。

输出格式：
{"class":value}
"""
    if isinstance(paper_info,dict):
        paper_info1 = {}
        paper_info1["title"] = paper_info["title"]
        paper_info1["summary"] = paper_info["summary"]
        paper_info_str = json.dumps(paper_info1,indent=4)
    elif isinstance(paper_info,str):
        paper_info_str = paper_info

    if isinstance(classify_list,list):
        classify_list_str = json.dumps(classify_list)
    elif isinstance(classify_list,str):
        classify_list_str = json.dumps(classify_list)

    query_prompt = f"""论文信息：{paper_info_str}

全部类别：{classify_list_str}
    """
    keywords_dict_str = chat_gpt.gpt_respond(query_prompt,sys_prompt,"json_object")
    classify = json.loads(keywords_dict_str)["class"]
    return classify


def summary_one_class_papers(query,paper_info_list,topic_name=None,language="Chinese"):
    chat_gpt = Chat_gpt()
    if isinstance(paper_info_list, list):
        paper_info_list1= []
        for paper_info in paper_info_list:
            paper_info1 = {}
            paper_info1["title"]=paper_info["title"]
            paper_info1["summary"]=paper_info["summary"]
            paper_info1["authors"] = paper_info["authors"]

            paper_info_list1.append(paper_info1)

        paper_info_list_str = json.dumps(paper_info_list1, indent=4)
    elif isinstance(paper_info_list, str):
        paper_info_list_str = paper_info_list
    if topic_name:
        sys_prompt = f"""
        你是一个专业的学者，很擅长基于某个核心主题给某个相关领域的论文进行归纳性总结，作为该主题综述的一个子章节，同时在总结的内容中以[1]索引的形式插入论文引用索引。
        我会告诉你检索关键词query，同时给你使用该query检索得到的一些论文信息，需要你以<<{topic_name}>>为综述中心方向，将这些论文的内容进行汇总梳理，基于这些论文信息汇总成该综述的一个子章节，总结内容以json的格式返回，要求包含该子章节的标题和内容，key是"subchapter heading"和"subchapter content",value是对应的内容。

        参考句式（请把参考句式中 学者A,学者B等 替换成具体引用论文的具体作者）：
        ```
        学者A 和学者 B，从......的角度......的差异进行研究，得出了......的必要性。
        学者 C在......年对......问题进行了研究，他认为......可以实现......提高。
学者D建议......中，化解因为......造成的.......。
学者E在......的角度对......进行了研究。他在研究中阐述了目前......和......两个方面的争论，一是......,二是......，在他看来这些争论表明了现在......展现一个......的趋势。
        ```
        要求：输出的json只有单层结构，不存在dict嵌套。
        输出格式：
        {{"subchapter heading":"content1","subchapter content":"content2"}}
        """
    else:
        sys_prompt = """
        你是一个专业的学者，很擅长给同一个领域的论文进行总结，同时在总结的内容中以[1]的形式插入论文引用索引。
        我会告诉你检索关键词query，同时给你同一个领域的一些论文（使用相同的query检索得到的论文），需要你将这些论文的内容进行汇总梳理成一个子章节，总结内容以json的格式返回，要求包含该子章节的标题和内容，key是"subchapter heading"和"subchapter content",value是对应的内容。

        输出格式：
        {"subchapter heading":value,"subchapter content":value1}
        """
    query_prompt = f"""
    检索关键词query:
    {query}

    论文信息：
    {paper_info_list_str}
    
    无论前面输入的语言是什么，请你用{language}输出对应的内容。
    """
    while True:
        summary_dict_str = chat_gpt.gpt_respond(query_prompt,sys_prompt,response_format="json_object")
        try:
            summary_dict = json.loads(summary_dict_str)
            if ("subchapter heading" in summary_dict.keys()) and ("subchapter content" in summary_dict.keys()):
                break
        except Exception as e:
            print(summary_dict_str)
            print(e)
    return summary_dict

def summary_all_papers(topic_name=None,update_pdf_info=True):
    pdf_info_json_path = os.path.join(Config.project_path,Config.pdf_info_json_path)
    with open(pdf_info_json_path,"r",encoding="utf-8") as f:
        pdf_info_json = json.load(fp=f)
    search_query_list = list(set([i["search_query"] for i in pdf_info_json]))
    pdf_info_json_copy = copy.deepcopy(pdf_info_json)
    pdf_info_dict_by_search_query = defaultdict(list)
    for index_i,pdf_info in enumerate(pdf_info_json):
        search_query_i = pdf_info["search_query"]
        if search_query_i != "None":
            pdf_info_dict_by_search_query[search_query_i].append(pdf_info)
        else:
            search_query_i = paper_classification(pdf_info,search_query_list)
            if search_query_i not in search_query_list:
                search_query_list.append(search_query_i)
            pdf_info["search_query"] = search_query_i
            pdf_info_json_copy[index_i] = pdf_info
            pdf_info_dict_by_search_query[search_query_i].append(pdf_info)
    if update_pdf_info:
        with open(pdf_info_json_path,"w",encoding="utf-8") as f:
            json.dump(pdf_info_json_copy,fp=f)
    # print(pdf_info_dict_by_search_query)
    field_summary_dict = {}
    for index_i,(query_i,pdf_infos_i) in enumerate(pdf_info_dict_by_search_query.items()):
        print(f"正在总结第{str(index_i+1)}个子章节（一共{str(len(search_query_list))}个章节）")
        subchapter_dict = summary_one_class_papers(query_i,pdf_infos_i,topic_name)
        subchapter_dict["references"] = pdf_infos_i
        field_summary_dict[query_i]=subchapter_dict
    # print(field_summary_dict)
    field_summary_path = os.path.join(Config.project_path,Config.process_folder,"field_summary.json")
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    field_summary_dict1 = {
        "topic":topic_name,
        "generate_time":current_time_str,
        "field_summary":field_summary_dict
    }
    with open(field_summary_path,"w",encoding="utf-8",) as f:
        json.dump(field_summary_dict1,f,indent=4,ensure_ascii=False)
    return field_summary_dict1
if __name__ =="__main__":
    topic_name = "面向城市治理的政务文本挖掘与分类研究"
    summary_all_papers(topic_name)


