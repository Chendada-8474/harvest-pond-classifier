import sys
import matplotlib.pyplot as plt
from classify_core_function import *
import json
from easygui import fileopenbox
import os


def on_press(event):
    global all_fp, sar_2d_array, train_data, s1, s2, s3

    if event.key == 'h':

        train_data["train_x"].append(sar_2d_array)
        train_data["train_y"].append(1)

        fp.loc[fp["FID"].map(lambda x: x == all_fp[0]), colname] = "h"

        print("index: %s harvested pond" % all_fp[0])
        s3 = s2
        s2 = s1
        s1 = all_fp[0]
        all_fp.pop(0)

    elif event.key == 'w':

        train_data["train_x"].append(sar_2d_array)
        train_data["train_y"].append(0)

        fp.loc[fp["FID"].map(lambda x: x == all_fp[0]), colname] = "f"

        print("index: %s full water pond" % all_fp[0])

        s3 = s2
        s2 = s1
        s1 = all_fp[0]

        all_fp.pop(0)

    elif event.key == 'u':
        fp.loc[fp["FID"].map(lambda x: x == all_fp[0]), colname] = "u"
        print("index: %s can not identify" % all_fp[0])

        s3 = s2
        s2 = s1
        s1 = all_fp[0]

        all_fp.pop(0)

    elif event.key == 'c':
        print("saving...")

        s1 = None
        s2 = None
        s3 = None

        with open("./train_data.json", "r") as f:
            old_train_data = json.load(f)

        old_train_data["train_x"].extend(list(train_data["train_x"]))
        old_train_data["train_y"].extend(list(train_data["train_y"]))


        with open('./train_data.json', 'w') as f:
            json.dump(old_train_data, f)

        train_data = {
            "train_x": [],
            "train_y": [],
            }

        fp.to_file(fp_path)
        print("changes saved")
        return

    elif event.key == "z":

        if not s1:
            print("no more zzzzzzzzzzzzzzzzzz")
            return

        all_fp.insert(0, s1)
        s1 = s2
        s2 = s3
        s3 = None

        fp.loc[fp["FID"].map(lambda x: x == all_fp[0]), colname] = None
        train_data["train_x"].pop()
        train_data["train_y"].pop()

        print("return")

    else:
        return

    sys.stdout.flush()
    ax[0].clear()
    ax[1].clear()
    ax[2].clear()

    sar_fn = get_filename(sar_path, fp_path, all_fp[0])
    rgb_fn = get_filename(rgb_path, fp_path, all_fp[0])
    ndwi2_fn = get_filename(ndwi2_path, fp_path, all_fp[0])

    fps, cut_sar, cut_rgb, cut_ndwi2, sar_2d_array = plot_fp_s2_ndwi2(fp["geometry"][all_fp[0]], sar, rgb, ndwi2, sar_fn, rgb_fn, ndwi2_fn)

    p_sar = rasterio.plot.show(cut_sar, ax=ax[0], cmap='Spectral_r', vmin = -30, vmax = 0.5, title = "sar")
    p_ndwi2 = rasterio.plot.show(cut_ndwi2, ax=ax[1], cmap='Spectral', vmin = -1, vmax = 1, title = "ndwi2")
    p_rgb = rasterio.plot.show(cut_rgb.read(), transform = cut_rgb.transform, ax=ax[2], title = "RGB")

    fps.plot(color = "white", ax = p_sar)
    fps.plot(color = "white", ax = p_ndwi2)
    fps.plot(color = "white", ax = p_rgb)

    fig.canvas.draw()

    cut_sar.close()
    cut_rgb.close()
    cut_ndwi2.close()


print("不知道會什麼預設會是中文輸入法\n使用前請先改成英文輸入法")

this_pc = os.environ['COMPUTERNAME']
if this_pc == "HAB-21-262":
    fp_path = "./sha/demo_ponds_5000m2.shp"
    sar_path = "./tiff/Subset_S1A_IW_GRDH_1SDV_20211210.tif"
    rgb_path = "./tiff/S2A_MSIL2A_20211211T023111_N0301_R046_T50QRL_20211211T045314_RGB2.tif"
    ndwi2_path = "./tiff/20211211 NDWI2_TWD97.tif"

else:
    fp_path = fileopenbox(msg = "請選擇魚塭 shapefile 檔")
    sar_path = fileopenbox(msg = "請選擇 sar tif 檔")
    rgb_path = fileopenbox(msg = "請選擇魚塭 rgb tif 檔")
    ndwi2_path = fileopenbox(msg = "請選擇魚塭 ndwi2 tif 檔")


fp = gpd.read_file(fp_path)
sar = rasterio.open(sar_path)
rgb = rasterio.open(rgb_path)
ndwi2 = rasterio.open(ndwi2_path)

train_data = {
    "train_x": [],
    "train_y": [],
}

colname = sar_path.split("_")[-1][:-4]

if colname not in fp.columns:
    fp[colname] = None
    fp.to_file(fp_path)

fp0 = fp[fp[colname].isna()]
all_fp = list(fp0["FID"])

sar_fn = get_filename(sar_path, fp_path, all_fp[0])
rgb_fn = get_filename(rgb_path, fp_path, all_fp[0])
ndwi2_fn = get_filename(ndwi2_path, fp_path, all_fp[0])


fps, cut_sar, cut_rgb, cut_ndwi2, sar_2d_array = plot_fp_s2_ndwi2(fp["geometry"][all_fp[0]], sar, rgb, ndwi2, sar_fn, rgb_fn, ndwi2_fn)

s1 = None
s2 = None
s3 = None

fig, ax = plt.subplots(nrows=1,ncols=3)
fig.canvas.mpl_connect('key_press_event', on_press)

p_sar = rasterio.plot.show(cut_sar, ax=ax[0], cmap='Spectral_r', vmin = -30, vmax = 0.5, title = "sar")
p_ndwi2 = rasterio.plot.show(cut_ndwi2, ax=ax[1], cmap='Spectral', vmin = -1, vmax = 1, title = "ndwi2")
p_rgb = rasterio.plot.show(cut_rgb.read(), transform = cut_rgb.transform, ax=ax[2], title = "RGB")

fps.plot(color = "white", ax = p_sar)
fps.plot(color = "white", ax = p_ndwi2)
fps.plot(color = "white", ax = p_rgb)

cut_sar.close()
cut_rgb.close()
cut_ndwi2.close()

plt.show()