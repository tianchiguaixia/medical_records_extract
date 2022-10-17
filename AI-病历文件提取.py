# -*- coding: utf-8 -*-
# time: 2022/10/17 15:03
# file: AI-病历文件提取.py


import streamlit as st
import requests
import streamlit.components.v1 as components
from spacy import displacy
from file_parsing import *
from paddlenlp import Taskflow

st.set_page_config(
    page_title="关键元素抽取",
    page_icon="🧊",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title("# 病例文件提取 👋\n")

uploaded_file = st.file_uploader("支持图片，pdf，扫描件，word文件等信息提取")
if uploaded_file is not None:
    with open(os.path.join("tempDir", uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    text=file_translate("tempDir"+"/"+uploaded_file.name)


col1, col2 = st.columns(2)
with col1:
    if uploaded_file is not None:
        with st.form(key="my_form"):
            example_schema="疾病;药品;年龄;性别"
            schema_inputs = st.text_input(label="输入模板", value=example_schema)
            submit_button = st.form_submit_button(label="✨ 启动!")


        if not submit_button:
            st.stop()
        else:
            schema = schema_inputs.split(";")
            ie_model = Taskflow('information_extraction', schema=schema)
            try:
                results = ie_model(text)[0]
                standard_list = []
                # [{"start": 4, "end": 10, "label": "ORG"}],
                for i,j in results.items():
                    tmp_dict = {}
                    tmp_dict["start"] = j[0]["start"]
                    tmp_dict["end"] = j[0]["end"]
                    tmp_dict["label"] = i
                    standard_list.append(tmp_dict)

                doc = [{
                    "text": text,
                    "ents": standard_list,
                    "title": None
                }]

                html = displacy.render(doc, style="ent", manual=True)
                components.html(html, width=350, height=2000, scrolling=True)
            except:
                pass

with col2:
    try:
        if uploaded_file is not None:
            st.title("内容提取")
            st.write("\n"*3)
            for element in standard_list:
                st.write(element["label"])
                st.info(text[element["start"]:element["end"]])
    except:
        pass
