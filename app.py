# モジュールインポート-------------------------
from module.rgb_module import rgb_apply
from module.val_module import val_apply
from module.sat_module import sat_apply
from module.hue_module import hue_apply
import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from datetime import datetime as dt

app = Flask(__name__, static_url_path="")
bootstrap = Bootstrap(app)

# 処理した画像ファイルの保存先
IMG_DIR = "/static/images/"
BASE_DIR = os.path.dirname(__file__)
IMG_PATH = BASE_DIR + IMG_DIR

# 保存先のパスがなければ作成
if not os.path.isdir(IMG_PATH):
    os.mkdir(IMG_PATH)


# グレーディング
def ad_rgb(sub, ref):
    # 画像をR G Bに分割
    ref_r, ref_g, ref_b = cv2.split(ref)
    sub_r, sub_g, sub_b = cv2.split(sub)

    sub_r = rgb_apply(ref_r, sub_r, "r")
    sub_g = rgb_apply(ref_g, sub_g, "g")
    sub_b = rgb_apply(ref_b, sub_b, "b")

    sub_rgb = cv2.merge((sub_r, sub_g, sub_b))
    return sub_rgb


def ad_hsv(sub, ref):
    # 画像をH S Vに分割
    ref_hsv = cv2.cvtColor(ref, cv2.COLOR_BGR2HSV)
    ref_h, ref_s, ref_v = cv2.split(ref_hsv)

    sub_hsv = cv2.cvtColor(sub, cv2.COLOR_BGR2HSV)
    sub_h, sub_s, sub_v = cv2.split(sub_hsv)

    sub_s = sat_apply(ref_s, sub_s, ref_h, sub_h)
    sub_h = hue_apply(ref_h, sub_h)
    sub_v = val_apply(ref_v, sub_v)

    sub_hsv_m = cv2.merge((sub_h, sub_s, sub_v))
    sub_adj = cv2.cvtColor(sub_hsv_m, cv2.COLOR_HSV2BGR)

    return sub_adj


def blend(sub, rgb):
    SUB = cv2.cvtColor(sub, cv2.COLOR_BGR2HSV)
    sub_h, sub_s, sub_v = cv2.split(SUB)

    RGB = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    rgb_h, rgb_s, rgb_v = cv2.split(RGB)

    rate = np.nanmean(sub_s+sub_v)/np.nanmean(rgb_s+rgb_v)*0.5
    if rate > 1:
        rate = 1
    rgb = cv2.addWeighted(sub, rate, rgb, 1-rate, 0)

    return rgb


def adjust(ref, sub):
    rgb = ad_rgb(sub, ref)

    rgb = blend(sub, rgb)

    hsv = ad_hsv(rgb, ref)

    return hsv


@app.route('/', methods=['GET', 'POST'])
def index():
    ref_name = ""
    sub_name = ""
    result_name = ""

    if request.method == 'POST':
        # 画像をロード
        stream1 = request.files['image1'].stream
        stream2 = request.files['image2'].stream

        img_array1 = np.asarray(bytearray(stream1.read()), dtype=np.uint8)
        img_array2 = np.asarray(bytearray(stream2.read()), dtype=np.uint8)

        # 画像データ用配列にデータがあれば
        if len(img_array1) != 0 and len(img_array2) != 0:
            ref = cv2.imdecode(img_array1, 1)
            h, w = ref.shape[:2]
            width = round(w*(500/h))
            if h > 500:
                ref = cv2.resize(ref, dsize=(width, 500))
            sub = cv2.imdecode(img_array2, 1)
            # 色調変換
            result = adjust(ref, sub)
            now_date = dt.now()
            ref_name = "ref_" + now_date.strftime('%Y-%m-%d-%H-%M-%S') + ".jpg"
            sub_name = "sub_" + now_date.strftime('%Y-%m-%d-%H-%M-%S') + ".jpg"
            result_name = "result_" + \
                now_date.strftime('%Y-%m-%d-%H-%M-%S') + ".jpg"
            # 画像の保存
            cv2.imwrite(os.path.join(IMG_PATH + ref_name), ref)
            cv2.imwrite(os.path.join(IMG_PATH + sub_name), sub)
            cv2.imwrite(os.path.join(IMG_PATH + result_name), result)

    return render_template('index.html', ref_name=ref_name, sub_name=sub_name, result_name=result_name)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080)
