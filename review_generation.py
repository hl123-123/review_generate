#encoding=utf-8
import os
from config import Config
import json
import re
from utils import *
field_summary_path = os.path.join(Config.project_path, Config.process_folder, "field_summary.json")

def generate_introduction(main_content,title,language="中文"):
    chat_gpt = Chat_gpt()
    sys_prompt = """
你是一个专业的学者，很擅长基于一篇综述的国内外研究 生成这篇综述的前文部分。
我会给你该篇综述的标题，该篇综述的国内外研究部分，请你生成对应的前文部分。
前文部分需要包括该综述的时代背景，并且逐渐引出该综述的意义，和该综述主要研究的方向。为下面国内外研究部分进行铺垫。
前文内容参考句式：
```
随着.....的发展，.....现在还存在着.....的问题，基于.....的现实状况，需要.....的解决，所以....是值得深入发展的课题。因\
此对于....问题的研究，具有一定的现实意义和理论意义。所以....的研究很有必要。
```

要求：输出的json只有单层结构，不存在dict嵌套。
输出格式：
{"introduction":value}
"""

    query_prompt = f"""
综述标题:
{title}的文献综述
    
国内外研究：
{main_content}
    
无论前面输入的语言是什么，请你用{language}输出对应的内容。
"""
    introduction_dict_str = chat_gpt.gpt_respond(query_prompt,sys_prompt,"json_object")
    introduction_str = json.loads(introduction_dict_str)["introduction"]
    return introduction_str

def generate_conclusion(introduction,main_content,title,language="中文"):
    chat_gpt = Chat_gpt()
    sys_prompt = """
    你是一个专业的学者，很擅长基于一篇综述的前文，国内外研究 生成这篇综述的总结部分。
    我会给你该篇综述的标题，该篇综述的前文，国内外研究部分，请你生成对应的总结部分。
    总结部分需要概述国内外研究部分，并且与前文部分 进行呼应，突出本篇综述的价值，和对未来该领域的展望。
    总结内容参考句式：
    综上所述，国内外学者对......、......和......的研究，为......理论的发展提供了丰富的基础，也在....\
    ..、......等实践方面提供了大量的案例研究参照，对.....的理论和实践发展起到了重要的推动作用，同时也是本文\
    进行......有关案例研究的理论参考和对策参照。整体而言，这些研究表明......。

    要求：输出的json只有单层结构，不存在dict嵌套。
    输出格式：
    {"conclusion":value}
    """

    query_prompt = f"""
    综述标题:
    {title}的文献综述

    前文：
    {introduction}
    
    国内外研究：
    {main_content}

    无论前面输入的语言是什么，请你用{language}输出对应的内容。
    """
    conclusion_dict_str = chat_gpt.gpt_respond(query_prompt, sys_prompt, "json_object")
    conclusion_str = json.loads(conclusion_dict_str)["conclusion"]
    return conclusion_str


def generate_abstract(introduction, main_content,conclusion, title, language="中文"):
    chat_gpt = Chat_gpt()
    print("正在生成摘要")
    sys_prompt = """
    你是一个专业的学者，很擅长基于一篇综述的前文，国内外研究,总结 生成这篇综述的摘要部分。
    我会给你该篇综述的标题，该篇综述的前文，国内外研究部分，总结部分，请你生成对应的综述的摘要部分。

    要求：输出的json只有单层结构，不存在dict嵌套。
    输出格式：
    {"abstract":value}
    """

    query_prompt = f"""
    综述标题:
    {title}的文献综述

    前文：
    {introduction}

    国内外研究：
    {main_content}
    
    总结：
    {conclusion}

    无论前面输入的语言是什么，请你用{language}输出对应的内容。
    """
    abstract_dict_str = chat_gpt.gpt_respond(query_prompt, sys_prompt, "json_object")
    abstract_str = json.loads(abstract_dict_str)["abstract"]
    return abstract_str

def review_dict2txt(review_dict):
    review_txt = ""
    review_txt += review_dict["title"]+"\n"
    review_txt += "摘要："+review_dict["摘要"]+"\n"
    review_txt += "keywords:"+review_dict["keywords"]+"\n"
    review_txt += "一、前言\n"+review_dict["前言"]+"\n"
    review_txt +="二、 国内外相关研究\n"+review_dict["国内外相关研究"]+"\n"
    review_txt +="三、 结论\n" +review_dict["结论"]+"\n"
    review_txt +="文献综述参考文献： \n"+review_dict["文献综述参考文献"]
    return review_txt
def generate_review(field_summary_path,review_dict_path,review_txt_path):
    '''
    基于summary_all_papers()按照不同search_query进行分类总结的json文件 生成最终的综述
    :param field_summary_path:
    :param review_dict_path:
    :param review_txt_path:
    :return:
    '''
    review_dict = {}
    with open(field_summary_path, "r", encoding="utf-8") as f:
        field_summary_dict1 = json.load(f)

    review_content = ""

    field_summary_dict = field_summary_dict1["field_summary"]
    topic_name = field_summary_dict1["topic"]
    references_list = []
    keywords = []
    for index_i,(keyword_i,field_summary_dict_i) in enumerate(field_summary_dict.items(),1):
        keywords.append(keyword_i)
        review_content += "\n"
        review_content += f"（{int_to_chinese_num(index_i)}）"
        review_content += field_summary_dict_i["subchapter heading"]
        review_content += "\n"
        subchapter_content = field_summary_dict_i["subchapter content"]
        subchapter_content = re.sub(r'\[(\d+)\]', lambda x: '[' + str(int(x.group(1)) + len(references_list)) + ']',
                                    subchapter_content)
        references_list += field_summary_dict_i["references"]
        review_content += subchapter_content

    references_str = ""
    for index_i,references_dict_i in enumerate(references_list,1):
        authors_str = "，".join(references_dict_i["authors"])
        title_str = references_dict_i["title"]
        pdf_url = references_dict_i["pdf_url"]
        published_time = references_dict_i["published_time"].split(" ")[0]
        references_str_i = f"[{str(index_i)}]{authors_str}.{title_str}[EB/OL].{published_time}.{pdf_url}."
        references_str += ('\n'+references_str_i)
    references_str = references_str.strip()
    review_dict["文献综述参考文献"] = references_str
    review_dict["keywords"]=(";".join(keywords))
    introduction_str = generate_introduction(review_content,topic_name)
    review_dict["title"] = topic_name+"的文献综述"
    review_dict["前言"] = introduction_str
    review_dict["国内外相关研究"] = review_content
    conclusion_str = generate_conclusion(introduction_str,review_content,topic_name)
    review_dict["结论"] = conclusion_str
    abstract_str = generate_abstract(introduction_str,review_content,conclusion_str,topic_name)
    review_dict["摘要"] = abstract_str
    with open(review_dict_path,"w",encoding="utf-8",) as f:
        json.dump(review_dict,f,indent=4,ensure_ascii=False)

    review_txt = review_dict2txt(review_dict)
    with open(review_txt_path,"w",encoding="utf-8",) as f:
        f.write(review_txt)
    return review_txt

if __name__ == "__main__":
    field_summary_path = os.path.join(Config.project_path,Config.process_folder,"field_summary.json")
    review_dict_path = os.path.join(Config.project_path,Config.process_folder,"review.json")
    review_txt_path = os.path.join(Config.project_path,Config.process_folder,"review.txt")
    generate_review(field_summary_path,review_dict_path,review_txt_path)






