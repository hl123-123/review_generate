import os
from config import Config
from data_process import get_search_keywords
from data_process import get_arxiv_paper
from data_process import summary_all_papers
from review_generation import generate_review
topic_name = ("母猪的产后护理")#论文标题
keywords_list = get_search_keywords(topic_name)#1. 生成检索关键词
print(keywords_list)
for query in keywords_list:
    paper_info_list = get_arxiv_paper(query, 5) #2. 下载论文

summary_all_papers(topic_name)# 3. 论文总结
field_summary_path = os.path.join(Config.project_path, Config.process_folder, "field_summary.json")
review_dict_path = os.path.join(Config.project_path, Config.process_folder, "review.json")
review_txt_path = os.path.join(Config.project_path, Config.process_folder, "review.txt")
generate_review(field_summary_path, review_dict_path, review_txt_path) # 4.生成完整综述
