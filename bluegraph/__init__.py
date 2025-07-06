import streamlit as st
import os
# import tkinter as tk
# from tkinter import filedialog
from lightrag import QueryParam

from .rag import main as rag_init
from .muti_input import muti_input
from .graph_viz import view as graph_viz
from .obj_viz import func as obj_viz
from .data_viz import func as data_viz

def main():
    st.set_page_config(layout="wide", page_title="BlueGraph - 交互式阅读图谱")
    st.title('BlueGraph')

    # 使用 session_state 初始化和管理核心对象
    if 'rag_instance' not in st.session_state:
        st.session_state.rag_instance = None
    if 'project_path' not in st.session_state:
        st.session_state.project_path = None

    # --- 新的文件上传和项目初始化逻辑 ---
    st.sidebar.header("项目初始化")
    
    # 使用 st.file_uploader 允许用户上传多个文件
    uploaded_files = st.sidebar.file_uploader(
        "上传文档进行分析",
        type=['txt', 'md', 'docx', 'pdf'],
        accept_multiple_files=True,
        help="您可以一次性上传多个文档，系统将融合它们构建知识图谱。"
    )

    # 当用户上传了文件，并且项目尚未初始化时，执行初始化
    if uploaded_files and st.session_state.rag_instance is None:
        
        # 创建一个临时目录来存放上传的文件
        # 这里使用 "temp_project" 作为项目目录名
        temp_dir = "temp_project"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # 将用户上传的每个文件保存到临时目录
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        # 显示处理状态
        with st.spinner("正在解析文档并构建知识图谱，请稍候..."):
            # 使用包含上传文件的临时目录路径来初始化 RAG 引擎
            st.session_state.rag_instance = rag_init(temp_dir)
            st.session_state.project_path = temp_dir
        
        st.success("项目初始化成功！现在可以开始探索了。")
        # 强制刷新一下界面，以展示下面的主内容区
        st.rerun()

    # --- 主内容区 ---
    # 只有在项目成功初始化后，才显示标签页和主要功能
    if st.session_state.rag_instance:
        
        # 将 RAG 实例和路径从 session_state 中取出，方便使用
        rag = st.session_state.rag_instance
        path = st.session_state.project_path

        # 你的原标签页结构
        insert_tab, graph_tab, query_tab, obj_tab, origin_tab = st.tabs(
            ['➕ 追加文件', '关系图', '智能查询', '对象列表', '原文']
        )

        with insert_tab:
            st.header('向当前项目追加新文件')
            st.info("在这里上传的文件将会被添加到已有的知识图谱中。")
            
            # 你的 muti_input 组件现在可以这样被调用
            # 假设 muti_input 是一个能处理文件上传的组件
            def after_insert(new_files_results):
                st.info('正在处理并融合新文件...')
                rag.insert(new_files_results) # 调用 RAG 的 insert 方法
                st.success('新文件已成功融合到知识图谱！')
            
            # 注意：你需要确保 muti_input 适应新的 Web 上传逻辑
            # 如果它也是基于 tkinter 的，也需要一并修改
            # 这里假设它是一个可以调用的函数
            muti_input(after_insert)

        with graph_tab:
            # graph_viz 函数现在使用 session_state 中存储的路径
            graph_viz(path)

        with query_tab:
            st.header('智能查询')
            st.info("基于已构建的知识图谱和原文进行智能问答。")
            prompt = st.text_input('输入任何问题', placeholder="例如：王超杰是谁？")
            
            if st.button('查询'):
                if prompt:
                    with st.spinner("正在思考..."):
                        # 调用 RAG 的 query 方法
                        answer = rag.query(prompt, param=QueryParam(mode="naive"))
                        st.markdown(answer)
                else:
                    st.warning("请输入您的问题。")

        with obj_tab:
            # obj_viz 函数使用 session_state 中存储的路径
            obj_viz(path)

        with origin_tab:
            # data_viz 函数使用 session_state 中存储的路径
            data_viz(path)

    # 如果项目尚未初始化，显示欢迎和引导信息
    else:
        st.info("👈 请在左侧边栏上传文档来启动您的分析项目。")
        st.markdown("""
        ### 欢迎使用 BlueGraph!
        
        BlueGraph 是一款交互式阅读辅助系统，您只需上传文本，即可：
        
        - **自动生成**知识图谱
        - **智能查询**关键信息
        - **回溯原文**进行深度探索
        
        开始您的“读结构”之旅吧！
        """)


if __name__ == "__main__":
    main()