from osgeo import ogr, osr
import copy

def read_shape_file_from_list_geo(in_path):
    file = ogr.Open(in_path)
    if file is None:
        return []
    layer = file.GetLayer(0)
    # numFeatures = layer.GetFeatureCount()

    ldefn = layer.GetLayerDefn()
    layerFieldNames = []
    for n in range(ldefn.GetFieldCount()):
        fdefn = ldefn.GetFieldDefn(n)
        layerFieldNames.append(fdefn.name)

    features = []
    for feature in layer:
        geom = feature.GetGeometryRef()
        #geo = GEOSGeometry(str(geom.ExportToWkt()))

        fieldsGeo = {}
        for field in layerFieldNames:
            fieldsGeo[field] = feature.GetField(field)

        fieldsGeo['envelop'] = geom.GetEnvelope()
        fieldsGeo['geometry'] = copy.deepcopy(geom)
        features.append(fieldsGeo)

    return features


