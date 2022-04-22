import math
import os
from skimage import io
import numpy as np
from itertools import combinations
import shutil
import argparse
import pickle


def getNumberId(in_listDir, in_id, in_perc):
    """ Find raster file name based on id
    Parameters
    ----------
    in_listDir: list str
        Base path where rasters are stored
    in_id : int
        Reference id
    in_perc : float
        Float
    Returns
    -------
        Dictionary with list of train and validation files
    """
    cnt = 0
    files = []
    for dir in in_listDir:
        data = dir.split('_')[0]
        if(int(data)==in_id):
            cnt += 1
            files.append(dir)
    num_files = math.floor(cnt*in_perc)
    if(num_files<1):
        num_files = 1
    print(in_id, cnt)
    return {'validation': files[:num_files], 'train': files[num_files:]}

def copy_list_rasters(in_basePath, in_outPath, in_listFiles):
    """Copy list of rasters from source to destination
            Parameters
    ----------
    in_basePath : str
        Base path where rasters are stored
    in_outPath : int
        Destination path
    in_listFiles : list str
        List files that will be moved to destination
    """
    for file in in_listFiles:
        shutil.copyfile(os.path.join(in_basePath, file), os.path.join(in_outPath, file))


def parse_args():
    """Method that handles arguments
    Returns
    -------
        parsed arguments
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--basepath", required=True, type=str,
                        help="Path where rasters that will be part of dataset are stored")
    ap.add_argument("-p", "--percval", required=True, type=float,
                        help="Percentage validation (0-1)")
    ap.add_argument("-o", "--pathoutput", required=True, type=str,
                        help="Path where output files will be stored")
    args = ap.parse_args()
    return args


if __name__ == '__main__':
    """This script split train and validation based on percentage informed as input.
    Please note that it expects the same pathoutput used for train_test
    """

    args = parse_args()
    base_out = args.pathoutput

    train_path = base_out + '\\train'
    validation_path = base_out + '\\valiation'
    if (not os.path.isdir(train_path)):
        os.makedirs(train_path)
    if (not os.path.isdir(validation_path)):
        os.makedirs(validation_path)

    base_path = args.basepath
    paths = os.listdir(base_path)

    ref_resolution_path = 'R10m'
    list_res = {'R10m': ['AOT', 'B02', 'B03', 'B04', 'B08', 'TCI', 'WVP', 'reference'],
                'R20m': ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12', 'SCL'],
                'R60m': ['B01', 'B09']}

    perc = args.percval
    with open(os.path.join(base_out, 'rel_sat_id.pickle'), 'rb') as handle:
        b = pickle.load(handle)

    ref_base_path = os.path.join(base_path, ref_resolution_path, 'reference')
    dirs = os.listdir(ref_base_path)
    rel_id_num = {}
    for i in b.keys():
        rel_id_num[i] = getNumberId(dirs, i, perc)

    for res in list_res.keys():
        ref_res_path = os.path.join(base_path, res)
        for paths_in_ref in list_res[res]:
            in_ref_spe_path = os.path.join(ref_res_path, paths_in_ref)

            validation_path_res_mask = os.path.join(validation_path, res, paths_in_ref)
            if (not os.path.isdir(validation_path_res_mask)):
                os.makedirs(validation_path_res_mask)
            train_path_res_mask = os.path.join(train_path, res, paths_in_ref)
            if (not os.path.isdir(train_path_res_mask)):
                os.makedirs(train_path_res_mask)

            for i in b.keys():
                copy_list_rasters(in_ref_spe_path, validation_path_res_mask, rel_id_num[i]['validation'])
                copy_list_rasters(in_ref_spe_path, train_path_res_mask, rel_id_num[i]['train'])

