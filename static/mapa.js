const ruta = location.protocol + "//" + location.host 

var map;
var asignaciones = [];
var poligonoZonificador
var globales = {
  markers :[],
  GrupoVendedores : [],
  polygon:[],
  polygonMarkers : [],
  polygonLocations : []
} 


function initMap() {
  globales.markers = []
  const mapOptions = {
    zoom: 10,
    center: { lat: -34.640211, lng:  -58.480778}
  };

  map = new google.maps.Map(document.getElementById("map"), mapOptions);
  const TrafficLayer = new google.maps.TrafficLayer();
  TrafficLayer.setMap(map);

  poligonoZonificador = new google.maps.Polygon(
    { paths: globales.polygonLocations,
    strokeColor: '#FF0000',
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: '#efe653',
    fillOpacity: 0.35,
    editable: true,
    map: map });


  google.maps.event.addListener(map, 'click', function (e) {
                
      // set a marker there, with a small measle icon
      var position = e.latLng;
      globales.polygonLocations.push(position);
      globales.polygonMarkers.push(new google.maps.Marker({
          icon: 'https://maps.gstatic.com/intl/en_ALL/mapfiles/markers2/measle.png',
          position: position,
          map: map
      }));
      // now let's add a globales.polygon
      drawPolygon(globales.polygonLocations);
  });
actualizarMapa();
}





function AddAsignacionesSiNoExiste(marker) {
  for (var i = 0; i < asignaciones.length; i++) {
      if (asignaciones[i].Paquete == marker.Paquete) {
          return;
      }
  }
  asignaciones.push(marker);
}
////////////////////////////////////////////////////////
// var polygon = new google.maps.Polygon();
function drawPolygon(points) {
  if (points.length < 3) {
      return;
  }
  // first delete the previous polygon
  if (poligonoZonificador) {
    poligonoZonificador.setMap(null);
  }
  // @see https://developers.google.com/maps/documentation/javascript/examples/polygon-simple
  poligonoZonificador = new google.maps.Polygon({
      paths: points,
      strokeColor: '#FF0000',
      strokeOpacity: 1,
      strokeWeight: 4,
      fillColor: '#efe653',
      fillOpacity: 0.35,
      editable: true,
      map: map
  });


  var place_polygon_path = poligonoZonificador.getPath();
  google.maps.event.addListener(place_polygon_path, 'set_at', polygonChanged);
  google.maps.event.addListener(place_polygon_path, 'insert_at', polygonChanged);
  // display to input
  displaySelectedMarkers(poligonoZonificador);
}


function polygonChanged() {
  displaySelectedMarkers(poligonoZonificador);
}

function displaySelectedMarkers(polygon) {
  // empty the input
  asignaciones = [];
  var contador = 0;
  for (var i in globales.markers) {
      // @see https://developers.google.com/maps/documentation/javascript/examples/poly-containsLocation
      if (google.maps.geometry.poly.containsLocation(globales.markers[i].position, polygon)) {

          if (globales.markers[i].visible) {
            globales.markers[i].setIcon(new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|EF2A00"));
            AddAsignacionesSiNoExiste(globales.markers[i]);
            document.getElementById("mensaje").outerHTML = "<div id='mensaje'><h3>" + asignaciones.length + " seleccionados</h3></div>"

          }
          
      }
    else {
        globales.markers[i].setIcon(getPinIcon(globales.markers[i].zona,globales.markers[i].estado))
      }    
  }
  for (var i = 0;  i < asignaciones.length; i++){
    contador = contador + 1
  }
}
async function getJSON(url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.responseType = 'json';
  xhr.onload = await function() {
    var status = xhr.status;
    if (status === 200) {
      callback(null, xhr.response);
    } else {
      console.log("ERROR EN RESPUESTA JSON")
      callback(status, xhr.response);
    }
  };
  xhr.send();
};

function numeroZona(zona){
  var zn = toString(zona).substring(2,3);
  return zn
}
 function actualizarMapa()
{
  getJSON(ruta + "/logistica/jsonPendientes",
    function(err, data) {
    if (err !== null) {
    alert('Something went wrong: ' + err);
    } 
    else 
    {
    for(x in data){
        var jsonEnvio = x;
        var jsonLatitud = data[x]["latitud"];
        var jsonLongitud = data[x]["longitud"];
        var jsonDir = data[x]["direccion"];
        var jsonLoc = data[x]["localidad"];
        var jsonFecha = data[x]["fecha"];
        var jsonChofer = data[x]["chofer"];
        var jsonEstado = data[x]["estado_envio"];
        var jsonZona = data[x]["zona"];
        var jsonVendedor = data[x]["vendedor"];
        var jsonmotivo = data[x]["motivo"];
        var fechaUltimoEstado = new Date()
        fechaUltimoEstado = data[x]["fechaUltimoEstado"];
        var horaUltimoEstado = data[x]["horaUltimoEstado"];
        var tipoEnvio = data[x]["tipoEnvio"]
        ultimoEstado = fechaUltimoEstado + " " + horaUltimoEstado;
        addPoint(jsonEnvio,jsonLatitud,jsonLongitud,jsonDir,jsonLoc,jsonChofer,jsonEstado,jsonZona,jsonFecha,jsonVendedor,jsonmotivo,ultimoEstado,tipoEnvio)
      }  
    }
  });
}


function modificarDatos(numEnvio,dir,loc,vend,est) {
    window.open("/formularioEdicionLogistica?direccion=" + dir + "&localidad=" + loc + "&vendedor=" + vend + "&numeroEnvio=" + numEnvio + "&estado=" + est,'_blank', 'modal=true,height=400,width=300');
  }

  
function addPoint(nro_env,lati,lng,dir,loc,chofer,est,zona,fecha,vendedor,motivo,ult_estado,tipo_envio){
    const marker = new google.maps.Marker({
      Paquete:nro_env,
      estado:est,
      direccion:dir,
      localidad:loc,
      vendedor:vendedor,
      zona:zona,
      tipoEnvio:tipo_envio,
      position: { lat: parseFloat(lati), lng:  parseFloat(lng)},
      icon: getPinIcon(zona,est),
      map: map,
    });
var contenido = "<p>Envio: "+nro_env+
"<br>Fecha: "+fecha+
"<br>Ultima actualizacion: "+ult_estado+
"<br>Direccion: "+dir+", "+loc+
" <br> Vendedor: " + vendedor + 
"<br>Chofer: "+chofer+
"<br>Estado: "+est+
"<br>Motivo: " + motivo+
`<br><button onclick="modificarDatos('`+nro_env+"','"+dir+"','"+loc+"','"+vendedor+"','"+est+`')">Modificar</button>`+
"<form action='/cambiozona' method='POST'><select name='zona' id='zona'>"+
"<option value='"+zona+"' selected disabled hidden>"+zona+"</option>"+
"<option value='null'>Limpiar zona</option>"+
"<option value='C 01'>C 01</option>"+
"<option vzalue='C 02'>C 02</option>"+
"<option value='C 03'>C 03</option>"+
"<option value='C 04'>C 04</option>"+
"<option value='C 05'>C 05</option>"+
"<option value='C 06'>C 06</option>"+
"<option value='C 07'>C 07</option>"+
"<option value='C 08'>C 08</option>"+
"<option value='C 09'>C 09</option>"+
"<option value='C 10'>C 10</option>"+
"<option value='C 11'>C 11</option>"+
"<option value='C 12'>C 12</option>"+
"<option value='C 13'>C 13</option>"+
"<option value='C 14'>C 14</option>"+
"<option value='C 15'>C 15</option>"+
"<option value='N 01'>N 01</option>"+
"<option value='N 02'>N 02</option>"+
"<option value='N 03'>N 03</option>"+
"<option value='N 04'>N 04</option>"+
"<option value='N 05'>N 05</option>"+
"<option value='N 06'>N 06</option>"+
"<option value='N 07'>N 07</option>"+
"<option value='N 08'>N 08</option>"+
"<option value='N 09'>N 09</option>"+
"<option value='N 10'>N 10</option>"+
"<option value='N 11'>N 11</option>"+
"<option value='N 12'>N 12</option>"+
"<option value='N 13'>N 13</option>"+
"<option value='N 14'>N 14</option>"+
"<option value='N 15'>N 15</option>"+
"<option value='O 01'>O 01</option>"+
"<option value='O 02'>O 02</option>"+
"<option value='O 03'>O 03</option>"+
"<option value='O 04'>O 04</option>"+
"<option value='O 05'>O 05</option>"+
"<option value='O 06'>O 06</option>"+
"<option value='O 07'>O 07</option>"+
"<option value='O 08'>O 08</option>"+
"<option value='O 09'>O 09</option>"+
"<option value='O 10'>O 10</option>"+
"<option value='O 11'>O 11</option>"+
"<option value='O 12'>O 12</option>"+
"<option value='O 13'>O 13</option>"+
"<option value='O 14'>O 14</option>"+
"<option value='O 15'>O 15</option>"+
"<option value='S 01'>S 01</option>"+
"<option value='S 02'>S 02</option>"+
"<option value='S 03'>S 03</option>"+
"<option value='S 04'>S 04</option>"+
"<option value='S 05'>S 05</option>"+
"<option value='S 06'>S 06</option>"+
"<option value='S 07'>S 07</option>"+
"<option value='S 08'>S 08</option>"+
"<option value='S 09'>S 09</option>"+
"<option value='S 10'>S 10</option>"+
"<option value='S 11'>S 11</option>"+
"<option value='S 12'>S 12</option>"+
"<option value='S 13'>S 13</option>"+
"<option value='S 14'>S 14</option>"+
"<option value='S 15'>S 15</option>"+
"</select><input type='submit' value='Guardar'>"+
"<input type='hidden' value="+nro_env+" name='envio' id='envio'>"+
"</form></p>"
    const infowindow = new google.maps.InfoWindow({
      content:contenido,
     });
     
    google.maps.event.addListener(marker, "click", () => {
      infowindow.open(map, marker);
    });
    globales.markers.push(marker);
}



function clearPolygon(){
  document.getElementById("mensaje").outerHTML = "<div id='mensaje'></div>"
  poligonoZonificador.setMap(null);
  asignaciones = [];
  globales.polygonLocations = []
  for (var i = 0; i < globales.markers.length; i++){
    globales.markers[i].setIcon(getPinIcon(globales.markers[i].zona,globales.markers[i].estado))
  }
}

function borrarPoligonoYpintarSeleccionado(zon){
  document.getElementById("mensaje").outerHTML = "<div id='mensaje'></div>"
  poligonoZonificador.setMap(null);
  for (var i = 0; i < globales.markers.length; i++){
    for(var e = 0; e < asignaciones.length; e++){
      if (asignaciones[e].Paquete == globales.markers[i].Paquete){
        globales.markers[i].zona = zon;
        globales.markers[i].setIcon(getPinIcon(zon,globales.markers[i].estado));
      }
    }
    
  }
  asignaciones = [];
  globales.polygonLocations = []
}

function asignacionesToString(){
  
  var envios = "<input type='hidden' name='enviosAzonificar' id='enviosAzonificar' value='";
  for (var i = 0;i < asignaciones.length;i++){
    envios = envios + asignaciones[i].Paquete+","
  }
  if(asignaciones.length<1){
    envios = envios.substring(0, envios.length - 1);
  }
  envios = envios.slice(0,-1) + "'></input>";
  return envios;
}


function zonificar(){
  var zona = document.getElementById("zonamasiva").value;
  document.getElementById("enviosAzonificar").outerHTML = asignacionesToString();
  document.getElementById("mensaje").outerHTML = "<div id='mensaje'><h3>" + asignaciones.length + " Asignados a " + zona + "</h3></div>"
  for (var i;i < globales.markers.length; i++) {
    // @see https://developers.google.com/maps/documentation/javascript/examples/poly-containsLocation
    if (google.maps.geometry.poly.containsLocation(globales.markers[i].position, poligonoZonificador)) {

        if (globales.markers[i].visible) {
          globales.markers[i].setIcon(getPinColor(zona,""))
          AddAsignacionesSiNoExiste(globales.markers[i]);
          document.getElementById("mensaje").outerHTML = "<div id='mensaje'><h3>" + asignaciones.length + " seleccionados</h3></div>"

        }
      }
    }
  $.ajax({
    url:'/logistica/cambiozonamasivo',
    type:'post',
    data:$('#formzona').serialize(),
    success:function(){
    }
  });
  borrarPoligonoYpintarSeleccionado(zona)
}

async function actualizarViajes(){
  $.ajax({
    url:'/descargalogixs',
    type:'get',
    success:function(){
        console.log("worked");
    }
  });
}


function getPinIcon(zona,est){
  var icon = "";
  if (est == "Entregado" || est == "No entregado" ||  est == "No Entregado" || est == "En Camino" || zona === null){
    icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + getPinColor(est))
    return(icon)
  }
  // Rojo: #FF0000
  // Verde: #00FF00
  // Azul: #0000FF
  // Amarillo: #FFFF00
  // Naranja: #FFA500
  // Morado: #800080
  // Rosa: #FF00FF
  // Marrón: #A52A2A
  // Gris: #808080
  // Verde claro: #00FF7F
  var zn = zona.charAt(3)
  switch (zn) {
    case "1":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|CFCFCF");
      return icon;
    case "2":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|AEAEAE");
      return icon;
    case "3":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|D69EDF");
      return icon;
    case "4":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|4E9AFC");
      return icon;
    case "5":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|159713");
      return icon;
    case "6":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|A2FA3A");
      return icon;
    case "7":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|1aabbb");
      return icon;
    case "8":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|2bbccc");
      return icon;
    case "9":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|3ccddd");
      return icon;
    case "0":
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|4ddeee");
      return icon;

    default:
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + getPinColor(est))
    return icon;
  }
  
}


function getPinColor(estado) {
    var color = "";
    switch (estado) {
        case "Entregado":
          color = "E4E1B2";
          break;
        case "Lista Para Retirar":
          color = "F3FF33";//amarillo
          break;
        case "Listo para Retirar":
          color = "F3FF33";//amarillo
          break;
        case "Listo para salir (Sectorizado)":
          color = "A4A16E";
          break;
        case " Listo para salir (Sectorizado)":
            color = "A4A16E";
            break;
        case "En Camino":
          color = "2A9B08";//verde
          break;
        case "Reasignado":
          color = "2A9B08";//verde
          break;
        case "No entregado":
          color = "ff0000";//rojo
          break;
        case "Retirado":
          color = "8a2be2";//
          break;
          // "4c2882";//naranja
        default:
          color = "FFA500";//
}
    return color;

}
