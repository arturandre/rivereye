from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import zipfile
import os
from util import esri_shp, geo_utils
from datetime import date
import calendar
import argparse
import sys


api = SentinelAPI('luancasagrande', '6599Ufsc..')

def download_data(in_footprint, in_date, in_limit):
    """Auxiliar function to query data usign API
    ----------
    in_footprint : str
        String describing the requested polygons convex hull
    in_date : tuple datetime
        Reference and limit datetime
    in_limit : int
        Number of samples

    Returns
    -------
        Dictionary describing the products sorted by cloud coverage percentage
    """

    products = api.query(in_footprint,
                         date=in_date,
                         platformname='Sentinel-2',
                         processinglevel='Level-2A')
    products_df = api.to_dataframe(products)
    products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True])
    products_df_sorted = products_df_sorted.head(in_limit)

    # download sorted and reduced products
    api.download_all(products_df_sorted.index)

    return products_df_sorted


def crop_data(in_path, in_listPolygons, in_outPath, in_shpFile):
    """Crop rasters based on list of polygons and store in the output file
    ----------
    in_path : str
        Input path
    in_listPolygons : list of OGRgeometries
        List of polygons used as reference to crop the data
    in_outPath : str
        Output path
    in_shpFile : str
        Path to shape file used as reference to calculate footprint and crop the data (input polygons)
    """
    listDirs = os.listdir(in_path)
    fileMask = os.path.join(in_outPath, 'polygons.tif')
    if (not os.path.isdir(in_outPath)):
        os.makedirs(in_outPath)
    geo_utils.gdal_rasterize(os.path.join(in_path, listDirs[0]), in_shpFile, fileMask)
    for polygonPos in range(len(in_listPolygons)):
        geo_utils.gdal_translate(fileMask, os.path.join(in_outPath, str(polygonPos) + '_mask.tif'),
                       in_listPolygons[polygonPos].GetEnvelope())
    for file in listDirs:
        for polygonPos in range(len(in_listPolygons)):
            filePath = os.path.join(in_path, file)
            outPath = os.path.join(in_outPath, file)
            if (not os.path.isdir(outPath)):
                os.makedirs(outPath)
            geo_utils.gdal_translate(filePath, os.path.join(outPath, str(polygonPos)+'.tif'),
                           in_listPolygons[polygonPos].GetEnvelope())


def donwload_data_based_on_geojson(in_shape, in_year, in_month, in_num, in_outpath):
    """Method that download, unzip, and move the data to outpath based on year, month, and number of samples
        Parameters
    ----------
    in_shape : str
        Path to shape file used as reference to calculate footprint and crop the data (input polygons)
    in_year : int
        Year used to query the data
    in_month : int
        Month used to query the data
    in_num : int
        Number of cases to be downloaded
    in_outpath : str
        Output path
    """
    tmp_folder = 'tmp'
    try:
        if(not os.path.isdir(tmp_folder)):
            os.makedirs(tmp_folder)
    except Exception as e:
        print('It is not possible to create a tmp folder! Please contact DEV team.')
        sys.exit()

    polygons = esri_shp.read_shape_file_from_list_geo(in_shape)
    listGeos = [item['geometry'] for item in polygons]
    multipolygon = geo_utils.get_multi_polygon(listGeos)

    products_df = download_data(str(multipolygon.ConvexHull()), (date(in_year, in_month, 1),
                                            date(in_year, in_month, calendar.monthrange(in_year, in_month)[1])), in_num)
    for index, row in products_df.iterrows():
        with zipfile.ZipFile(row['title'] + '.zip', 'r') as zip_ref:
            zip_ref.extractall(tmp_folder)
        path_imgs = os.path.join(tmp_folder, row['filename'], 'GRANULE')
        for folder in os.listdir(path_imgs):
            path_segment = os.path.join(path_imgs, folder, 'IMG_DATA')
            if (os.path.isdir(os.path.join(path_segment, 'R10m'))):
                pathFiles10m = os.path.join(path_segment, 'R10m')
                outFolderAux = os.path.join(in_outpath, str(in_year), str(in_month), row['filename'], folder, 'R10m')
                crop_data(pathFiles10m, listGeos, outFolderAux, in_shape)
            if (os.path.isdir(os.path.join(path_segment, 'R20m'))):
                pathFiles10m = os.path.join(path_segment, 'R20m')
                outFolderAux = os.path.join(in_outpath, str(in_year), str(in_month), row['filename'], folder, 'R20m')
                crop_data(pathFiles10m, listGeos, outFolderAux, in_shape)
            if (os.path.isdir(os.path.join(path_segment, 'R60m'))):
                pathFiles10m = os.path.join(path_segment, 'R60m')
                outFolderAux = os.path.join(in_outpath, str(in_year), str(in_month), row['filename'], folder, 'R60m')
                crop_data(pathFiles10m, listGeos, outFolderAux, in_shape)


def parse_args():
    """Method that handles arguments
    Returns
    -------
        parsed arguments
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--month", required=True, type=int,
                        help="Month number used to query the raster")
    ap.add_argument("-y", "--year", required=True, type=int,
                        help="Year number used to query the raster")
    ap.add_argument("-mn", "--maxnum", required=True, type=int,
                        help="Maximum number of downloads")
    ap.add_argument("-i", "--inshape", required=True, type=str,
                    help="Input shape used as reference to define the footprint and ROI")
    ap.add_argument("-o", "--pathoutput", required=True, type=str,
                        help="Path where output files will be stored")
    args = ap.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    m = args.month
    y = args.year
    num = args.maxnum
    in_shape = args.inshape
    out_path = args.pathoutput

    if(not os.path.isfile(in_shape)):
        print('Your input directory is not a file!')
        sys.exit()

    try:
        if(not os.path.isdir(out_path)):
                os.makedirs(out_path)
    except Exception as e:
        print('It is not possible to create your output folder! Please input a valid directory.')
        sys.exit()

    try:
        donwload_data_based_on_geojson(in_shape, y, m, num, out_path)
    except Exception as e:
        print('Problem when downloading/composing the dataset. Please contact the DEV team.')
        sys.exit()

    print('Data downloaded and saved in the following folder: ' + (out_path))
    sys.exit()

