import math
import os
from skimage import io
import numpy as np
from itertools import combinations
import shutil
import argparse
import pickle


def copy_list_rasters(in_basePath, in_outPath, in_listFiles, in_seq):
    """Copy list of rasters from source to destination
            Parameters
    ----------
    in_basePath : str
        Base path where rasters are stored
    in_outPath : int
        Destination path
    in_listFiles : list str
        List files that will be moved to destination
    in_seq : int
        Raster id
    """
    for file in in_listFiles:
        shutil.copyfile(os.path.join(in_basePath, file), os.path.join(in_outPath, str(in_seq) + '_' + file))


def parse_args():
    """Method that handles arguments
    Returns
    -------
        parsed arguments
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--basepath", required=True, type=str,
                        help="Path where rasters that will be part of dataset are stored")
    ap.add_argument("-p", "--perctest", required=True, type=float,
                        help="Percentage test (0-1)")
    ap.add_argument("-o", "--pathoutput", required=True, type=str,
                        help="Path where output files will be stored")
    args = ap.parse_args()
    return args


if __name__ == '__main__':
    """This script goes over all rasters, split them based on input parameters (try to approximate), 
    and stores it in an organized way (train/test) in the output path. It is important to note that the organization
    from spectra reference is kept.
    """

    args = parse_args()

    base_dir = args.pathoutput
    train_opt_path = base_dir + '\\train-opt'
    test_path = base_dir + '\\test'

    if (not os.path.isdir(train_opt_path)):
        os.makedirs(train_opt_path)
    if (not os.path.isdir(test_path)):
        os.makedirs(test_path)

    base_path = args.basepath
    paths = os.listdir(base_path)

    ref_resolution_path = 'R10m'
    list_res = ['R10m', 'R20m', 'R60m']
    skipPaths = ['shapes']

    perc = args.perctest
    seq = 0
    rel_path_seq = {}
    for ref in paths:
        rel_path = os.path.join(base_path, ref)
        stripes = os.listdir(rel_path)
        for stripe in stripes:
            stripe_path = os.path.join(rel_path, stripe)
            ref_res_path = os.path.join(stripe_path, ref_resolution_path)
            masks_path = os.path.join(ref_res_path, 'ref-out')
            masks_dict = {}

            for mask_dir in os.listdir(masks_path):
                try:
                    im = io.imread(os.path.join(masks_path, mask_dir))
                    masks_dict[mask_dir] = np.sum(im>0)
                except Exception as e:
                    continue
            sum_pixels = np.sum([masks_dict[key] for key in masks_dict])
            expected_number = sum_pixels * perc
            keys = masks_dict.keys()
            num_comb = math.floor(len(keys)*perc)
            if(num_comb < 1):
                num_comb = 1

            temp = combinations(keys, num_comb)
            combs = {}
            for comb in temp:
                sum = 0
                for item in comb:
                    sum += masks_dict[item]
                dif = expected_number - sum
                combs[comb] = abs(dif)
            test_keys = min(combs, key=combs.get)
            train_keys = set(keys) ^ set(test_keys)

            rel_path_seq[seq] = ref
            for res in list_res:
                train_opt_path_res = os.path.join(train_opt_path, res)
                if (not os.path.isdir(train_opt_path_res)):
                    os.makedirs(train_opt_path_res)
                test_path_res = os.path.join(test_path, res)
                if (not os.path.isdir(test_path_res)):
                    os.makedirs(test_path_res)

                ref_res_path = os.path.join(stripe_path, res)
                paths_in_ref = os.listdir(ref_res_path)
                for paths_in_ref in paths_in_ref:
                    in_ref_spe_path = os.path.join(ref_res_path, paths_in_ref)
                    if ((paths_in_ref in skipPaths) or (not os.path.isdir(in_ref_spe_path))):
                        continue

                    if(paths_in_ref == 'ref-out'):
                        test_path_resMask = os.path.join(test_path_res, 'reference')
                        if (not os.path.isdir(test_path_resMask)):
                            os.makedirs(test_path_resMask)
                        copy_list_rasters(in_ref_spe_path, test_path_resMask, test_keys, seq)
                        train_path_res_mask = os.path.join(train_opt_path_res, 'reference')
                        if (not os.path.isdir(train_path_res_mask)):
                            os.makedirs(train_path_res_mask)
                        copy_list_rasters(in_ref_spe_path, train_path_res_mask, train_keys, seq)
                    else:
                        spe = paths_in_ref.split('_')[-2]
                        test_path_resSpe = os.path.join(test_path_res, spe)
                        if (not os.path.isdir(test_path_resSpe)):
                            os.makedirs(test_path_resSpe)
                        copy_list_rasters(in_ref_spe_path, test_path_resSpe, test_keys, seq)
                        train_path_res_spe = os.path.join(train_opt_path_res, spe)
                        if (not os.path.isdir(train_path_res_spe)):
                            os.makedirs(train_path_res_spe)
                        copy_list_rasters(in_ref_spe_path, train_path_res_spe, train_keys, seq)
            seq += 1

    with open(os.path.join(base_dir, 'rel_sat_id.pickle'), 'wb') as handle:
        pickle.dump(rel_path_seq, handle, protocol=pickle.HIGHEST_PROTOCOL)

