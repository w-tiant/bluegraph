import streamlit as st
import os
import asyncio
from lightrag import QueryParam

# 你的其他模块导入
from .rag import main as rag_init
from .graph_viz import view as graph_viz
from .obj_viz import func as obj_viz
from .data_viz import func as data_viz

def main():
    st.set_page_config(layout="wide", page_title="BlueGraph - 交互式阅读图谱")
    st.title('BlueGraph')

    # 使用 session_state 管理核心状态
    if 'rag_instance' not in st.session_state:
        st.session_state.rag_instance = None
    if 'project_path' not in st.session_state:
        st.session_state.project_path = None
    if 'uploaded_file_names' not in st.session_state:
        st.session_state.uploaded_file_names = []
    if 'graph_generated' not in st.session_state:
        st.session_state.graph_generated = False

    # --- 文件上传区 (仅在项目未初始化时显示) ---
    if not st.session_state.rag_instance:
        st.header("步骤 1: 上传文档以创建项目")
        uploaded_files = st.file_uploader(
            "选择一个或多个文档",
            type=['txt', 'md', 'docx', 'pdf'],
            accept_multiple_files=True
        )

        if uploaded_files:
            if st.button("创建项目"):
                with st.spinner("正在创建工作目录并初始化引擎..."):
                    temp_dir = "temp_project"
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    
                    file_names = []
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_names.append(uploaded_file.name)
                    
                    # 初始化 RAG，但不处理文件
                    st.session_state.rag_instance = rag_init(temp_dir)
                    st.session_state.project_path = temp_dir
                    st.session_state.uploaded_file_names = file_names
                
                st.success("项目已创建！请前往 '解析文本' 标签页生成图谱。")
                st.rerun()

    # --- 主功能区 (项目创建后显示) ---
    if st.session_state.rag_instance:
        rag = st.session_state.rag_instance
        path = st.session_state.project_path

        tab_list = ['解析文本', '关系图', '智能查询', '对象列表', '原文']
        insert_tab, graph_tab, query_tab, obj_tab, origin_tab = st.tabs(tab_list)

        with insert_tab:
            st.header("步骤 2: 解析文件并生成知识图谱")
            
            st.markdown("项目已上传以下文件:")
            for name in st.session_state.uploaded_file_names:
                st.write(f"- `{name}`")
            
            st.markdown("---")
            
            # 如果图谱还未生成，显示生成按钮
            if not st.session_state.graph_generated:
                st.warning("知识图谱尚未生成。")
                if st.button("开始生成图谱", type="primary"):
                    with st.spinner("正在处理文档并构建知识图谱，这可能需要一些时间..."):
                        try:
                            # 准备文件路径列表
                            file_paths_to_process = [os.path.join(path, name) for name in st.session_state.uploaded_file_names]
                            
                            # 调用 insert 方法
                            asyncio.run(rag.insert(documents=file_paths_to_process))
                            
                            st.session_state.graph_generated = True
                            st.success("知识图谱生成成功！现在可以切换到 '关系图' 标签页查看。")
                            # st.rerun() # 可以选择刷新一下，让按钮消失

                        except Exception as e:
                            st.error("生成图谱时发生严重错误！")
                            st.exception(e)
            else:
                st.success("知识图谱已生成。您可以前往其他标签页进行探索。")


        with graph_tab:
            if not st.session_state.graph_generated:
                st.info("请先在 '解析文本' 标签页中生成图谱。")
            else:
                graph_viz(path)

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
        
        # ... obj_tab 和 origin_tab 也可以加上类似的检查 ...
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