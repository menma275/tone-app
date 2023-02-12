from math import gamma
import cv2
import numpy as np
from scipy.interpolate import lagrange
import scipy.interpolate as scipl


def val_apply(ref_v, sub_v):
    div = 5
    step = 255/div
    i = step
    x = [0]
    y = [ref_v.min()]

    for j in range(div-1):
        # ------ 一定範囲のsubとref ------
        sub_v_range = sub_v[np.where(
            np.logical_and(sub_v >= i-step, sub_v < i+step))]
        ref_v_range = ref_v[np.where(
            np.logical_and(ref_v >= i-step, ref_v < i+step))]

        # ------ subの上下限値の計算 ------
        q = 10
        sub_q_high, sub_q_low = np.percentile(sub_v_range, [100-q, q])

        # ------ step区切りの輝度の平均 ------
        sub_v_mean = sub_v_range.mean()

        # ------ subの外れ値を元に上下限をカットしたrefの平均 ------
        ref_v_mean = ref_v_range[np.where(np.logical_and(
            ref_v_range > sub_q_low, ref_v_range < sub_q_high))].mean()

        # ------ 取得した輝度の平均値からnun値を削除→0に ------
        sub_v_mean = np.nan_to_num(sub_v_mean)
        ref_v_mean = np.nan_to_num(ref_v_mean)

        # x=yのグラフの値に対して、ref画像の輝度値がどれだけずれているかを作成
        ad_v = np.divide(ref_v_mean, sub_v_mean, out=np.zeros_like(
            ref_v_mean), where=ref_v_mean != 0)

        ad_v_sub = np.clip(sub_v[np.logical_and(
            sub_v >= i-step, sub_v < i+step)].mean()*ad_v, 0, 255)

        x.append(i)
        y.append(ad_v_sub)
        i += step

    x.append(255)
    y.append(ref_v.max())

    # 分割した領域の点からラグランジュで全ての点の動きを計算
    # 0~256の配列
    lag_v = np.linspace(0, 255, num=256, dtype=np.int16)

    # ラグランジュ補間
    lag = scipl.CubicSpline(x, y)
    LUT = np.clip(lag(lag_v), 0, 255)

    gamma_LUT = np.zeros((256, 1), dtype=np.uint8)
    for i in range(256):
        gamma_LUT[i][0] = LUT[i]

    sub_v = cv2.LUT(sub_v, gamma_LUT)

    return sub_v
