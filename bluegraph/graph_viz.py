import streamlit as st
import networkx as nx
import os
from pyvis.network import Network
import pandas as pd
import json

def create_html(net):
    """返回用于嵌入的 HTML 内容"""
    html_content = net.generate_html()
    return html_content

def st_net(html_content, height=800):
    """展示 pyvis 网络"""
    # 确保 HTML 内容是安全的，并使其自适应 streamlit 的宽度
    html = f"""
    <div style="width: 100%; height: {height}px; overflow: hidden; border: 1px solid #ddd; border-radius: 5px;">
        {html_content}
    </div>
    """
    st.components.v1.html(html, height=height+20)

def node_tip(data):
    """根据节点的属性创建工具提示"""
    tip = ""
    
    if 'entity_id' in data:
        tip += f"{data['entity_id']}\n"
    
    if 'description' in data:
        tip += f"{data['description']}\n"
    
    if 'entity_type' in data:
        tip += f"类型: {data['entity_type']}"
    
    return tip

def edge_tip(data):
    """根据边的属性创建工具提示"""
    tip = ""
    
    if 'description' in data:
        tip += f"{data['description']}\n"
    
    if 'keywords' in data:
        tip += f"关键词: {data['keywords']}"
    
    return tip

def set_physics_options(net, spring_length=90, central_gravity=0.3):
    """设置物理引擎选项"""
    physics_options = {
                    "physics": {
                        "barnesHut": {
                            "gravitationalConstant": -1000,
                            "centralGravity": central_gravity,
                            "springLength": spring_length,
                            "springConstant": 0.04,
                            "damping": 0.09,
                            "avoidOverlap": 0.5
                        },
                        "maxVelocity": 50,
                        "minVelocity": 0.1,
                        "solver": "barnesHut",
                        "stabilization": {
                            "enabled": True,
                            "iterations": 1000,
                            "updateInterval": 100,
                            "onlyDynamicEdges": False,
                            "fit": True
                        },
                        "timestep": 0.2,
                        "adaptiveTimestep": True
                    }
                }
    # 将物理选项转为 JSON 字符串
    net.set_options(json.dumps(physics_options))
    return net

def assign_colors(G):
    """为每种类型的节点分配颜色"""
    color_list = ['#F38181', '#FCE38A', '#A1EAFB', '#C8F4DE', 
                  '#FFB6B9', '#EAFFD0', '#FFCEF3']
    
    node_types = {}
    for node_id, data in G.nodes(data=True):
        entity_type = data.get('entity_type', 'unknown')
        if entity_type not in node_types:
            node_types[entity_type] = []
        node_types[entity_type].append(node_id)
    
    type_to_color = {}
    color_idx = 0
    for entity_type, nodes in node_types.items():
        color = color_list[color_idx % len(color_list)]  # 循环使用颜色
        for node_id in nodes:
            type_to_color[node_id] = color
        color_idx += 1

    return type_to_color

def node_size(G):
    """为每个节点分配大小"""
    node_sizes = {}
    for node_id, data in G.nodes(data=True):
        node_size = 10 + G.degree[node_id]  # 节点的大小和度数成比例
        node_sizes[node_id] = node_size
    return node_sizes

def viz_graph(graphml_path, height=800, physics=True):
    """可视化 .graphml 文件并返回交互式网络"""
    if os.path.exists(graphml_path):
        try:
            G = nx.read_graphml(graphml_path)
            node_colors = assign_colors(G)
            node_sizes = node_size(G)

            # 创建 Pyvis 网络
            net = Network(height=f"{height}px", width="100%", bgcolor="#3E4149", 
                        font_color="white", directed=False, 
                        cdn_resources="in_line")

            if physics:
                net = set_physics_options(net)
            
            for node_id in G.nodes():
                node_data = G.nodes[node_id]
                size = node_sizes.get(node_id, 10)  # 默认大小为 20
                color = node_colors.get(node_id, '#00ffff')  # 默认颜色为 #00ffff
                shape = "dot"

                title = node_tip(node_data)
                
                # 添加节点
                net.add_node(node_id,
                            size=size,
                            label=node_id,
                            title=title, 
                            shape=shape,
                            color=color
                            )
            
            # 添加边
            for source, target, edge_data in G.edges(data=True):
                weight = float(edge_data.get('weight', 1.0))
                
                title = edge_tip(edge_data)
                width = 1 + (weight / 7)
                
                net.add_edge(source, target, title=title, width=width, 
                            weight=weight)
            
            # 生成 HTML
            html_content = create_html(net)
            return html_content, G
        except Exception as e:
            st.error(f"处理图形时出错: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return None, None
    else:
        st.error(f"文件 '{graphml_path}' 未找到!")
        return None, None

def view(path):
    st.title("交互式阅读图谱")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("图谱视图")
        
        # 提供默认路径或允许用户上传
        
        graphml_path = None
        G = None
        
        graphml_path = os.path.join(path, "graph_chunk_entity_relation.graphml")
        # 检查路径是否存在
        if not os.path.exists(graphml_path):
            st.warning(f"File not found: {graphml_path}")
            st.info("请检查默认路径！")
            graphml_path = None
        
        if graphml_path:
            # 物理引擎参数
            physics_enabled = st.checkbox("启用物理引擎", value=True)
            height = st.slider("图形高度", min_value=400, max_value=1200, value=800, step=100)
            
            html_content, G = viz_graph(graphml_path, height=height, physics=physics_enabled)
            
            if html_content:
                try:
                    st_net(html_content, height=height)
                except Exception as e:
                    st.error(f"显示图形时出错: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
    
    if G:
        with col2:
            st.header("图谱信息")
            
            st.subheader("基本信息")
            st.markdown(f"**节点数量:** {G.number_of_nodes()}")
            st.markdown(f"**连接数量:** {G.number_of_edges()}")
            
            # 展示实体类型统计
            st.subheader("实体类型分布")
            entity_types = {}
            for node_id, data in G.nodes(data=True):
                entity_type = data.get('entity_type', 'unknown')
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

            # 创建实体类型数据框
            entity_df = pd.DataFrame({
                '实体类型': list(entity_types.keys()),
                '数量': list(entity_types.values())
            })
            st.dataframe(entity_df)
            
            # 展示节点列表
            st.subheader("节点列表")
            node_data = []
            for node_id, data in G.nodes(data=True):
                entity_type = data.get('entity_type', '-')
                description = data.get('description', '-')
                # 截断过长的描述
                if description and len(description) > 50:
                    description = description[:50] + "..."
                
                node_data.append({
                    '节点ID': node_id,
                    '类型': entity_type,
                    '描述': description
                })
            
            node_df = pd.DataFrame(node_data)
            st.dataframe(node_df)
            
            # 展示边列表
            st.subheader("关系列表")
            edge_data = []
            for source, target, data in G.edges(data=True):
                weight = data.get('weight', '-')
                description = data.get('description', '-')
                # 截断过长的描述
                if description and len(description) > 50:
                    description = description[:50] + "..."
                
                edge_data.append({
                    '源节点': source,
                    '目标节点': target,
                    '权重': weight,
                    '描述': description
                })
            
            edge_df = pd.DataFrame(edge_data)
            st.dataframe(edge_df)

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="交互式阅读图谱")
    view()
