import streamlit as st
import PyPDF2
import docx2txt
from io import BytesIO

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    return docx2txt.process(file)

def muti_input(after):
    # 文件上传器
    uploaded_file = st.file_uploader("请选择一个文件", type=['txt', 'md', 'markdown', 'pdf', 'docx'])
    content = ""
    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        try:
            # 根据文件类型提取文本
            if file_type in ['pdf']:
                content = extract_text_from_pdf(BytesIO(uploaded_file.getvalue()))
            elif file_type in ['doc', 'docx']:
                content = extract_text_from_docx(BytesIO(uploaded_file.getvalue()))
            else:  # txt, md, markdown
                content = uploaded_file.getvalue().decode("utf-8")
            # 显示文件信息
            st.subheader("文件信息：")
            st.write(f"文件名：{uploaded_file.name}")
            st.write(f"文件大小：{uploaded_file.size / 1024:.2f} KB")
            st.write("上传成功！")
            
        except Exception as e:
            st.error(f"处理文件时出错：{str(e)}")
        after(content)

#if __name__ == "__main__":
#   print(muti_input())