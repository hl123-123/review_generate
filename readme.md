# 一键生成论文综述

## 整体思路
1. 输入论文主题
2. 基于论文主题生成相关领域的检索关键词，相当于把具体的一篇论文看作多个子领域的交集
3. 基于检索关键词 下载对应的论文文献，因此每个检索关键词都下载了几篇对应的文献（基于arxiv的API），并且把论文信息整理在对应json文件下，每篇论文都保存在一个dict中，一共有以下key:
   1. title(论文标题)
   2. summary(直接使用论文摘要部分进行初始化)
   3. pdf_url(论文的URL地址)
   4. authors(作者)
   5. crawled_time(本项目爬取该论文时间)
   6. published_time(论文公开时间)
   7. search_query(检索这篇论文的检索关键词)
   8. save_path(本地下载路径)
4. 以用相同的检索关键词作为子领域分类标准，把同一个子领域的论文作为 综述 正文部分（国内外研究）的其中一个子章节，在这个步骤，我会给每个子章节内容让LLM自己插入引用编号
5. 基于综述正文生成 前文和总结和摘要。
6. 将正文各个章节的相关论文引用进行重新编号，整理参考论文部分，

## 具体效果（以母猪的产后护理为例）
综述效果，请直接看save_data/process_data1/review.txt。 

## 操作指南
1. 安装好requirements.txt中所有的包
2. 复制config_template.py在同路径粘贴为config.py,同时进行config.py中的一些路径和API的填充。
3. 可以运行main.py，这是直接一键运行的。
4. 也可以直接运行webui.py


## 🌟 Star History



[![Star History Chart](https://api.star-history.com/svg?repos=hl123-123/review_generate&type=Timeline)](https://star-history.com/#hl123-123/review_generate&Timeline)