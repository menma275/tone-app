import cv2
import numpy as np
from scipy.interpolate import lagrange
import scipy.interpolate as scipl


def rgb_apply(ref_rgb, sub_rgb, rgb):
    div = 4
    step = 255/div
    i = step
    x = [0]
    y = [ref_rgb.min()]

    for j in range(div-1):
        # ------ 一定範囲のsubとref ------
        sub_rgb_range = sub_rgb[np.where(np.logical_and(
            sub_rgb >= i-step, sub_rgb < i+step))]
        ref_rgb_range = ref_rgb[np.where(np.logical_and(
            ref_rgb >= i-step, ref_rgb < i+step))]

        # ------ subの上下限値の計算 ------
        q = 10
        sub_q_high, sub_q_low = np.percentile(sub_rgb_range, [100-q, q])

        # ------ step区切りの輝度の平均 ------
        sub_rgb_mean = sub_rgb_range.mean()

        # ------ subの外れ値を元に上下限をカットしたrefの平均 ------
        ref_rgb_mean = ref_rgb_range[np.where(np.logical_and(
            ref_rgb_range > sub_q_low, ref_rgb_range < sub_q_high))].mean()

        # ------ 取得した輝度の平均値からnun値を削除→0に ------
        sub_rgb_mean = np.nan_to_num(sub_rgb_mean)
        ref_rgb_mean = np.nan_to_num(ref_rgb_mean)

        # x=yのグラフの値に対して、ref画像の輝度値がどれだけずれているかを作成
        ad_rgb = np.divide(ref_rgb_mean, sub_rgb_mean, out=np.zeros_like(
            ref_rgb_mean), where=ref_rgb_mean != 0)

        ad_rgb_sub = np.clip(sub_rgb[np.logical_and(
            sub_rgb >= i-step, sub_rgb < i+step)].mean()*ad_rgb, 0, 255)

        x.append(i)
        y.append(ad_rgb_sub)
        i += step

    x.append(255)
    y.append(ref_rgb.max())

    # 分割した領域の点からラグランジュで全ての点の動きを計算
    # 0~256の配列
    lag_rgb = np.linspace(0, 255, num=256, dtype=np.int16)

    # スプライン補間
    lag = scipl.CubicSpline(x, y)
    LUT = np.clip(lag(lag_rgb), 0, 255)

    gamma_LUT = np.zeros((256, 1), dtype=np.uint8)
    for i in range(256):
        gamma_LUT[i][0] = LUT[i]

    sub_rgb = cv2.LUT(sub_rgb, gamma_LUT)
    return sub_rgb
