from osgeo import gdal
from util.esri_shp import read_shape_file_from_list_geo, polygon_response, add_area_per_polygon
from util.geo_utils import *
from util.ml_utils import *
import argparse
import os
import sys
import copy


def get_string(in_listString, in_listConditions):
    """Get string based on condition
    ----------
    in_listString : list str
        List of strings that will be analyzed
    in_listConditions : list str
        List of conditions to be checked

    Returns
    -------
        String that attends all conditions
    """
    for string in in_listString:
        flag_conditions = True
        for condition in in_listConditions:
            if(condition not in string):
                flag_conditions = False
                break
        if(flag_conditions == False):
            continue
        else:
            return string

def get_mask_based_on_dictPolygons(in_dict, in_shapeOut, in_gt):
    """Rasterize shape and define values based on keys
    ----------
    in_dict : dict
        Dictionary that relates the geometries to be rasterized and it's id
    in_shapeOut : tuple int
        raster size
    in_gt :
        Geotransform

    Returns
    -------
        Raster composed by polygons
    """
    out = np.zeros(in_shapeOut)
    for key in in_dict:
        if (key is None):
            continue
        mask = rasterize_list_geometries(in_dict[key], in_shapeOut, in_gt, in_dtype='uint8')
        out += mask*key
    return out


def class_definition_based_on_clusters(in_labels, in_index_ref, in_num_clusters, in_num_classes, in_valida_test):
    """Optimize number of clusters based on reference
    ----------
    in_labels : raster
        Labels predicted using unsupervised method
    in_index_ref : raster
        Raster that represents the values that were clustered
    in_num_clusters :
        Number of clusters
    in_num_classes :
        Expected number of classes
    in_valida_test :
        Reference mask

    Returns
    -------
        output :
            Raster that represents the best output
        thresholds :
            Thresholds used to compute the output
        in_valida_test :
            List of classes predicted
    """
    output = np.zeros(in_labels.shape, 'uint8')
    num_pixels = np.zeros(in_num_classes)

    for i in range(0, in_num_classes):
        num_pixels[i] = np.sum(in_valida_test == (i+1))

    perc = np.zeros((in_num_clusters, in_num_classes))
    class_def = []
    thresholds = []
    for i in range(0, in_num_clusters):
        aux = in_labels == i

        if (np.sum(aux) == 0):
            continue
        for j in range(0, in_num_classes):
            pixels = np.multiply(aux, in_valida_test == (j+2))
            perc[i, j] = (np.sum(pixels)) / (float(np.sum(aux)))
        values = in_index_ref[aux]

        thresholds.append([np.min(values), np.max(values)])
        class_def.append((np.argwhere(np.max(perc[i, :]) == perc[i, :])[0][0])+2)
        output[aux] = (np.argwhere(np.max(perc[i, :]) == perc[i, :])[0][0])+2

    return output, thresholds, class_def


def get_thresholds(in_raster, in_reference,  in_nclasses):
    """Optimize number of clusters based on reference
    ----------
    in_labels : raster
        Dictionary that relates the geometries to be rasterized and it's id
    in_shapeOut : tuple int
        raster size
    in_gt :
        Geotransform

    Returns
    -------
        Raster composed by polygons
    """
    nOutput = 1
    list_best_comb = [[] for i in range(nOutput)]
    list_acc_kappa = [[] for i in range(nOutput)]
    list_min_weight = np.zeros(nOutput)


    try:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_PP_CENTERS

        cont = 0

        for band_num in range(in_raster.shape[2]):
            for nclusters in range(in_nclasses, 10):
                index = in_raster[:,:,band_num]
                compactness, labels, centers = cv2.kmeans(index.flatten().astype(np.float32), nclusters, None,
                                                              criteria, 10, flags)
                labels = labels.reshape((index.shape))
                [img_out, thresholds, class_def] = class_definition_based_on_clusters(labels, index, nclusters, in_nclasses,
                                                                                    in_reference)

                kappa, acc = calc_fitness(img_out, in_reference, in_nclasses, removeZeroFlag=True)
                if np.isnan(kappa):
                    kappa = 1
                weighted_value = kappa * 0.75 + acc * 0.25
                if (np.sum(weighted_value > list_min_weight) > 0):
                    posAux = np.where(list_min_weight == np.min(list_min_weight))[0][0]
                    list_best_comb[posAux] = [None, None, copy.deepcopy(thresholds),
                                            copy.deepcopy(class_def)]
                    list_min_weight[posAux] = weighted_value
                    list_acc_kappa[posAux] = [kappa, acc]
                    best_out = copy.deepcopy(img_out)
                    print(nclusters, weighted_value)
            cont += 1
    except Exception as e:
        print('Error kmeans', e)
    return list_best_comb, list_acc_kappa, list_min_weight, best_out

def cleanData(in_data):
    in_data[np.isnan(in_data)] = 0
    in_data[np.isinf(in_data)] = 0
    return in_data

def parse_args():
    """Method that handles arguments
    :return parsed arguments
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-ir", "--inrasters", required=True, type=str,
                        help="Folder composed by the rasters that will be analyzed")
    ap.add_argument("-is", "--inshape", required=True, type=str,
                        help="Dirctory that points to a shape file where the ROI were defined")
    ap.add_argument("-o", "--outpath", required=True, type=str,
                        help="Base output path")
    args = ap.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    in_folder = args.inrasters
    out_shapes = args.outpath
    shpFile = args.inshape

    tmp_folder = 'tmp'
    try:
        if(not os.path.isdir(tmp_folder)):
            os.makedirs(tmp_folder)
    except Exception as e:
        print('It is not possible to create a tmp folder! Please contact DEV team.')
        sys.exit()

    polygons = read_shape_file_from_list_geo(shpFile)

    polygons_per_ID = {}
    for item in polygons:
        if(item['id'] in polygons_per_ID):
            polygons_per_ID[item['id']].append(item['geometry'])
        else:
            polygons_per_ID[item['id']] = [item['geometry']]

    list_sat_rasters = os.listdir(in_folder)
    for sat in list_sat_rasters:
        sat_folder = os.path.join(in_folder, sat)
        stripes = os.listdir(sat_folder)
        for stripe in stripes:
            stripe_folder = os.path.join(sat_folder, stripe)
            folder10m = os.path.join(stripe_folder, 'R10m')

            out_shape = os.path.join(folder10m, out_shapes)
            if (not os.path.isdir(out_shape)):
                os.makedirs(out_shape)

            dirs = os.listdir(folder10m)
            dirb08 = get_string(dirs, ['_B08_'])
            dirb04 = get_string(dirs, ['_B04_'])
            dirb03 = get_string(dirs, ['_B03_'])
            b08 = os.path.join(folder10m, dirb08)
            b04 = os.path.join(folder10m, dirb04)
            b03 = os.path.join(folder10m, dirb03)
            patches = os.listdir(b08)
            for cnt, patch in enumerate(patches):
                if not patch.endswith((".tif", ".tiff", ".png", ".jpg", ".jp2", ".jpeg")):
                    continue
                print('Processing {}. {}%'.format(patch, round(cnt*100.0 / float(len(patches)))))

                patch_value = patch.split('.')[0]
                rast_ds = gdal.Open(os.path.join(b08, patch))
                gt = rast_ds.GetGeoTransform()

                b08raster = read_image(os.path.join(b08, patch))[:,:,0]
                b04raster = read_image(os.path.join(b04, patch))[:,:,0]
                b03raster = read_image(os.path.join(b03, patch))[:,:,0]
                ndvi = np.divide((b08raster-b04raster),(b08raster+b04raster))
                ndvi[ndvi>1] = 1
                ndvi = cleanData(ndvi)
                ndwi = np.divide((b08raster-b03raster),(b08raster+b03raster))
                ndwi[ndwi>1] = 1
                ndwi = cleanData(ndwi)

                aux = np.zeros([ndvi.shape[0], ndvi.shape[1], 4])
                aux[:, :, 0] = ndvi
                aux[:, :, 1] = ndwi
                aux[:, :, 2] = b08raster
                aux[:, :, 3] = b04raster

                gdal_rasterize(os.path.join(b08, patch), shpFile, 'tmp2.tif', in_attribute='ATTRIBUTE=id')
                mask = read_image('tmp2.tif')[:,:,0]
                water = (mask == 4).astype(np.uint8)
                forestry = (mask == 2).astype(np.uint8)
                other = (mask == 3).astype(np.uint8)

                aux_mask = np.zeros(mask.shape)
                aux_mask[forestry>0] = 1
                aux_mask[other>0] = 2
                listBestComb, listAccKappa, listMinWeight, bestOutForestry = get_thresholds(aux, aux_mask+1, len(np.unique(aux_mask)))

                aux_mask_wa = np.zeros(mask.shape)
                aux_mask_wa[water>0] = 1
                aux_mask_wa[aux_mask>0] = 2
                listBestComb, listAccKappa, listMinWeight, bestOutWater = get_thresholds(aux, aux_mask_wa+1, len(np.unique(aux_mask_wa)))

                pred_water = (bestOutWater==2)
                bestOutForestry[pred_water>0]= 1
                water = (pred_water).astype(np.uint8)

                outputs = cv2.connectedComponentsWithStats(water, connectivity=8,
                                                           ltype=cv2.CV_32S)
                areas = outputs[2][:, 4]
                res = np.where(areas <= 10)
                areas_identified = np.in1d(outputs[1], res).astype(np.uint8)
                areas_identified = np.reshape(areas_identified, water.shape)
                water[areas_identified>0] = 0

                kernel = np.ones((21, 21), np.uint8)
                img_dilation = cv2.dilate(water, kernel, iterations=1)

                rast_ds = gdal.Open(os.path.join(b08, patch))
                gt = rast_ds.GetGeoTransform()

                bestOutForestry[img_dilation == 0] = 0
                bestOutForestry[pred_water>0] = 1
                create_multi_band_geotiff(bestOutForestry, rast_ds, 'tmp3.tif')
                polygon_response('tmp3.tif', os.path.join(out_shapes, str(patch.split('.')[0]) + '_out'))
                add_area_per_polygon(os.path.join(out_shapes, str(patch.split('.')[0]) + '_out.shp'))

