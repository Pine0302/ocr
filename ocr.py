from flask import Flask, request, jsonify
from paddleocr import PaddleOCR, draw_ocr
from datetime import datetime
import random
import base64
import os
import re
import logging

# 定义文件路径全局变量
BASE_FILE_PATH = '/home/pine/workspace/paddle/'
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(os.path.join(BASE_FILE_PATH,
                            "ocr.log"))
                      #  logging.StreamHandler()  # 控制台输出
                    ])

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.json
    if not data or 'image' not in data:
        logging.error("No image provided in request")
        return jsonify({'error': 'No image provided'}), 400
    
    image_data = data['image']
    try:
        # Assuming the image data is in the format "data:image/png;base64,iVBORw0KGgo..."
        header, encoded = image_data.split(",", 1)
        file_extension = header.split(';')[0].split('/')[1]
        image_bytes = base64.b64decode(encoded)
        # 生成时间戳和随机数的文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_number = random.randint(1000, 9999)
        file_name = f"uploaded_image/{timestamp}_{random_number}.{file_extension}"
        file_path = os.path.join(BASE_FILE_PATH, file_name)
        with open(file_path, 'wb') as file:
            file.write(image_bytes)
        logging.info(f"Image saved at {file_path}")    
        ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
        result = ocr.ocr(file_path, cls=True)
        logging.debug("OCR completed")
        for idx in range(len(result)):
            res = result[idx]
        # 提取文本
        texts = [item[1][0] for item in res]
        # 合并文本
        combined_text = ''.join(texts)
        logging.debug(f"Extracted Combined Text: {combined_text}")
        print(combined_text)
        # 定义正则表达式
        patterns = {
            "姓名": "姓名([\u4e00-\u9fa5]+)(?=性别)",
            "性别": "性别(男|女)",
            "民族": "民族([\u4e00-\u9fa5]+)(?=出生)",
            "出生": "出生(\d{4}年\d+月\d+日)",
            "住址": "住址(.*?)(?=公民身份号码|\d{17}|\d{18})",  # 调整住址匹配规则
            "公民身份号码": "公民身份号码(\d+[Xx]?)",
            "有效期限": "有效期限(\d{4}\.\d{2}\.\d{2}-\d{4}\.\d{2}\.\d{2})",
            "签发机关":
            "签发机关([\u4e00-\u9fa5]+(?:局|所))(?=有效期限|居民身份证|\d)"
        }
        # 提取信息
        info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, combined_text)
            if match:
                info[key] = match.group(1)
            else:
                info[key] = "未找到信息"
                logging.warning(f"Info not found for {key}")

        # 打印提取的信息
        for key, value in info.items():
            logging.info(f"{key}: {value}")
        return jsonify({'message': 'Image saved successfully', 'path':
            file_path,'info':info}), 200
    except Exception as e:
        logging.error(f"Error processing the image: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

