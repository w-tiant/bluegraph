# 项目说明
## 1. 部署
```bash
pip install -r requirements.txt
```
或者使用uv
```bash
uv add -r requirements.txt
```

## 2. 运行
```bash
streamlit run app.py
```
example目录中有已经生成好的样例可以用于测试。

## 3. 开源项目依赖说明
### 1. streamlit
+ 可视化以及文件传输

### 2. lightrag (HKU)
+ **GraphRAG** 的优化版本，用于实体提取和图的构建

### 3. **docx2txt** & **pypdf2**
+ 多文件格式的支持

## 4. 说明
+ 该 **lightrag** 版本是经过修改的版本。原版存在bug，无法运行。因此，请不要使用原版作为依赖。
+ 在分析文本时会大量调用api，api不稳定可能导致卡死。
+ 蓝心模型的上下文大小相对于其他模型差距太大，因此可能会导致多次重试（可能导致卡死），展示出的关系图可能连线较少。