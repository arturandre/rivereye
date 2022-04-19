// import 'ol/ol.css';
// import Map from 'ol/Map';
// import View from 'ol/View';
// import {Circle as CircleStyle, Fill, Stroke, Style} from 'ol/style';
// import {Draw, Modify, Snap} from 'ol/interaction';
// import {OSM, Vector as VectorSource} from 'ol/source';
// import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer';
// import {get} from 'ol/proj';

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
  function(ft) {
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
      color: 'rgba(255, 0, 0, 0.2)',
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

  

const modify = new ol.interaction.Modify({source: source});
map.addInteraction(modify);

let draw, snap; // global so we can remove them later
//const typeSelect = document.getElementById('type');

function addInteractions() {
  draw = new ol.interaction.Draw({
    source: source,
    //type: typeSelect.value,
    type: "Polygon",
  });
  map.addInteraction(draw);
  snap = new ol.interaction.Snap({source: source});
  map.addInteraction(snap);
}

async function readBinaryFile(url)
{
  let oReq = new XMLHttpRequest();
  oReq.open("GET", url, true);
  oReq.responseType = "blob";
  return new Promise(function(s, r){
    oReq.onload = async function (oEvent){
      let blob = await oReq.response.arrayBuffer();
      s(blob);
    };
    oReq.send();
  });
}

async function load_demo0()
{
  let shpurl = "http://localhost:8000/static/mapretriever/demo/map0/0_buffer.shp";
  let dbfurl = "http://localhost:8000/static/mapretriever/demo/map0/0_buffer.dbf";
  let prjurl = "http://localhost:8000/static/mapretriever/demo/map0/0_buffer.prj";
  
  
  let shpBuffer = await readBinaryFile(shpurl);
  let dbfBuffer = await readBinaryFile(dbfurl);
  let prjStr = await $.get(prjurl);
  let featureCollection =
    shp.combine([shp.parseShp(shpBuffer, prjStr),shp.parseDbf(dbfBuffer)]);

  let fldStyles = [
    new ol.style.Style({ //0 - Yellow (Anything?)
      fill: new ol.style.Fill({
        color: 'rgba(255, 255, 0, 0.5)',
      })
    }),
    new ol.style.Style({ // 1 - Blue (River)
      fill: new ol.style.Fill({
        color: 'rgba(0, 0, 255, 0.5)',
      })
    }),
    new ol.style.Style({
      fill: new ol.style.Fill({ // 2 - Green (Forest?)
        color: 'rgba(0, 255, 0, 0.5)',
      })
    })
  ];
  
  
  featureCollection = new ol.format.GeoJSON().readFeatures(featureCollection);
  for (let i = 0; i < featureCollection.length; i++)
  {
    featureCollection[i].getGeometry().transform("EPSG:4326", "EPSG:3857");
    try {
      let myfldcode = featureCollection[i].getProperties()["MYFLD"];
      featureCollection[i].setStyle(fldStyles[myfldcode]);
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


$('#btnAnalisis').click(function(){
  $(map.getViewport()).toggle('hidden');
  $('#demo0').toggle('hidden');
});