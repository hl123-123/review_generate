import json
import os
from PyPDF2 import PdfReader
import os
import arxiv
import datetime
from datetime import datetime
import requests
import re
from config import Config
def clean_title_for_filename(title):
    '''
    为防止论文题目直接进行文件命名会涉及命名非法的问题，这里将论文标题名称进一步处理
    :param title:原始的论文标题
    :return:转换后的论文标题
    '''
    # 移除非法字符
    safe_title = re.sub(r'[\\/*?:"<>|,]', '', title)
    # 替换空格为下划线
    safe_title = safe_title.replace(' ', '_')
    # 缩短标题长度（如果需要）
    max_length = 255
    if len(safe_title) > max_length:
        safe_title = safe_title[:max_length]
    return safe_title

def get_arxiv_paper(query,max_num=20,is_download=True):
    '''
    基于查询内容query
    :param query:
    :param max_num:
    :param download_folder:
    :return:
    '''
    search = arxiv.Search(query, max_results=max_num)#默认sort_by基于论文相关性进行优先级查找，可改为提交时间或者最后一次更新为优先级查找
    client = arxiv.Client()
    results = client.results(search)

    papers_list = []
    for i, result in enumerate(results):
        print(result)
        paper_dict = {}
        paper_dict["title"] = result.title
        paper_dict["summary"] = result.summary #arxiv的summary就是paper的abstract
        paper_dict["pdf_url"] = result.pdf_url
        paper_dict["authors"] = [i.name for i in result.authors]
        # 获取当前时间
        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        paper_dict["crawled_time"] = current_time_str
        paper_dict["published_time"] = result.published.strftime("%Y-%m-%d %H:%M:%S")
        paper_dict["search_query"] = query

        if is_download:
            title = result.title
            title = clean_title_for_filename(title)
            save_path = os.path.join(Config.project_path,Config.pdf_folder,title + '.pdf')
            download_tf = download_arxiv_paper(paper_dict["pdf_url"],save_path)
            if download_tf:
                paper_dict["save_path"] = save_path
            else:
                paper_dict["save_path"] = "None"
        else:
            paper_dict["save_path"]="None"

        papers_list.append(paper_dict)

    pdf_info_json_path = os.path.join(Config.project_path,Config.pdf_info_json_path)
    if not os.path.exists(pdf_info_json_path):
        all_pdf_info_list0 = []
        all_pdf_info_dict0 = {}
    else:
        with open(pdf_info_json_path,mode="r") as f:
            all_pdf_info_list0 = json.load(fp=f)
            all_pdf_info_dict0 ={i["title"]:i for i in all_pdf_info_list0}
    for paper_dict in papers_list:
        all_pdf_info_dict0[paper_dict["title"]] = paper_dict
    all_pdf_info_list = list(all_pdf_info_dict0.values())
    with open(pdf_info_json_path, mode="w") as f:
        json.dump(all_pdf_info_list,fp=f,indent=4)
    return all_pdf_info_list




def download_arxiv_paper(url, save_path):
    # URL of the arXiv paper

    # Regular expression to extract the arXiv ID
    arxiv_id_pattern = r'arxiv\.org/(abs|pdf)/(\d+\.\d+)(v\d+)?'
    if re.search(r'\.pdf$', url, re.IGNORECASE):
        # return "PDF file URL"
        url = url
    # Regular expression for arXiv paper page URL
    elif re.search(r'arxiv\.org/(abs|pdf)/\d+\.\d+(v\d+)?', url):
        # return "arXiv paper page URL"

        match = re.search(arxiv_id_pattern, url)

        # Extracting the arXiv ID
        arxiv_id = match.group(2) if match else None

        url = f'https://arxiv.org/pdf/{arxiv_id}.pdf'

    response = requests.get(url)

    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print("Download successful")
        return True
    else:
        print("Error: Unable to download the paper")
        return False
def extract_pdf_title(file_path):
    '''
    从pdf论文中获取论文标题
    :param file_path: pdf路径
    :return: paper标题
    '''
    try:
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            title = pdf.metadata.title
            return title if title else "Title not found in the document metadata."
    except Exception as e:
        print(e)
        return str(e)


def extract_abstract(file_path):
    '''
    从pdf论文中获取论文摘要
    :param file_path: pdf路径
    :return: paper摘要
    '''
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        # Finding the abstract part
        start_idx = text.lower().find("abstract")
        end_idx = text.lower().find("introduction")
        if end_idx!= -1 and start_idx != -1:
            return text[start_idx:end_idx].strip()
        if start_idx != -1:
            # Some assumed length for abstract, since end is not defined
            end_idx = text.find("\n",start_idx+800)
            return text[start_idx:end_idx].strip()
        else:
            return "Abstract not found."
    except Exception as e:
        return str(e)
def update_pdf_info():
    '''
    当手动把论文pdf下载到save_data/pdf_data后，pdf_info.json自动更新
    :return:
    '''
    pdf_folder = os.path.join(Config.project_path,Config.pdf_folder)
    local_pdf_list = os.listdir(pdf_folder)
    pdf_info_json_path = os.path.join(Config.project_path,Config.pdf_info_json_path)
    with open(pdf_info_json_path, mode="r") as f:
        all_pdf_info_list0 = json.load(fp=f)
        save_pdf_list = [os.path.basename(i["save_path"]) for i in all_pdf_info_list0]
    for local_pdf_i in local_pdf_list:
        if local_pdf_i not in save_pdf_list:
            paper_dict = {}
            local_pdf_save_path = os.path.join(pdf_folder,local_pdf_i)
            paper_dict["save_path"] = local_pdf_save_path
            paper_dict["title"] = extract_pdf_title(local_pdf_save_path)
            paper_dict["summary"] = extract_abstract(local_pdf_save_path)
            paper_dict["pdf_url"] = "None"
            paper_dict["authors"] = ["None"]
            # 获取当前时间
            current_time = datetime.now()
            current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            paper_dict["crawled_time"] = current_time_str
            paper_dict["published_time"] = "None"
            paper_dict["search_query"] = "None"
            all_pdf_info_list0.append(paper_dict)

    with open(pdf_info_json_path, mode="w") as f:
        json.dump(all_pdf_info_list0,fp=f,indent=4)





if __name__ == "__main__":
    from data_process import get_search_keywords
    keywords_list= get_search_keywords("面向城市治理的政务文本挖掘与分类研究")
    print(keywords_list)
    for query in keywords_list:
        paper_info_list = get_arxiv_paper(query,5)
    # query = "LLM agent"
    # paper_info_list = get_arxiv_paper(query,20)
    # print(paper_info_list)

    # title = "Bounded Approval Ballots: Balancing Expressiveness and Simplicity for Multiwinner Elections"
    # cleaned_title = clean_title_for_filename(title)
    # print(cleaned_title)

    # pdf_path = r"D:\project\收集信息的助理\save_data\pdf_data\Bounded_Approval_Ballots_Balancing_Expressiveness_and_Simplicity_for_Multiwinner_Elections.pdf"
    # pdf_title = extract_abstract(pdf_path)
    # print(pdf_title)
    # update_pdf_info()