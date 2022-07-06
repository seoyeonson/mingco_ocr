import matplotlib.pyplot as plt
import cv2
import numpy as np
import io
import os
from google.cloud import vision
from collections import Counter
import re
from functools import reduce
from key_path import CREDENTIAL_PATH

class visionAPI():

    def __init__(self, path):
        self.path = path
        self.texts = None
        self.pills = None
        self.info_list = None
        self.img_out = None

        self.ocr_detect()
        self.search_pill(self.texts)
        self.out_img()

    def most_frequent_word(self, pack, line):
        temp_list = Counter(re.sub(r"[^가-힣]"," ", line[-1]).split()).most_common()
        if temp_list == []:
            return pack
        fr_word = temp_list[0][0]
        result = line[:-1]
        result.append(fr_word)
        pack.append(result)
        return pack

    # 구글 클라우드에서 
    def ocr_detect(self):
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIAL_PATH
        img_origin = cv2.imread(self.path)
        img_copy = img_origin.copy()

        height, width, channel = img_origin.shape
        
        client = vision.ImageAnnotatorClient()

        with io.open(self.path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)

        texts = response.text_annotations
        self.texts = texts

    def search_pill(self, texts):
        info_list = []
        pill_list = []
        pat = re.compile('.*처.*방.*전.*', re.DOTALL) # 처방전임을 나타내는 글자가 전체 문자열 중에 포함되어 있는지 판별하는 정규식
        crop_y = None
        
        cnt = 0
        for text in texts:
            if not(pat.match(texts[0].description)):
                print('처방전이 아닙니다')
                break
            if text == texts[0]: # text의 첫번째 인덱스는 인식한 문자열 전체. 건너뛰기
                continue
            if '의약품' in text.description:  # '의약품' 이라는 글자를 발견하면 해당 글자의 위치(y) 변수로저장
                crop_y = text.bounding_poly.vertices[0].y
            if crop_y and (text.bounding_poly.vertices[0].y > crop_y + 20):  # '의약품' 아래 위치한 글자들에 대해서만 처리
                word = re.sub(r"[^a-zA-Z0-9|가-힣|.]"," ",text.description)

                x = text.bounding_poly.vertices[0].x
                y = text.bounding_poly.vertices[0].y
                x2 = text.bounding_poly.vertices[2].x
                y2 = text.bounding_poly.vertices[2].y
                p1 = (x, y)
                p2 = (x2, y2)

                info_list.append({
                    'idx': cnt,
                    'word': word,
                    'xywh': (x, y, x2-x, y2-y)
                })
                pill_list.append(word)
                cnt += 1
            
        rows_dict = {1:[info_list[0]['idx'], info_list[0]['word']]}
        temp_y = 0
        temp_x = 0
        temp_row = 1
        for d in info_list:
            if d['idx'] == 0:
                temp_y = d['xywh'][1]
                temp_x = d['xywh'][0] + d['xywh'][2]
                continue

            if (abs(d['xywh'][1] - temp_y) < 10) and (abs(d['xywh'][0] - temp_x) < 50):
                if len(rows_dict[temp_row]) > 2:
                    rows_dict[temp_row][1] = d['idx']
                    rows_dict[temp_row][2] += d['word']

                else:
                    rows_dict[temp_row].insert(1, d['idx'])
                    rows_dict[temp_row][2] += d['word']

            else:
                temp_row += 1
                rows_dict[temp_row] = [d['idx'], d['word']]
                temp_y = d['xywh'][1]
            temp_x = d['xywh'][0] + d['xywh'][2]
        
        value_list = list(rows_dict.values())
        
        rst_list = reduce(self.most_frequent_word, value_list, [])
        
        self.info_list = info_list
        self.pills = rst_list
        
    def out_img(self):
        img_out = cv2.imread(self.path)
        for data in self.pills:
            p1 = self.info_list[data[0]]['xywh']
            p2 = self.info_list[data[1]]['xywh']
            x1 = p1[0]
            y1 = p1[1]
            x2 = p2[0] + p2[2]
            y2 = p2[1] + p2[3]

            cv2.rectangle(img_out, pt1=(x1, y1), pt2=(x2, y2), color=(0, 200, 200), thickness=1)
        self.img_out = img_out
        

            
            