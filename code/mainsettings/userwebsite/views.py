from ast import Mult
from http.client import HTTPResponse
import json
from django.shortcuts import render

from userwebsite.gerar_relatorio.build_report import create_pdf_report
from mainsettings.settings import STATIC_ROOT

from django.http import FileResponse, HttpResponse, JsonResponse

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.serializers import serialize
import shapely
from shapely import wkt
from shapely.ops import clip_by_rect

from django.views.decorators.csrf import csrf_exempt

from scripts.util.geo_utils import shape_to_raster_based_on_extent

from .models import Riversides

import os

# Create your views here.

def Home(request):
    return render(request,'home.html')

def Home2(request):
    return render(request,'pagina/index.html')

@csrf_exempt
def get_report(request):
    output_folder = os.path.join('mainsettings', "temp")
    os.makedirs(output_folder, exist_ok=True)
    body_text = request.body.decode("utf-8")
    area_results = json.loads(body_text)

    for area_result in area_results:
        map_id = 0
        def map_path(map_id):
            result = os.path.join('mainsettings', output_folder, f"map{map_id}")
            return result
        while os.path.exists(map_path(map_id)+ ".jpg"):
            map_id += 1
        base_shape_file = os.path.join('mainsettings', *(STATIC_ROOT.split('/')), *('/mapretriever/demo/map0/0_out.shp'.split('/')))
        print(base_shape_file)
        shape_to_raster_based_on_extent(
            in_extent = area_result['extent'],
            in_shape_path = base_shape_file,
            in_out_path = map_path(map_id) + ".tiff"
        )
        area_result['fname'] = map_path(map_id).replace('\\', '/') + ".jpg"
    #     'river_area' : 1,
    #     'veg_area' : 2,
    #     'nveg_area' : 5,
    #     'fname' : 'map.jpg',
    #     'cost' : 20000}]
    outfile = create_pdf_report(area_results, output_folder)
    response = FileResponse(open(outfile, 'rb'), content_type='application/pdf')
    response["Content-Description"] = "File-Transfer"
    response["Content-Transfer-Encoding"] = "binary"
    response["Content-Disposition"] = "attachment; filename=" + "report.pdf"

    return response

def mock_shape_extent(request):
    from scripts.util.geo_utils import mock_shape_extent
    mock_shape_extent()
    return HttpResponse("OK")

@csrf_exempt
def filter_by_bbox(request):
    aux = request.body.decode("utf-8")
    aux = json.loads(aux)
    results = []
    for poly in aux['features']:
        poly = Polygon(poly['geometry']['coordinates'][0])
        #aux = GEOSGeometry(poly['features'])
        result = Riversides.objects.filter(poly__intersects=poly)
        for geom in result:
            shapelyGeom = wkt.loads(geom.poly.wkt)
            clipped = clip_by_rect(shapelyGeom, *poly.extent)
            if isinstance(clipped, shapely.geometry.Polygon):
                clipped = shapely.geometry.multipolygon.MultiPolygon([clipped])
            clipped = clipped.wkt
            geom.poly = MultiPolygon.from_ewkt(clipped)
        result = serialize('geojson', result, geometry_field='poly', fields=('MYFLD','AREA',))
        result = json.loads(result)
        results.append(result)
    return JsonResponse(results, safe=False)
