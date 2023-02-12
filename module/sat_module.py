from matplotlib.lines import lineStyles
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import lagrange
import scipy.interpolate as scipl

# 数値を分割してラグランジュ


def sat_apply(ref_s, sub_s, ref_h, sub_h):
    div = 4
    step = int(180/(div-1))

    sub_s = np.nan_to_num(sub_s)
    ref_s = np.nan_to_num(ref_s)

    ref_s_d_min = ref_s[np.where(np.logical_and(ref_h >= 0, ref_h < step/2))]
    ref_s_d_max = ref_s[np.where(
        np.logical_and(ref_h >= 180-step/2, ref_h < 180))]
    sub_s_d_min = sub_s[np.where(np.logical_and(sub_s >= 0, sub_s < step/2))]
    sub_s_d_max = sub_s[np.where(
        np.logical_and(sub_s >= 180-step/2, sub_s < 180))]

    if ref_s_d_max.size == 0 or ref_s_d_min.size == 0 or sub_s_d_max.size == 0 or sub_s_d_min.size == 0:
        ymm = 0
    else:
        isSameRefMin = np.all(ref_s_d_min == ref_s_d_min[0])
        isSameRefMax = np.all(ref_s_d_max == ref_s_d_max[0])
        isSameSubMin = np.all(sub_s_d_min == sub_s_d_min[0])
        isSameSubMax = np.all(sub_s_d_max == sub_s_d_max[0])

        if isSameRefMin:
            ref_s_min = ref_s_d_min[0]
        else:
            ref_s_min = np.nanmin(ref_s[np.where(np.logical_and(
                ref_h >= 0, ref_h < step/2))])
        if isSameRefMax:
            ref_s_max = ref_s_d_max[0]
        else:
            ref_s_max = np.nanmax(ref_s[np.where(np.logical_and(
                ref_h >= 180-step/2, ref_h < 180))])
        ref_s_mm = np.nanmax((ref_s_min+ref_s_max))

        if isSameSubMin:
            sub_s_min = sub_s_d_min[0]
        else:
            sub_s_min = np.nanmin(sub_s[np.where(np.logical_and(
                sub_h >= 0, sub_h < step/2))])
        if isSameSubMax:
            sub_s_max = sub_s_d_max[0]
        else:
            sub_s_max = np.nanmax(sub_s[np.where(np.logical_and(
                sub_h >= 180-step/2, sub_h < 180))])
        sub_s_mm = np.nanmean((sub_s_min+sub_s_max))

        # 倍率
        try:
            ymm = int(ref_s_mm)/int(sub_s_mm)
        except ZeroDivisionError:
            ymm = 0

    x = [0]
    y = [ymm]

    for i in range(step, 180, step):
        # ------ 一定範囲のsubとref ------
        ref_s_range = ref_s[np.where(
            np.logical_and(ref_h >= i-step, ref_h < i+step))]
        sub_s_range = sub_s[np.where(
            np.logical_and(sub_h >= i-step, sub_h < i+step))]

        # ------ subの上下限値の計算 ------
        q = 10
        q_high, q_low = np.percentile(sub_s_range, [100-q, q])

        # ------ 色相区切りの彩度の平均 ------
        sub_s_mean = sub_s_range.mean()

        # ------ subの四分位範囲の下限と上限を元にカットしたrefの色相区切りの彩度の平均 ------
        ref_s_range_q = ref_s_range[np.where(np.logical_and(
            ref_s_range > q_low, ref_s_range < q_high))]
        if ref_s_range_q.size == 0:
            ad_s = 0
        else:
            ref_s_mean = np.nanmean(ref_s_range_q)
            ad_s = np.divide(ref_s_mean, sub_s_mean, out=np.zeros_like(
                ref_s_mean), where=ref_s_mean != 0)

        x.append(i)
        y.append(ad_s)

    x.append(180)
    y.append(ymm)

    y = np.nan_to_num(y)
    y = y.tolist()

    # 分割した領域の点からラグランジュで全ての点の動きを計算
    # 0~180の配列
    lag_s = np.linspace(0, 180, num=181, dtype=np.int16)

    # スプライン補間
    lag = scipl.CubicSpline(x, y)
    LUT = lag(lag_s)

    # オーバーフロー対策
    sub_s = sub_s.astype(np.int16)
    for i in range(181):
        if (sub_s[np.where(sub_h == i)].size != 0):
            # 適用前に、確認のため計算値を取得
            sub_s_lut = sub_s[np.where(sub_h == i)]*LUT[i]

            # 色相iの彩度値の最大値・最小値
            sub_s_lut_max = np.max(sub_s_lut)
            sub_s_lut_min = np.min(sub_s_lut)

            # 差分 計算後の値を min-max→を0-255 に圧縮
            # 計算後の最小値と最大値が異なり、最小値と最大値が同時に0を下回る、255を上回ることがない時、適用
            if (sub_s_lut_min != sub_s_lut_max):
                a = sub_s_lut_min
                b = sub_s_lut_max

                # ともに0-255の範囲に収まる場合 → 実際に代入
                if ((a >= 0 and a <= 255) and (b >= 0 and b <= 255)):
                    sub_s[np.where(sub_h == i)] = sub_s_lut
                # どちらかの値が0-255の範囲をはみ出す場合（どちらもは除く） → 代入後、圧縮
                elif (a >= 0 and b > 255):
                    sub_s[np.where(sub_h == i)] = np.interp(
                        sub_s_lut, (a, b), (a, 255))
            else:
                sub_s[np.where(sub_h == i)] = sub_s_lut

    sub_s = sub_s.astype(np.uint8)

    return sub_s
