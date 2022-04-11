import geopandas as gpd
from shapely import geometry
from rasterio.mask import mask
import rasterio
from rasterio import plot
import matplotlib.pyplot as plt
import shutil


def plot_fp_s2_ndwi2(fp, sar, rgb, ndwi2, sar_fn: str, rgb_fn: str, ndwi2_fn: str):
    '''
    fp: a fishpond geometry
    sar: tif raster of sentinal-1 sar
    ndwi2: tif raster of ndwi2
    sar_fn: path of sentinal-1 sar tif
    sar_fn: path of ndwi2 tif
    This function return fishpond geometry with frame, cutted sar raster, cutted ndwi2 raster and a list of sar value in fishpond.
    '''

    # find the frame of fispond
    fp_cor = tuple(fp.exterior.coords)

    x = []
    y = []
    for i in fp_cor:
        x.append(i[0])
        y.append(i[1])

    x = sum(x)/len(x)
    y = sum(y)/len(y)

    b = 250

    max_x = x + b
    max_y = y + b
    min_x = x - b
    min_y = y - b

    # max_x = 0
    # max_y = 0
    # min_x = 9999999999
    # min_y = 9999999999
    # for i in fp_cor:
    #     if i[0] > max_x:
    #         max_x = i[0]
    #     if i[0] < min_x:
    #         min_x = i[0]
    #     if i[1] > max_y:
    #         max_y = i[1]
    #     if i[1] < min_y:
    #         min_y = i[1]

    p1 = geometry.Point(max_x,max_y)
    p2 = geometry.Point(min_x,max_y)
    p3 = geometry.Point(min_x,min_y)
    p4 = geometry.Point(max_x,min_y)

    fp_frame = geometry.Polygon([[p.x, p.y] for p in [p1, p2, p3, p4, p1]])
    fps = gpd.GeoDataFrame({"geometry":[fp, fp_frame]}).boundary

    # cut sar raster
    framed_sar, trans_sar = mask(sar, [fp_frame], crop = True, all_touched=True)

    sar_meta = sar.meta
    sar_meta.update({
        "driver": "GTiff",
        "height": framed_sar.shape[1],
        "width": framed_sar.shape[2],
        "transform": trans_sar
        })

    with rasterio.open("./cut/sar_cut/%s.tif" % sar_fn, "w", **sar_meta) as cut_sar:
        cut_sar.write(framed_sar)

    cut_sar = rasterio.open("./cut/sar_cut/%s.tif" % sar_fn)


    # cut RGB raster
    framed_rgb, trans_rgb = mask(rgb, [fp_frame], crop = True, all_touched=True)

    rgb_meta = rgb.meta
    rgb_meta.update({
        "driver": "GTiff",
        "height": framed_rgb.shape[1],
        "width": framed_rgb.shape[2],
        "transform": trans_rgb
        })

    with rasterio.open("./cut/rgb_cut/%s.tif" % rgb_fn, "w", **rgb_meta) as cut_rgb:
        cut_rgb.write(framed_rgb)
    cut_rgb = rasterio.open("./cut/rgb_cut/%s.tif" % rgb_fn)


    # cut ndwi2 raster
    framed_ndwi2, trans_ndwi = mask(ndwi2, [fp_frame], crop = True, all_touched=True)
    ndwi2_meta = ndwi2.meta
    ndwi2_meta.update({
        "driver": "GTiff",
        "height": framed_ndwi2.shape[1],
        "width": framed_ndwi2.shape[2],
        "transform": trans_ndwi
        })

    with rasterio.open("./cut/ndwi2_cut/%s.tif" % ndwi2_fn, "w", **ndwi2_meta) as cut_ndwi2:
        cut_ndwi2.write(framed_ndwi2)
    cut_ndwi2 = rasterio.open("./cut/ndwi2_cut/%s.tif" % ndwi2_fn)

    # generate sar list
    sar_2d_array, trans = mask(sar, [fp], crop = True, all_touched = False)
    sar_2d_array = sar_2d_array[0].tolist()



    return fps, cut_sar, cut_rgb, cut_ndwi2, sar_2d_array

def get_filename(raster_path: str, fp_path: str, index: int):
    fp_fn = fp_path.replace("\\", "/")
    fp_fn = fp_fn.split("/")[-1][:-4]
    dir_name = raster_path.split("/")[-1][:-4] + "_" + fp_fn + "_" + str(index)

    return dir_name



if __name__ == "__main__":
    fp = gpd.read_file("./sha/demo_ponds.shp")
    sar_path = "./tiff/Subset_S1A_IW_GRDH_1SDV_20211210.tif"
    ndwi2_path = "./tiff/20211211 NDWI2_TWD97.tif"
    rgb_path = "./tiff/S2A_MSIL2A_20211211T023111_N0301_R046_T50QRL_20211211T045314_RGB2.tif"
    sar = rasterio.open(sar_path)
    ndwi2 = rasterio.open(ndwi2_path)
    rgb = rasterio.open(rgb_path)
    fp = fp["geometry"][14535]

    fps, cut_sar, cut_rgb, cut_ndwi2, sar_2d_array= plot_fp_s2_ndwi2(fp, sar, rgb, ndwi2, "mask_demo_img", "mask_demo_img", "mask_demo_img")

    fig, ax = plt.subplots(nrows=1,ncols=3)

    p_sar = rasterio.plot.show(cut_sar, ax=ax[0], cmap='Spectral_r', vmin = -30, vmax = 0.5, title = "sar")
    p_ndwi2 = rasterio.plot.show(cut_ndwi2, ax=ax[1], cmap='Spectral', vmin = -1, vmax = 1, title = "ndwi2")
    p_rgb = rasterio.plot.show(cut_rgb.read(), transform = cut_rgb.transform, ax=ax[2], title = "RGB")

    fps.plot(color = "white", ax = p_sar)
    fps.plot(color = "white", ax = p_ndwi2)
    fps.plot(color = "white", ax = p_rgb)
    plt.show()