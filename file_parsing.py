# -*- coding: utf-8 -*-
# time: 2022/10/17 15:04
# file: file_parsing.py

import json
import requests
from flask import Flask, request, render_template, jsonify, session
from docx import Document
from docx.shared import Inches
import os
import pdfplumber

app = Flask(__name__)
import requests
import fitz
import shutil
import cv2
import paddlehub as hub
import traceback

# 加载移动端预训练模型
ocr = hub.Module(name="chinese_ocr_db_crnn_mobile")



def ocr_result(image_path):
    np_images = [cv2.imread(image_path)]
    results = ocr.recognize_text(
    images=np_images,  # 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
    use_gpu=False,  # 是否使用 GPU；若使用GPU，请先设置CUDA_VISIBLE_DEVICES环境变量
    output_dir='ocr_result',  # 图片的保存路径，默认设为 ocr_result；
    visualization=True,  # 是否将识别结果保存为图片文件；
    box_thresh=0.5,  # 检测文本框置信度的阈值；
    text_thresh=0.5)  # 识别中文文本置信度的阈值；
    text=[]
    for result in results:
        data = result['data']
        save_path = result['save_path']
        for infomation in data:
            text.append(infomation['text'])
    text="".join(text)
    return text

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def file_translate(file_path):
    try:
        file=file_path.split("/")[-1]
        file_name = file.split(".")[0]
        file_type = file.split(".")[-1]
        if file_type in ["docx", "doc"]:
            document = Document(file_path)
            text = ""
            for paragraph in document.paragraphs:
                text += paragraph.text
            text = text.replace("\n", "").replace(" ", "")
            return text

        elif file_type.lower() in ["jpg","jpeg","bmp","png"]:
            text=ocr_result(file_path)
            return text

        elif file_type == "pdf":
            pdf = pdfplumber.open(file_path)
            text = ""
            for page in pdf.pages:
                # 获取当前页面的全部文本信息，包括表格中的文字
                text += page.extract_text()
            text = text.replace("\n", "").replace(" ", "")

            if text != "":
                return text
            elif text == "":
                file_save = "static/ocr_files/"
                isExists = os.path.exists(file_save)
                # 判断结果
                if not isExists:
                    os.makedirs(file_save)

                pdf = fitz.open(file_path)
                print(pdf.pageCount)
                text = ''
                for pg in range(pdf.pageCount):
                    page = pdf[pg]
                    rotate = int(0)
                    # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
                    # 此处若是不做设置，默认图片大小为：792X612, dpi=96
                    zoom_x = 1.33333333  # (1.33333333-->1056x816)   (2-->1584x1224)
                    zoom_y = 1.33333333
                    mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
                    pix = page.getPixmap(matrix=mat, alpha=False)

                    file_isExists = os.path.exists("static/ocr_files/" + file_name)
                    # 判断结果
                    if not file_isExists:
                        os.makedirs("static/ocr_files/" + file_name)

                    pix.writePNG("static/ocr_files/" + file_name + "/" + '%s.PNG' % pg)
                    response = ocr_result("static/ocr_files/" + file_name + "/" + '%s.PNG' % pg)
                    text +=response
                return text
    except:
        print(traceback.print_exc())
        text="未提取出内容"

if __name__=="__main__":
    # print(file_translate('tempDir/test1.docx'))
    # print(file_translate('tempDir/1.jpeg'))
    print(file_translate("img/1.jpeg"))
