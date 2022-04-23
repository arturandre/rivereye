// import 'ol/ol.css';
// import Map from 'ol/Map';
// import View from 'ol/View';
// import {Circle as CircleStyle, Fill, Stroke, Style} from 'ol/style';
// import {Draw, Modify, Snap} from 'ol/interaction';
// import {OSM, Vector as VectorSource} from 'ol/source';
// import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer';
// import {get} from 'ol/proj';

class Region{
  constructor(gps_S, gps_W, extent){
    this.gps_S = gps_S;
    this.gps_W = gps_W;
    this.irregular_area = 0;
    this.river_area = 0;
    this.veg_area = 0;
    this.nveg_area = 0;
    this.extent = extent; //minx, miny, maxx, maxy
  }

  inc_irregular_area(amount)
  {
    this.irregular_area += amount;
  }

  inc_river_area(amount)
  {
    this.river_area += amount;
  }

  inc_veg_area(amount)
  {
    this.veg_area += amount;
  }

  inc_nveg_area(amount)
  {
    this.nveg_area += amount;
  }

  simplify_values(){
    this.gps_S = parseFloat(this.gps_S.toFixed(4));
    this.gps_W = parseFloat(this.gps_W.toFixed(4));
    this.irregular_area = parseFloat(this.irregular_area.toFixed(2));
    this.river_area = parseFloat(this.river_area.toFixed(2));
    this.veg_area = parseFloat(this.veg_area.toFixed(2));
    this.nveg_area = parseFloat(this.nveg_area.toFixed(2));
  }
}

let featureCounter = 0

const raster = new ol.layer.Tile({
  source: new ol.source.OSM()
  /*source: new ol.source.XYZ({
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  })*/
})
// const raster = new TileLayer({
//   source: new OSM(),
// });

const source = new ol.source.Vector();
const source2 = new ol.source.Vector();
source.on('addfeature',
  function (ft) {
    console.log(ft);
    featureCounter++;
    ft.feature.setId(featureCounter)
  });


const vector = new ol.layer.Vector({
  source: source,
  style: new ol.style.Style({
    fill: new ol.style.Fill({
      color: 'rgba(255, 255, 255, 0.2)',
    }),
    stroke: new ol.style.Stroke({
      color: '#ffcc33',
      width: 2,
    }),
    image: new ol.style.Circle({
      radius: 7,
      fill: new ol.style.Fill({
        color: '#ffcc33',
      }),
    }),
  }),
});

const vector2 = new ol.layer.Vector({
  source: source2,
  style: new ol.style.Style({
    fill: new ol.style.Fill({
      color: 'rgba(255, 255, 0, 0.0)',
    }),
    stroke: new ol.style.Stroke({
      color: '#33ff33',
      width: 2,
    }),
    image: new ol.style.Circle({
      radius: 7,
      fill: new ol.style.Fill({
        color: '#ffcc33',
      }),
    }),
  }),
});

// Limit multi-world panning to one world east and west of the real world.
// Geometry coordinates have to be within that range.
const extent = ol.proj.get('EPSG:3857').getExtent().slice();
extent[0] += extent[0];
extent[2] += extent[2];
var map = new ol.Map({
  target: 'map',
  layers: [raster, vector, vector2],
  view: new ol.View({
    // center: ol.proj.fromLonLat([-97.7459463, 30.2838094]),
    // center: ol.proj.fromLonLat([-47.48258,-24.03863]), //próximo
    center: [-5280244.47922211, -2760133.33496918],
    zoom: 14.667234241513816
  })
});



const modify = new ol.interaction.Modify({ source: source });
map.addInteraction(modify);

let draw, snap; // global so we can remove them later

function addInteractions() {
  draw = new ol.interaction.Draw({
    source: source, type: "Polygon",
  });
  snap = new ol.interaction.Snap({ source: source });

  map.addInteraction(draw);
  map.addInteraction(snap);
}

async function readBinaryFile(url) {
  let oReq = new XMLHttpRequest();
  oReq.open("GET", url, true);
  oReq.responseType = "blob";
  return new Promise(function (s, r) {
    oReq.onload = async function (oEvent) {
      let blob = await oReq.response.arrayBuffer();
      s(blob);
    };
    oReq.send();
  });
}

let fldStyles = [
  new ol.style.Style({ // 0 - Blue (River)
    fill: new ol.style.Fill({
      color: 'rgba(0, 0, 255, 0.5)',
    })
  }),
  new ol.style.Style({
    fill: new ol.style.Fill({ // 1 - Green (Forest?)
      color: 'rgba(0, 255, 0, 0.5)',
    })
  }),
  new ol.style.Style({ //2 - Red (Irregular?)
    fill: new ol.style.Fill({
      color: 'rgba(255, 0, 0, 0.5)',
    })
  }),
  new ol.style.Style({ //3 - Yellow (Anything?)
    fill: new ol.style.Fill({
      color: 'rgba(255, 255, 0, 0.5)',
    })
  }),
];

async function load_demo0() {
  let shpurl = "http://localhost:8000/static/mapretriever/demo/map0/0_out.shp";
  let dbfurl = "http://localhost:8000/static/mapretriever/demo/map0/0_out.dbf";
  let prjurl = "http://localhost:8000/static/mapretriever/demo/map0/0_out.prj";


  let shpBuffer = await readBinaryFile(shpurl);
  let dbfBuffer = await readBinaryFile(dbfurl);
  let prjStr = await $.get(prjurl);
  let featureCollection =
    shp.combine([shp.parseShp(shpBuffer, prjStr), shp.parseDbf(dbfBuffer)]);


  featureCollection = new ol.format.GeoJSON().readFeatures(featureCollection);
  add_geojson_to_source2(featureCollection);
}




function add_geojson_to_source2(featureCollection, currentAreaIndex) {
  // MYFLD
  // 0 - Blue (River)
  // 1 - Green (Forest?)
  //2 - Red (Irregular?)
  //3 - Yellow (Anything?)
  // let areas = {
  //   "irregular_area": 0,
  //   "river_area": 0,
  //   "veg_area": 0,
  //   "nveg_area": 0
  // };

  let areas = region_areas[currentAreaIndex];
  
  for (let i = 0; i < featureCollection.length; i++) {
    featureCollection[i].getGeometry().transform("EPSG:4326", "EPSG:3857");
    try {
      let myfldcode = featureCollection[i].getProperties()["MYFLD"] - 1;
      let area = featureCollection[i].getProperties()["AREA"]/10000; //m2 -> ha
      featureCollection[i].setStyle(fldStyles[myfldcode]);
      if (myfldcode == 0)
      {
        areas.inc_irregular_area(area);
      }
      else if (myfldcode == 1)
      {
        areas.inc_river_area(area);
      }
      else if (myfldcode == 2)
      {
        areas.inc_veg_area(area);
      }
      else if (myfldcode == 3)
      {
        areas.inc_nveg_area(area);
      }
    } catch (error) {
      console.error(error);
    }
    source2.addFeature(featureCollection[i]);
  }
}

/**
 * Handle change event.
 */
// typeSelect.onchange = function () {
//   map.removeInteraction(draw);
//   map.removeInteraction(snap);
//   addInteractions();
// };

addInteractions();

$(map.getViewport()).css('position', 'absolute');
$(map.getViewport()).css('top', '0');
$('#demo0').css('position', 'absolute');
$('#demo0').css('top', '0');


$('#btnAnalisis').click(function () {
  //$(map.getViewport()).toggle('hidden');
  //$('#demo0').toggle('hidden');
  //$('#btnReport').hide();
  $('#btnReport').show();
  get_geom_for_sel_bbox();
});

$('#btnReport').click(async function () {
  mockup_data = [{
    "gps_S": 23.5558,
    "gps_W": 46.6396,
    "irregular_area": 2,
    "river_area": 1,
    "veg_area": 2,
    "nveg_area": 5
  }];
  for (let i in region_areas)
  {
    region_areas[i].simplify_values();
  }
  
  real_data = JSON.stringify(region_areas);

  let url = "http://127.0.0.1:8000/get_report";

  var oReq = new XMLHttpRequest();
  oReq.open("POST", url, true);
  oReq.responseType = "arraybuffer";
  //oReq.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

  oReq.onload = function(oEvent) {
    var arrayBuffer = oReq.response;

    // if you want to access the bytes:
    var byteArray = new Uint8Array(arrayBuffer);
    // ...

    // If you want to use the image in your DOM:
    var blob = new Blob([arrayBuffer], {type: "application/pdf;charset=UTF-8"});
    var url = URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    a.download = 'myfile.pdf';
    document.body.append(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  //oReq.send(JSON.stringify(mockup_data));
  //oReq.send(JSON.stringify(real_data));
  oReq.send(real_data);
});

var region_areas = [];
var region_counter_idx = 0;

async function get_geom_for_sel_bbox() {
  let url = "http://127.0.0.1:8000/filterbybbox";

  let format = new ol.format["GeoJSON"]();
  let bounding_boxes = source.getFeatures();
  let geoJsonStr = format.writeFeatures(bounding_boxes, { dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857' });
  for (bbox_idx in bounding_boxes)
  {
    bbox = bounding_boxes[bbox_idx];
    let extent = ol.proj.transformExtent(bbox.getGeometry().getExtent(), 'EPSG:3857', 'EPSG:4326');
    let centerX = (extent[0]+extent[2])/2;
    let centerY = (extent[1]+extent[3])/2;
    region_areas[bbox_idx] = new Region(centerY, centerX, extent);
  }

  var response = await $.post(url, geoJsonStr, function (featureCollections) {
    console.log(featureCollections);
    for (let ftColIdx in featureCollections) {
      featureCollection = featureCollections[ftColIdx];
      featureCollection = new ol.format.GeoJSON().readFeatures(featureCollection);
      add_geojson_to_source2(featureCollection, ftColIdx);
    }
  });
}