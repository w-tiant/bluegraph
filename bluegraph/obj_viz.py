import streamlit as st
import json
import os

def func(path: str) -> None:
    """
    path: 项目文件根目录
    调用后，显示vdb_entities.json的内容为可视化列表，并支持搜索。
    """
    json_path = os.path.join(path, 'vdb_entities.json')
    if not os.path.exists(json_path):
        st.error(f"未找到文件: {json_path}")
        return
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entities = data.get('data', [])

    search = st.text_input('搜索实体名或内容')
    if search:
        entities = [e for e in entities if search in e.get('entity_name', '') or search in e.get('content', '')]
    st.write(f"共 {len(entities)} 条记录")
    for e in entities:
        with st.expander(e.get('entity_name', '无名实体')):
            st.write(f"**内容**: {e.get('content', '')}")
            st.write(f"**ID**: {e.get('__id__', '')}")
            st.write(f"**创建时间**: {e.get('__created_at__', '')}")
            st.write(f"**来源ID**: {e.get('source_id', '')}")
            st.write(f"**文件路径**: {e.get('file_path', '')}")

if __name__ == "__main__":
    st.title('vdb_entities.json 可视化工具')
    path = st.text_input('请输入vdb_entities.json所在的根目录路径', value='.')
    # 用session_state记录是否已加载
    if 'loaded' not in st.session_state:
        st.session_state['loaded'] = False
    if st.button('加载并显示列表'):
        st.session_state['loaded'] = True
        st.session_state['path'] = path
    # 只要loaded为True就显示内容
    if st.session_state.get('loaded', False):
        func(st.session_state.get('path', path))
