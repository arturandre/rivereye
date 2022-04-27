import argparse
import os
import torch
from dl_utils.model.unet import UNet
import numpy as np
import math
import pickle
from util.geo_utils import read_image, create_multi_band_geotiff
from util.esri_shp import polygon_response, add_area_per_polygon
from skimage.transform import resize
from osgeo import gdal
import sys
import cv2

PATCH_SIZE = 512

def parse_args():
    """Method that handles arguments
    :return parsed arguments
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-ir", "--inrasters", required=True, type=str,
                        help="Folder composed by the rasters that will be analyzed")
    ap.add_argument("-o", "--outpath", required=True, type=str,
                        help="Base output path")
    args = ap.parse_args()
    return args


def cleanData(in_data):
    in_data[in_data<0] = 0
    in_data[in_data>255] = 255
    in_data[np.isnan(in_data)] = 0
    in_data[np.isinf(in_data)] = 0
    return in_data


def get_raster(in_base_path, in_dir, in_bands_rel):
    bandRef = 'B02'
    order = ['B02', 'B03', 'B04', 'B08']
    dirRef = os.path.join(in_base_path, in_bands_rel[bandRef]['res_path'], bandRef)

    r1ref = read_image(os.path.join(dirRef, in_dir))
    out = np.zeros((r1ref.shape[0], r1ref.shape[1], len(in_bands_rel.keys())))
    for id, band in enumerate(order):
        filePath = os.path.join(in_base_path, in_bands_rel[band]['res_path'], band, in_dir)
        im = read_image(filePath)
        im = (im - in_bands_rel[band]['lower']) / (in_bands_rel[band]['upper'] - in_bands_rel[band]['lower'])
        im = cleanData(im)
        im = im[:,:,0]
        out[:, :, id] = (im * 255).astype(np.uint8)

    return out



if __name__ == '__main__':
    args = parse_args()

    in_folder = args.inrasters
    out_shapes = args.outpath

    try:
        if(not os.path.isdir(out_shapes)):
            os.makedirs(out_shapes)
    except Exception as e:
        print('It is not possible to create a tmp folder! Please contact DEV team.')
        sys.exit()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = UNet(n_channels=4, n_classes=4, bilinear=True).to(device)
    model.load_state_dict(torch.load('dl_utils/files/4bands-spectra/unet_epoch_79_0.13364.pt', map_location=torch.device(device)))
    model.eval()

    with open('dl_utils/files/norm.pickle', "rb") as fh:
        bands_rel = pickle.load(fh)

    bandRef = 'B02'
    order = ['B02', 'B03', 'B04', 'B08']
    base_path = os.path.join(in_folder, bands_rel[bandRef]['res_path'], bandRef)
    dirs = os.listdir(base_path)
    for dir in dirs:
        if not dir.endswith((".tif", ".tiff", ".png", ".jpg", ".jp2", ".jpeg")):
            continue
        print('Processing {}'.format(dir))
        raster = get_raster(in_folder, dir, bands_rel)
        height_ref = raster.shape[0]
        width_ref = raster.shape[1]
        nH = math.ceil(raster.shape[0] / float(PATCH_SIZE))
        nW = math.ceil(raster.shape[1] / float(PATCH_SIZE))
        out_f = np.zeros([height_ref, width_ref])
        for i in range(nH):
            for j in range(nW):
                imgAux = raster[i * PATCH_SIZE:(i + 1) * PATCH_SIZE, j * PATCH_SIZE:(j + 1) * PATCH_SIZE, :]
                height = imgAux.shape[0]
                width = imgAux.shape[1]
                resize_flag = False

                if(imgAux.shape[0] < PATCH_SIZE or imgAux.shape[1] < PATCH_SIZE):
                    imgAux = resize(imgAux, (PATCH_SIZE, PATCH_SIZE), order=0, preserve_range=True)
                    resize_flag = True

                imgAux /= 255.0
                imgAux = np.moveaxis(imgAux, -1, 0)
                imgAux =np.array([imgAux])
                torch_data = torch.tensor(imgAux).float()
                result = model(torch_data.to(device))
                mask = torch.argmax(result, axis=1).cpu().detach().numpy()[0]

                if(resize_flag):
                    mask = resize(mask, (height, width), order=0, preserve_range=True)
                out_f[i * PATCH_SIZE:(i + 1) * PATCH_SIZE, j * PATCH_SIZE:(j + 1) * PATCH_SIZE] = mask

        out = np.zeros(out_f.shape, np.uint8)
        out[out_f==1] = 2
        out[out_f==2] = 3

        water = (out_f==0).astype(np.uint8)
        kernel = np.ones((21, 21), np.uint8)
        img_dilation = cv2.dilate(water, kernel, iterations=1)

        rast_ds = gdal.Open(os.path.join(base_path, dir))
        gt = rast_ds.GetGeoTransform()

        out[img_dilation==0] = 0
        out[out_f==0] = 1
        create_multi_band_geotiff(out, rast_ds, 'tmp3.tif')
        polygon_response('tmp3.tif', os.path.join(out_shapes, str(dir.split('.')[0]) + '_out'))
        add_area_per_polygon(os.path.join(out_shapes, str(dir.split('.')[0]) + '_out.shp'))
