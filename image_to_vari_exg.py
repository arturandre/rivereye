import geojson
from geojson import MultiPoint, Feature

import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser

class Options:
    def __init__(self) -> None:
        self.parser = ArgumentParser()
        self.initialize()

    def initialize(self):
        self.parser.add_argument("input_image", type=str, help="Input image to be converted to vari and ExG representations")
        self.parser.add_argument("--output_name", type=str, help="Optional output name 'output_ExG.png' and 'output_VARI.png'")
        self.parser.add_argument("-texg", type=int, help="Optional threshold to filter the ExG image. If not provided no filtered image for ExG is produced.")
        self.parser.add_argument("-tvari", type=int, help="Optional threshold to filter the VARI image. If not provided no filtered image for VARI is produced.")

    def parse(self):
        opts = self.parser.parse_args()
        return opts


def split_rgbimage(image):
    r = image[:,:,0]
    g = image[:,:,1]
    b = image[:,:,2]
    return r,g,b

def toExG(image):
    r,g,b = split_rgbimage(image)
    return 2*g -r-b

def toVARI(image):
    r,g,b = split_rgbimage(image)
    vari = (g-r)/(g+r-b)
    vari[np.isnan(vari)] = 0
    vari[np.isinf(vari)] = 0
    return vari

if __name__ == "__main__":
    """
    The outputted geojson has a single feature, whose geometry is
    a multipoint. The CRS should be the geojson standard WGS84 = EPSG:4326
    """


    # HARD CODED
    # TOP LEFT COORDINATE (center of the pixel)
    # EPSG:4326
    tllon,tllat = -46.45264024,-23.41153138
    
    # BOTTOM LEFT
    bllon,bllat = -46.4531857,-23.4616460

    # TOP RIGHT
    trlon,trlat = -46.38972815,-23.41210409

    # BOTTOM RIGHT
    brlon,brlat = -46.39025220,-23.46222443


    opts = Options().parse()
    input_image = plt.imread(opts.input_image)
    input_image = input_image.astype('int')

    image_height, image_width, _ = input_image.shape
    top_delta_lon = (trlon - tllon)/image_width
    bottom_delta_lon = (brlon - bllon)/image_width
    
    left_delta_lat = (tllat - bllat)/image_height
    right_delta_lat = (trlat - brlat)/image_height

    print(f"delta_lon |top-bottom| = {np.abs(top_delta_lon-bottom_delta_lon)}")
    print(f"delta_lat |left-right| = {np.abs(right_delta_lat-left_delta_lat)}")

    exg = toExG(input_image)
    vari = toVARI(input_image)

    input_no_ext = opts.input_image[:-4]
    outname_no_ext = input_no_ext if opts.output_name is None else opts.output_name

    plt.imsave(f"{outname_no_ext}_exg.png", exg, cmap='gray')
    plt.imsave(f"{outname_no_ext}_VARI.png", vari, cmap='gray')

    
    pmat = np.array([[top_delta_lon, 0],[0,left_delta_lat]])

    if opts.texg is not None:
        exg[exg < opts.texg] = 0
        plt.imsave(f"{outname_no_ext}_texg.png", exg, cmap='gray')
        exg_candidate_points = np.argwhere(exg>0)
        exg_candidate_points = list(np.array([tllon, tllat]) + exg_candidate_points@pmat)
        exg_candidate_points = [list(i) for i in exg_candidate_points]
        exg_multipoint = Feature(geometry=MultiPoint(exg_candidate_points))
        with open(f"{outname_no_ext}_texg.geojson", 'w') as f:
            geojson.dump(exg_multipoint, f)
        


    if opts.texg is not None:
        vari[vari < opts.tvari] = 0
        plt.imsave(f"{outname_no_ext}_tVARI.png", vari, cmap='gray')
        vari_candidate_points = np.argwhere(vari>0)
        vari_candidate_points = list(np.array([tllon, tllat]) + vari_candidate_points@pmat)
        vari_candidate_points = [list(i) for i in vari_candidate_points]
        vari_multipoint = Feature(geometry=MultiPoint(vari_candidate_points))
        with open(f"{outname_no_ext}_tvari.geojson", 'w') as f:
            geojson.dump(vari_multipoint, f)
        
