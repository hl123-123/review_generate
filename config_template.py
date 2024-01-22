import os
class Config: #李开宇
    openai_key = ""#openai_api_key
    openai_model = "gpt-4-1106-preview"#或者gpt-3.5-turbo-1106
    project_path = r"D:\project\综述生成" #项目所在的绝对路径
    # 下面如果想要不同的论文保存在新的文件夹，只需要把下面3个路径中的save_data进行替换就行，不需要手动创建文件夹
    pdf_folder = "save_data/pdf_data1" #想要保存pdf的文件夹的位置
    pdf_info_json_path = "save_data/pdf_info1.json" #保存pdf_folder里面所有pdf的基本信息的json
    process_folder = "save_data/process_data1" #保存基于原始信息的处理后信息，比如基于对于每个search_query下的相关论文进行总结的结果等。


abs_pdf_folder = os.path.join(Config.project_path,Config.pdf_folder)
if not os.path.exists(abs_pdf_folder):
    os.makedirs(abs_pdf_folder)

abs_process_folder = os.path.join(Config.project_path,Config.process_folder)
if not os.path.exists(abs_process_folder):
    os.makedirs(abs_process_folder)