import numpy as np
import rasterio
from rasterio.plot import reshape_as_image
from affine import Affine
from rasterio.features import rasterize
from osgeo import gdal
from osgeo import ogr, osr


def read_image(in_path):
    dataset = rasterio.open(in_path)
    aux = dataset.read()
    aux = reshape_as_image(aux)
    return aux

def get_multi_polygon(in_list):
    multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
    for item in in_list:
        multipolygon.AddGeometry(item)
    return multipolygon


def rasterize_list_geometries(in_list, in_shapeOut, in_geoTransform, in_dtype = 'uint8'):
    try:
        if(len(in_list)==0):
            return np.zeros(in_shapeOut, dtype=in_dtype)
        gtAffine = Affine(in_geoTransform[1], in_geoTransform[2], in_geoTransform[0],
                             in_geoTransform[4], in_geoTransform[5], in_geoTransform[3])
        return rasterize(in_list, out_shape=in_shapeOut, transform=gtAffine, dtype=in_dtype)
    except Exception as e:
        return np.zeros(in_shapeOut, dtype=in_dtype)


def gdal_rasterize(src_rast, mask_vect, in_outPath, in_attribute = 'ATTRIBUTE=MYFLD'):
    rast_ds = gdal.Open(src_rast)
    gt = rast_ds.GetGeoTransform()
    b = rast_ds.GetRasterBand(1)

    # Get vector metadata
    mask_ds = ogr.Open(mask_vect)
    mask_lyr = mask_ds.GetLayer(0)

    # Get EPSG info
    rast_srs = osr.SpatialReference(wkt=rast_ds.GetProjection())
    rast_srs.AutoIdentifyEPSG()
    rast_epsg = rast_srs.GetAttrValue('AUTHORITY',1)

    mask_srs = mask_lyr.GetSpatialRef()
    mask_srs.AutoIdentifyEPSG()
    mask_epsg = mask_srs.GetAttrValue('AUTHORITY',1)

    # Get raster corner points
    ul = gdal.ApplyGeoTransform(gt,0,0)
    ur = gdal.ApplyGeoTransform(gt,b.XSize,0)
    lr = gdal.ApplyGeoTransform(gt,b.XSize,b.YSize)
    ll = gdal.ApplyGeoTransform(gt,0,b.YSize)



    # Create raster to store mask
    drv = gdal.GetDriverByName('GTiff')

    mask_rast = drv.Create(in_outPath,b.XSize,b.YSize, 1, gdal.GDT_Float32,
                        options=['TILED=YES','COMPRESS=DEFLATE'])
    mask_rast.SetGeoTransform(gt)
    mask_rast.SetProjection(rast_srs.ExportToWkt())
    mask_band = mask_rast.GetRasterBand(1)
    mask_band.Fill(0)

    # Rasterize filtered layer into the mask tif
    gdal.RasterizeLayer(mask_rast, [1], mask_lyr,
                        options=[in_attribute])
    mask_rast = None
    mask_ds = None
    rast_ds = None


def gdal_translate(in_filePath, in_outFile, in_extent):
    ext = [in_extent[0], in_extent[3], in_extent[1], in_extent[2]]
    gdal.Translate(in_outFile, in_filePath, projWin=ext, projWinSRS='EPSG:4326')


def create_multi_band_geotiff(in_img, in_dataSet, in_outPath, in_outType=gdal.GDT_Byte):
    try:
        driver = in_dataSet.GetDriver()
        num_bands = 1
        if len(in_img.shape) == 3:
            num_bands = in_img.shape[2]
        outDS = driver.Create(in_outPath, in_img.shape[1], in_img.shape[0], num_bands, in_outType, ['COMPRESS=LZW'])
        in_geoTransform = in_dataSet.GetGeoTransform()
        outDS.SetGeoTransform(in_geoTransform)
        proj = in_dataSet.GetProjection()
        outDS.SetProjection(proj)
        for bandId in range(num_bands):
            if num_bands > 1:
                outDS.GetRasterBand(bandId + 1).WriteArray(in_img[:, :, bandId])
            else:
                outDS.GetRasterBand(bandId + 1).WriteArray(in_img)
        outDS.FlushCache()
        outDS = None
    except Exception as e:
        raise Exception("GDAL_MANAGER: Problem to compose geotiff: %s" % (str(e)))


