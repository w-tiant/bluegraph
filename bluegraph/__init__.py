import streamlit as st
import os
import asyncio
from lightrag import QueryParam

# 你的其他模块导入
from .rag import main as rag_init
from .muti_input import muti_input  # 我们现在假设这个模块也需要被替换
from .graph_viz import view as graph_viz
from .obj_viz import func as obj_viz
from .data_viz import func as data_viz

# --- 替换 muti_input ---
# 由于 muti_input 很可能也依赖 tkinter，我们用一个简单的 Streamlit 组件来替代它
# 这个新函数的功能等同于你原始流程中的“第二次文件选择”
def web_muti_input(callback_func):
    """
    一个用 Streamlit 实现的 muti_input 替代品。
    它提供一个文件上传器和一个按钮，点击按钮后，将选中的文件路径列表传给回调函数。
    """
    st.subheader("步骤 2: 选择要解析的文件")
    files_to_insert = st.file_uploader(
        "从项目中选择文件进行解析",
        accept_multiple_files=True,
        type=['txt', 'md', 'docx', 'pdf'],
        key="insert_uploader" # 使用 key 防止组件冲突
    )

    if st.button("开始解析选中的文件", type="primary"):
        if files_to_insert:
            # 获取上传文件的临时路径
            # 注意：这里我们不能直接用文件名，因为 rag.insert 需要的是已保存文件的路径
            # 我们需要从 session_state 中获取项目路径
            project_path = st.session_state.get('project_path', 'temp_project')
            
            # 构建所选文件的完整路径列表
            selected_file_paths = [os.path.join(project_path, f.name) for f in files_to_insert]
            
            # 调用你原始的回调函数
            callback_func(selected_file_paths)
        else:
            st.warning("请至少选择一个文件进行解析。")

# --- 核心 main 函数 ---
def main():
    st.set_page_config(layout="wide", page_title="交互式阅读图谱")
    st.title('BlueGraph')

    # 使用 session_state 来存储关键信息，这是云端应用必需的
    if 'rag_instance' not in st.session_state:
        st.session_state.rag_instance = None
    if 'project_path' not in st.session_state:
        st.session_state.project_path = None

    # --- 步骤 1: 创建项目 (替代你的 tkinter 文件夹选择) ---
    # 只有当项目未创建时，才显示这部分
    if not st.session_state.rag_instance:
        st.header("步骤 1: 上传文档以创建项目")
        st.info("在这里上传的文件将定义项目的工作目录和可用文件。")
        
        uploaded_files = st.file_uploader(
            "选择一个或多个初始文档",
            accept_multiple_files=True,
            type=['txt', 'md', 'docx', 'pdf'],
            key="initial_uploader"
        )

        if uploaded_files and st.button("创建项目", type="primary"):
            with st.spinner("正在创建工作目录并初始化引擎..."):
                temp_dir = "temp_project"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # 完全等同于你本地的 rag = rag_init(path)
                st.session_state.rag_instance = rag_init(temp_dir)
                st.session_state.project_path = temp_dir
            
            st.success("项目已创建！")
            st.rerun() # 刷新页面以显示主功能区

    # --- 主功能区 (项目创建后显示，完全模拟你的 fragment 结构) ---
    if st.session_state.rag_instance:
        rag = st.session_state.rag_instance
        path = st.session_state.project_path
        
        # 你的原标签页结构
        insert_tab, graph_tab, query_tab, obj_tab, origin_tab = st.tabs(
            ['解析文本', '关系图', '智能查询', '对象列表', '原文']
        )
        with insert_tab:
            st.title('选择文件')
            
            # 定义你的 after 回调函数，和原始代码一模一样
            def after(res): # res 将会是一个文件路径列表
                st.info('正在处理...')
                try:
                    # 调用 insert，不带关键字参数！
                    asyncio.run(rag.insert(res))
                    st.success('完成！')
                except Exception as e:
                    st.error("处理文件时出错！")
                    st.exception(e)
            
            # 调用我们创建的 web_muti_input 来替代你原来的 muti_input
            web_muti_input(after)

        with graph_tab:
            graph_viz(path)

        with query_tab:
            st.title('智能查询')
            prompt = st.text_input('输入任何问题')
            if st.button('查询'):
                if prompt:
                    st.text(rag.query(prompt, param=QueryParam(mode="naive")))

        with obj_tab:
            obj_viz(path)

        with origin_tab:
            data_viz(path)


if __name__ == "__main__":
    main()
    