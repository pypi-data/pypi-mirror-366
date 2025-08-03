# -*- coding: utf-8 -*-
"""
 @Author: xiaoxuan6
 @Date: 2025/8/3 13:32
 @File: operation.py
 @Description: 计算数字运算结果
"""
import ddddocr
from PIL import Image

ocr = ddddocr.DdddOcr(show_ad=False)


def operation(img):
    if not isinstance(img, (bytes, str, Image.Image)):
        raise TypeError("未知图片类型")

    global total
    text = ocr.classification(img, png_fix=True)
    #  图片有干扰
    text = text.replace('F', '+')

    sign_seq = text.find('=')
    if sign_seq > 0:
        sub_text = text[:sign_seq]
    else:
        sign_seq = text.find('三')
        if sign_seq > 0:
            sub_text = text[:sign_seq]
        else:
            sign_seq = text.find('？')
            if sign_seq > 0:
                sub_text = text[:sign_seq]
            else:
                sign_seq = text.find('一')
                if sign_seq > 0:
                    sub_text = text[:sign_seq]
                else:
                    sub_text = text

    if not any(sign in sub_text for sign in ['x', '*', '/', '十', '+', '-', '一']):
        print("不包含运算符号")
        return ''

    for sign in ['x', '*', '/', '十', '+', '-', '一']:
        result = sub_text.find(sign)
        if result > 0:
            sp_arr = sub_text.split(sign)

            if '-' in sp_arr[1]:
                sub = int(sp_arr[1][:sp_arr[1].find('-')])
            else:
                sub = int(sp_arr[1])

            prefix = int(sp_arr[0])

            match sign:
                case '+' | '十':
                    total = prefix + sub
                case '-':
                    total = prefix - sub
                case '*' | 'x':
                    total = prefix * sub
                case '/':
                    total = prefix / sub
            break

    return total
