import streamlit as st
import json
import os

def func(path: str) -> None:
    """
    path: 项目文件根目录
    调用后，显示kv_store_doc_status.json的内容为可视化列表。
    """
    json_path = os.path.join(path, 'kv_store_doc_status.json')
    if not os.path.exists(json_path):
        st.error(f"未找到文件: {json_path}")
        return
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    st.write(f"共 {len(data)} 个文档")
    search = st.text_input('搜索文档ID或内容摘要')
    filtered = []
    for doc_id, info in data.items():
        if not search or search in doc_id or search in info.get('content_summary', ''):
            filtered.append((doc_id, info))
    for doc_id, info in filtered:
        with st.expander(f"文档ID: {doc_id}"):
            st.write(f"**状态**: {info.get('status', '')}")
            st.write(f"**分块数**: {info.get('chunks_count', '')}")
            st.write(f"**内容摘要**: {info.get('content_summary', '')}")
            st.write(f"**内容长度**: {info.get('content_length', '')}")
            st.write(f"**创建时间**: {info.get('created_at', '')}")
            st.write(f"**更新时间**: {info.get('updated_at', '')}")
            st.write(f"**文件路径**: {info.get('file_path', '')}")
            st.text_area('完整内容', info.get('content', ''), height=200)

if __name__ == "__main__":
    st.title('kv_store_doc_status.json 可视化工具')
    path = st.text_input('请输入kv_store_doc_status.json所在的根目录路径', value='.')
    if 'loaded' not in st.session_state:
        st.session_state['loaded'] = False
    if st.button('加载并显示列表'):
        st.session_state['loaded'] = True
        st.session_state['path'] = path
    if st.session_state.get('loaded', False):
        func(st.session_state.get('path', path))