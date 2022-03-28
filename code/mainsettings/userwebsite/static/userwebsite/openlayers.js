// import 'ol/ol.css';
// import Map from 'ol/Map';
// import View from 'ol/View';
// import {Circle as CircleStyle, Fill, Stroke, Style} from 'ol/style';
// import {Draw, Modify, Snap} from 'ol/interaction';
// import {OSM, Vector as VectorSource} from 'ol/source';
// import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer';
// import {get} from 'ol/proj';

async function load_demo0() {
  function readFilePromise(file, filename) {
    return new Promise(function (resolve, reject) {
      if (!file) resolve(null);
      const reader = new FileReader();
      reader.onerror = function () {
        this.abort();
        console.trace(this.error);
        reject(this.error);
      };

      reader.onload = function () {
        resolve(this.result);
      };
      if (filename.endsWith('.prj')) {
        reader.readAsText(file);
      }
      else {
        reader.readAsBinaryString(file);
      }
    });
  }

  // var dbfFile;
  // var prjFile;
  // var shpFile;
  // var shxFile;

  var urls = [
    "http://localhost:8000/static/mapretriever/demo/map0/0_buffer.dbf",
    "http://localhost:8000/static/mapretriever/demo/map0/0_buffer.prj",
    "http://localhost:8000/static/mapretriever/demo/map0/0_buffer.shp",
    "http://localhost:8000/static/mapretriever/demo/map0/0_buffer.shx"
  ];

  var rets = [
    undefined, //dbf
    undefined, //prj
    undefined, //shp
    undefined  //shx
  ]; //dbf

  // async function all_loaded() {
  //   if ((dbfFile !== undefined) &&
  //     (prjFile !== undefined) &&
  //     (shpFile !== undefined) &&
  //     (shxFile !== undefined)) {
  //     [shpFile, dbfFile, prjFile] = await Promise.all(
  //       [
  //         readFilePromise(shpFile, ".shp"),
  //         readFilePromise(dbfFile, ".dbf"),
  //         readFilePromise(prjFile, ".prj"),
  //       ]);
  //   }
  // }

  reqs = [];


  for (let i = 0; i < urls.length; i++) {
    reqs.push(
      new Promise(function (resolve, reject) {
        fetch(urls[i])
          .then(resp => resp.blob())
          .then(blob => {
            let reader = new FileReader();
            if (urls[i].endsWith(".prj")) {
              reader.readAsText(blob);
            }
            else {
              reader.readAsArrayBuffer(blob);
            }
            reader.onload = function () {
              rets[i] = this.result;
              resolve(rets[i]);
            }
          })
      })
    );

  }
  Promise.all(reqs).then(async function (values) {
    let geoJson = null;
    if (rets[0] === undefined) {
      geoJson = shp.combine(
        [
          shp.parseShp(rets[2], rets[1]),
          shp.parseDbf(rets[0])
        ]);
    }
    else {
      geoJson = await shp.parseShp(rets[2], rets[1]);
    }

    // let minLon = geoJson[i]['bbox'][0];
    // let maxLon = geoJson[i]['bbox'][2];

    // let minLat = geoJson[i]['bbox'][1];
    // let maxLat = geoJson[i]['bbox'][3];
  });


}

let featureCounter = 0;

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

// Limit multi-world panning to one world east and west of the real world.
// Geometry coordinates have to be within that range.
const extent = ol.proj.get('EPSG:3857').getExtent().slice();
extent[0] += extent[0];
extent[2] += extent[2];
var map = new ol.Map({
  target: 'map',
  layers: [raster, vector],
  view: new ol.View({
    center: ol.proj.fromLonLat([-97.7459463, 30.2838094]),
    zoom: 18
  })
});

const modify = new ol.interaction.Modify({ source: source });
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
  snap = new ol.interaction.Snap({ source: source });
  map.addInteraction(snap);
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

load_demo0(); 