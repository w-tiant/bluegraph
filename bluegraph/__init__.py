import streamlit as st
import tkinter as tk
from tkinter import filedialog
from lightrag import QueryParam

from .rag import main as rag_init
from .muti_input import muti_input
from .graph_viz import view as graph_viz
from .obj_viz import func as obj_viz
from .data_viz import func as data_viz

def main():
    st.set_page_config(layout="wide", page_title="交互式阅读图谱")
    st.title('BlueGraph')
    file_selector = st.empty()
    # Set up tkinter
    root = tk.Tk()
    root.withdraw()

    # Make folder picker dialog appear on top of other windows
    root.wm_attributes('-topmost', 1)

    # Folder picker button
    with file_selector.container():
        st.markdown('请选择文件夹')
        clicked = st.button('Folder Picker')

    if clicked:
        path = filedialog.askdirectory(master=root)
        rag = rag_init(path)
        file_selector.title('正在创建项目文件')
        file_selector.empty()

        @st.fragment
        def fragment():
            refresh = st.button('刷新')
            insert_tab, graph_tab, query_tab, obj_tab, origin_tab = st.tabs(
                ['解析文本', '关系图', '智能查询', '对象列表', '原文']
            )
            with insert_tab:
                st.title('选择文件')
                def after(res):
                    st.title('正在处理')
                    rag.insert(res)
                    st.text('完成！')
                muti_input(after)

            with graph_tab:
                graph_viz(path)

            with query_tab:
                st.title('智能查询')
                prompt = st.text_input('输入任何问题')
                if st.button('查询'):
                    st.text(rag.query(prompt, param=QueryParam(mode="naive")))

            with obj_tab:
                obj_viz(path)

            with origin_tab:
                data_viz(path)
            if refresh:
                st.rerun(scope='fragment')
        fragment()


if __name__ == "__main__":
    main()