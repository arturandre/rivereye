import json
from django.shortcuts import render
from userwebsite.gerar_relatorio.build_report import create_pdf_report
from django.http import FileResponse

from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def Home(request):
    return render(request,'home.html')

def Home2(request):
    return render(request,'pagina/index.html')

@csrf_exempt
def get_report(request):
    output_folder = r"temp"
    area_results = json.loads(request.body.decode("utf-8"))

    for area_result in area_results:
        area_result['fname'] = 'map.jpg' # Luan vai mudar isso para ser dinamico baseado no extent
        area_result['cost'] = area_result['irregular_area']*10000 # Essa constante precisa ser alterada para algo mais factível e eventualmente algo dinâmico ou armazenado no BD

    # area_results = [{
    #     'gps_S' : 23.5558,
    #     'gps_W' : 46.6396,
    #     'irregular_area' : 2,
    #     'river_area' : 1,
    #     'veg_area' : 2,
    #     'nveg_area' : 5,
    #     'fname' : 'map.jpg',
    #     'cost' : 20000}]
    outfile = create_pdf_report(area_results, output_folder)
    response = FileResponse(open(outfile, 'rb'))

    return response
