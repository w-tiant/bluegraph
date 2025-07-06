import streamlit as st
import os
import time  # 引入 time 模块
from lightrag import QueryParam

# 你的其他模块导入
from .rag import main as rag_init
from .graph_viz import view as graph_viz
from .obj_viz import func as obj_viz
from .data_viz import func as data_viz
from .muti_input import extract_text_from_pdf, extract_text_from_docx

from io import BytesIO

# --- 核心 main 函数 ---
def main():
    st.set_page_config(layout="wide", page_title="BlueGraph")
    st.title('BlueGraph')

    # session_state 管理
    if 'rag_instance' not in st.session_state:
        st.session_state.rag_instance = None
    if 'project_path' not in st.session_state:
        st.session_state.project_path = None
    if 'graph_generated' not in st.session_state:
        st.session_state.graph_generated = False

    # --- 步骤 1: 创建项目工作目录 ---
    if not st.session_state.rag_instance:
        st.header("步骤 1: 创建一个新项目")
        st.info("在云端，我们需要先创建一个工作空间来存放您的图谱。")
        
        project_name = st.text_input("给您的项目起个名字", value="my_reading_project")

        if st.button("创建并开始", type="primary"):
            with st.spinner("正在创建工作目录并初始化引擎..."):
                temp_dir = project_name
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                st.session_state.rag_instance = rag_init(temp_dir)
                st.session_state.project_path = temp_dir
            
            st.success(f"项目 '{project_name}' 已创建！")
            st.rerun()

    # --- 主功能区 ---
    if st.session_state.rag_instance:
        rag = st.session_state.rag_instance
        path = st.session_state.project_path
        
        insert_tab, graph_tab, query_tab, obj_tab, origin_tab = st.tabs(
            ['解析文本', '关系图', '智能查询', '对象列表', '原文']
        )

        with insert_tab:
            st.header("步骤 2: 上传并解析单个文档")
            
            uploaded_file = st.file_uploader(
                "请选择一个文件进行解析", 
                type=['txt', 'md', 'pdf', 'docx']
            )

            if uploaded_file is not None:
                st.write(f"已选择文件: `{uploaded_file.name}`")
                
                if st.button("开始解析此文件", type="primary"):
                    content = ""
                    try:
                        file_type = uploaded_file.name.split('.')[-1].lower()
                        
                        with st.spinner(f"正在从 {file_type} 文件中提取文本..."):
                            if file_type == 'pdf':
                                content = extract_text_from_pdf(BytesIO(uploaded_file.getvalue()))
                            elif file_type == 'docx':
                                content = extract_text_from_docx(BytesIO(uploaded_file.getvalue()))
                            else:
                                content = uploaded_file.getvalue().decode("utf-8")
                        
                        st.success("文本提取成功！")

                        # =======================================================
                        # 这是集成了强制等待和文件检查的调试逻辑
                        # =======================================================
                        with st.spinner("正在处理文本并构建知识图谱... (包含调试等待)"):
                            # 1. 调用 insert
                            st.info("1. 正在调用 `rag.insert(content)`...")
                            rag.insert(content)
                            st.info("2. `rag.insert` 调用已返回，无异常。")

                            # 2. 强制等待
                            wait_time = 10  # 让我们等待10秒，给足后台时间
                            st.info(f"3. 强制等待 {wait_time} 秒，以便后台任务完成...")
                            
                            progress_bar = st.progress(0)
                            for i in range(wait_time):
                                time.sleep(1)
                                progress_bar.progress((i + 1) / wait_time)
                            
                            st.info("4. 等待结束。")

                            # 3. 检查文件是否存在
                            graph_file_path = os.path.join(path, "graph_chunk_entity_relation.graphml")
                            
                            st.info(f"5. 正在检查文件是否存在于: `{graph_file_path}`")
                            if os.path.exists(graph_file_path):
                                st.success("✅ 文件已成功找到！图谱生成完毕。")
                                st.session_state.graph_generated = True
                            else:
                                st.error("❌ 等待后，文件依然未找到！")
                                # 顺便看一下目录里到底有什么
                                if os.path.exists(path):
                                    files_in_dir = os.listdir(path)
                                    st.warning(f"当前 `{path}` 目录内容: `{files_in_dir}`")
                                else:
                                    st.error(f"严重错误：工作目录 `{path}` 本身都消失了！")
                        # =======================================================
                        # 调试逻辑结束
                        # =======================================================

                    except Exception as e:
                        st.error(f"处理文件时发生严重错误！")
                        st.exception(e)


        with graph_tab:
            # (这部分代码保持不变)
            if not st.session_state.graph_generated:
                st.info("请先在 '解析文本' 标签页中上传并解析一个文件。")
            else:
                graph_viz(path)
        
        # ... 其他标签页逻辑保持不变 ...
        with query_tab:
            if not st.session_state.graph_generated:
                st.info("请先在 '解析文本' 标签页中生成图谱。")
            else:
                st.header('智能查询')
                prompt = st.text_input('输入任何问题', placeholder="例如：王超杰是谁？")
                if st.button('查询'):
                    if prompt:
                        with st.spinner("正在思考..."):
                            answer = rag.query(prompt, param=QueryParam(mode="naive"))
                            st.markdown(answer)
                    else:
                        st.warning("请输入您的问题。")
        with obj_tab:
            if not st.session_state.graph_generated:
                st.info("请先在 '解析文本' 标签页中生成图谱。")
            else:
                obj_viz(path)
        
        with origin_tab:
            if not st.session_state.graph_generated:
                st.info("请先在 '解析文本' 标签页中生成图谱。")
            else:
                data_viz(path)

if __name__ == "__main__":
    main()