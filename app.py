import os
# 设置环境变量
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
# 下载模型
os.system('huggingface-cli download --resume-download sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --local-dir ./sentence-transformer')
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from langchain.vectorstores import Chroma
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import os
from LLM import InternLM_LLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from openxlab.model import download
import openxlab
openxlab.login(ak='k2kxnxb5j7dewd9yvqzl', sk='ozx4r5e6oedlwba8epoxnxenjapmm0dkn21jyvnx') 


from openxlab.dataset import get
get(dataset_repo='Xpg12138/pigandcow', target_path='./data_base/vector_db/') # 数据集下载

def print_tree(folder_path, indent='', file_path=''):
    # 打印当前目录名称
    print(indent + os.path.basename(folder_path) + '/')
    
    # 获取子目录和文件列表
    subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir()]
    files = [f.name for f in os.scandir(folder_path) if f.is_file()]
    
    # 递归打印子目录
    for i, subfolder in enumerate(sorted(subfolders)):
        # 判断是否为最后一个子目录
        if i == len(subfolders) - 1 and len(files) == 0:
            print_tree(subfolder, indent + '  ')
        else:
            print_tree(subfolder, indent + '│ ')
            
    # 打印文件
    for i, file in enumerate(sorted(files)):
        # 判断是否为最后一个文件
        if i == len(files) - 1:
            print(indent + '└── ' + file)
        else:
            print(indent + '├── ' + file)

# 测试程序
folder_path = './'
print_tree(folder_path)

# 定义原始文件路径和新文件名
old_file = "./data_base/vector_db/Xpg12138___pigandcow/pig_cow/chroma.pkl"
new_name = "chroma.sqlite3"
 
# 构建新文件路径
new_file = os.path.join(os.path.dirname(old_file), new_name)
 
try:
    # 重命名文件
    os.rename(old_file, new_file)
    print("文件已成功更名为", new_name)
except FileNotFoundError:
    print("未找到指定的文件")
except Exception as e:
    print("发生错误: ", str(e))
    
download(model_repo='OpenLMLab/InternLM-chat-7b',output='./internlm-chat-7b')
def load_chain():
    # 加载问答链
    # 定义 Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="./sentence-transformer")

    # 向量数据库持久化路径
    persist_directory = './data_base/vector_db/Xpg12138___pigandcow/pig_cow'

    # 加载数据库
    vectordb = Chroma(
        persist_directory=persist_directory,  # 允许我们将persist_directory目录保存到磁盘上
        embedding_function=embeddings
    )

    # 加载自定义 LLM
    llm = InternLM_LLM(model_path = "./internlm-chat-7b")

    # 定义一个 Prompt Template
    template = """使用以下上下文来回答最后的问题。如果你不知道答案，就说你不知道，不要试图编造答
    案。尽量使答案简明扼要。总是在回答的最后说“谢谢你的提问！”。
    {context}
    问题: {question}
    有用的回答:"""

    QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context","question"],template=template)

    # 运行 chain
    qa_chain = RetrievalQA.from_chain_type(llm,retriever=vectordb.as_retriever(),return_source_documents=True,chain_type_kwargs={"prompt":QA_CHAIN_PROMPT})
    
    return qa_chain

class Model_center():
    """
    存储检索问答链的对象 
    """
    def __init__(self):
        # 构造函数，加载检索问答链
        self.chain = load_chain()

    def qa_chain_self_answer(self, question: str, chat_history: list = []):
        """
        调用问答链进行回答
        """
        if question == None or len(question) < 1:
            return "", chat_history
        try:
            chat_history.append(
                (question, self.chain({"query": question})["result"]))
            # 将问答结果直接附加到问答历史中，Gradio 会将其展示出来
            return "", chat_history
        except Exception as e:
            return e, chat_history

import gradio as gr

# 实例化核心功能对象
model_center = Model_center()
# 创建一个 Web 界面
block = gr.Blocks()
with block as demo:
    with gr.Row(equal_height=True):   
        with gr.Column(scale=15):
            # 展示的页面标题
            gr.Markdown("""<h1><center>InternLM</center></h1>
                <center>畜禽知识问答</center>
                """)

    with gr.Row():
        with gr.Column(scale=4):
            # 创建一个聊天机器人对象
            chatbot = gr.Chatbot(height=450, show_copy_button=True)
            # 创建一个文本框组件，用于输入 prompt。
            msg = gr.Textbox(label="Prompt/问题")

            with gr.Row():
                # 创建提交按钮。
                db_wo_his_btn = gr.Button("Chat")
            with gr.Row():
                # 创建一个清除按钮，用于清除聊天机器人组件的内容。
                clear = gr.ClearButton(
                    components=[chatbot], value="Clear console")
                
        # 设置按钮的点击事件。当点击时，调用上面定义的 qa_chain_self_answer 函数，并传入用户的消息和聊天历史记录，然后更新文本框和聊天机器人组件。
        db_wo_his_btn.click(model_center.qa_chain_self_answer, inputs=[
                            msg, chatbot], outputs=[msg, chatbot])

    gr.Markdown("""提醒：<br>
    1. 初始化数据库时间可能较长，请耐心等待。
    2. 使用中如果出现异常，将会在文本输入框进行展示，请不要惊慌。 <br>
    """)
gr.close_all()
# 直接启动
demo.launch()
