import numpy as np
# from matplotlib.lines import lineStyles
import matplotlib.pyplot as plt
# from scipy.interpolate import lagrange
import scipy.interpolate as scipl


def hue_apply(ref_h, sub_h):
    div_hue = 6
    step = int(180/div_hue)

    x = []
    y = []

    for i in range(0, 180, step):

        ref_h_d = ref_h[np.where(np.logical_and(ref_h >= i, ref_h < i+step))]
        sub_h_d = sub_h[np.where(np.logical_and(sub_h >= i, sub_h < i+step))]

        if ref_h_d.size == 0:
            ad_h = 0
        else:
            # 全てが同値の場合
            isSameRef = np.all(ref_h_d == ref_h_d[0])
            isSameSub = np.all(sub_h_d == sub_h_d[0])

            # ある範囲の色相の平均値, 最大値, 最小値
            if isSameRef:
                ref_h_mean = ref_h_max = ref_h_min = ref_h_d[0]
            else:
                ref_h_mean = np.nanmean(ref_h_d)
                ref_h_max = np.nanmax(ref_h_d)
                ref_h_min = np.nanmin(ref_h_d)

            if isSameSub:
                sub_h_mean = sub_h_max = sub_h_min = sub_h_d[0]
            else:
                sub_h_mean = np.nanmean(sub_h_d)
                sub_h_max = np.nanmax(sub_h_d)
                sub_h_min = np.nanmin(sub_h_d)

            # 平均値から求めたズレているであろう色相の角度
            ad_h = int(ref_h_mean) - int(sub_h_mean)

            if (ref_h_min != 0 or ref_h_max != 0 or sub_h_min != 0 or sub_h_max != 0):
                # ある範囲におけるrefとsubの持つ幅
                try:
                    h_range = int(ref_h_max-ref_h_min)/int(sub_h_max-sub_h_min)
                except ZeroDivisionError:
                    h_range = 1

                # h_rangeをもとにした色相のずれ値
                try:
                    ad_h /= h_range
                except ZeroDivisionError:
                    ad_h = ad_h

        sub_h[np.logical_and(sub_h >= i, sub_h < i+step)] = np.clip(
            sub_h[np.logical_and(sub_h >= i, sub_h < i+step)]+ad_h, i, i+step)

        x.append(i+step/2)
        y.append(ad_h)

    x.append(180)
    y.append((y[0]+ad_h)/2)

    x.insert(0, 0)
    y.insert(0, (y[0]+ad_h)/2)

    y = np.nan_to_num(y)
    y = y.tolist()

    return sub_h
