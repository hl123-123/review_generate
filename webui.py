import json
import gradio as gr
import os
from config import Config
from data_process import get_search_keywords
from data_process import get_arxiv_paper
from data_process import summary_all_papers
from review_generation import generate_review
def generate_review_wb():
    field_summary_path = os.path.join(Config.project_path, Config.process_folder, "field_summary.json")
    review_dict_path = os.path.join(Config.project_path, Config.process_folder, "review.json")
    review_txt_path = os.path.join(Config.project_path, Config.process_folder, "review.txt")
    review_txt = generate_review(field_summary_path, review_dict_path, review_txt_path)
    return review_txt
def get_search_keywords_wb(paper_title,language):
    keywords_list = get_search_keywords(paper_title,language)
    print(keywords_list)
    keywords_str = ";".join(keywords_list)
    keywords_num = len(keywords_list)
    return keywords_str,keywords_num

def summary_all_papers_wb(paper_title):
    field_summary_dict1 = summary_all_papers(paper_title)
    try:
        field_summary_str = json.dumps(field_summary_dict1,indent=4,ensure_ascii=False)
    except:
        field_summary_str = json.dumps(field_summary_dict1,indent=4)
    return field_summary_str
def download_paper_wb(keywords,sub_paper_num):
    keywords_list = keywords.split(";")
    for index_i,query in enumerate(keywords_list):
        print(f"下载进度：{str(index_i)}/{str(len(keywords_list))} (已下载的关键词/全部关键词数)")
        paper_info_list = get_arxiv_paper(query, sub_paper_num)
    try:
        all_paper_str = json.dumps(paper_info_list,indent=4,ensure_ascii=False)
    except:
        all_paper_str = json.dumps(paper_info_list,indent=4)
    return all_paper_str


with gr.Blocks(title="一键综述生成") as demo:
    gr.HTML("""<h1 align="center">一键综述生成</h1>""")
    with gr.Accordion("第一步：检索关键词生成"): # 可折叠的组件
        with gr.Row():
            with gr.Column(scale=2):
                paper_name = gr.Textbox(label="输入你的论文名称", show_label=True)
            with gr.Column(scale=1):
                keywords_language = gr.Dropdown(
                    ["English","中文"],
                    label="关键词语言",
                    value="English",
                )
        gen_keywords_button = gr.Button("生成")
        gr.HTML("""<p align="center">你可以对于生成后的检索关键词进行修改，比如觉得检索关键词太多可以删掉一些。但是注意，关键词和关键词之间使用英文分号“;”隔开</p>""")
        with gr.Row():
            with gr.Column(scale=2):
                keywords_str = gr.Textbox(label="检索关键词", interactive=True)
            with gr.Column(scale=1):
                keywords_num = gr.Textbox(label="得到的关键词数量")
    gen_keywords_button.click(fn=get_search_keywords_wb,inputs=[paper_name,keywords_language],outputs=[keywords_str,keywords_num])
    with gr.Accordion("第二步：论文下载(从arxiv，所有论文下载至config.py中定义的pdf_folder),论文信息整理在pdf_info_json_path"):
        sub_paper_num = gr.Slider(1, 7, value=5, step=1, label="每个检索关键词下载的论文篇数", show_label=True)
        paper_download_button = gr.Button("下载")
        all_paper_info = gr.Textbox(label="所有论文信息")
    paper_download_button.click(fn=download_paper_wb,inputs=[keywords_str,sub_paper_num],outputs=all_paper_info)
    with gr.Accordion("第三步：把所有论文按照子主题（检索关键词）进行总结，生成到process_folder/field_summary.json"):
        summary_button = gr.Button("总结")
        summary_content = gr.Textbox(label="预览总结生成的结果")
    summary_button.click(fn=summary_all_papers_wb,inputs=[paper_name],outputs=[summary_content])
    with gr.Accordion("第四步：生成一篇完整的综述"):
        gen_review_button = gr.Button("生成")
        review_content = gr.Textbox(label="预览综述的结果")
    gen_review_button.click(fn=generate_review_wb,inputs=None,outputs=[review_content])






if __name__ == "__main__":
    demo.queue().launch(server_name='127.0.0.1',
                server_port= 2021, #2021
                show_api=False,
                share=False,
                inbrowser=False)
