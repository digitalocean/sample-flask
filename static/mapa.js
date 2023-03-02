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
}
async function getJSON(url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.responseType = 'json';
  xhr.onload = await function() {
    var status = xhr.status;
    if (status === 200) {
      callback(null, xhr.response);
      var listasParaRetirar = 0;
      var retirados = 0;
      var sectorizados = 0
      for(var i in globales.markers){
        if(globales.markers[i].estado == "Lista Para Retirar"){
          listasParaRetirar ++
        }else if((globales.markers[i].estado == "Retirado")){
          retirados ++
        }else if((globales.markers[i].estado == "Listo para salir (Sectorizado)")){
          sectorizados ++
        }
      }
      document.getElementById("contadores").outerHTML = `<div id='contadores'>
      <h1><a href="/logistica/ruteo"><input type="button" value="Ver en lista" class="boton"></a> ${listasParaRetirar} Para Retirar || ${retirados} Retirados || ${sectorizados} Sectorizados</h1>
      </div>`
      
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
        var tipoEnvio = data[x]["tipoEnvio"];
        var cp = data[x]["CP"];
        var bultos = data[x]["bultos"];
        var cobrar = data[x]["cobrar"]
        ultimoEstado = fechaUltimoEstado + " " + horaUltimoEstado;
        addPoint(jsonEnvio,jsonLatitud,jsonLongitud,jsonDir,jsonLoc,jsonChofer,jsonEstado,jsonZona,jsonFecha,jsonVendedor,jsonmotivo,ultimoEstado,tipoEnvio,cp,bultos,cobrar)
      }  
    }
  });
}


function modificarDatos(numEnvio,dir,loc,vend,est,cobrar) {
    window.open("/formularioEdicionLogistica?direccion=" + dir + "&localidad=" + loc + "&vendedor=" + vend + "&numeroEnvio=" + numEnvio + "&cobrar=" + cobrar + "&estado=" + est,'_blank', 'modal=true,height=400,width=300');
  }

let iniciales = ["C","N", "O", "S"];
let options = "";

for (let i = 0; i < iniciales.length; i++) {
    for (let j = 1; j <= 15; j++) {
      
      if(j < 10){
        options += "<option value='" + iniciales[i] + " 0" + j + "'>" + iniciales[i] + " 0" + j + "</option>";
      }else{
        options += "<option value='" + iniciales[i] + " " + j + "'>" + iniciales[i] + " " + j + "</option>";
      }
    }
}
  
function addPoint(nro_env,lati,lng,dir,loc,chofer,est,zona,fecha,vendedor,motivo,ult_estado,tipo_envio,cp,bultos,cobrar){
    const marker = new google.maps.Marker({
      Paquete:nro_env,
      estado:est,
      direccion:dir,
      localidad:loc,
      vendedor:vendedor,
      zona:zona,
      tipoEnvio:tipo_envio,
      cp:cp,
      bultos:bultos,
      position: { lat: parseFloat(lati), lng:  parseFloat(lng)},
      icon: getPinIcon(zona),
      map: map,
    });
var contenido = "<p>Envio: "+nro_env+
"<br>Fecha: "+fecha+
"<br>Ultima actualizacion: "+ult_estado+
"<br>Direccion: "+dir+", "+loc+
"<br>CP: "+cp+
" <br> Vendedor: " + vendedor + 
"<br>Chofer: "+chofer+
"<br>Estado: "+est+
"<br>Motivo: " + motivo+
"<br>Monto a cobrar: $" + cobrar +
`<br><button onclick="modificarDatos('`+nro_env+"','"+dir+"','"+loc+"','"+vendedor+"','"+est+"','"+cobrar+`')">Modificar</button>`

if(est == "Lista Para Retirar"){
  contenido = contenido + `<button onclick="noVino('`+nro_env+`')">No Vino</button>`
}
contenido = contenido + 
`<form action='/bultosporenvio' method='POST'>
Bultos: <select name='bultos' id='bultos'>
  <option value=${bultos}>${bultos}</option>
  <option value=1>1</option>
  <option value=2>2</option>
  <option value=3>3</option>
  <option value=4>4</option>
  <option value=5>5</option>
  <option value=6>6</option>
</select><input type='submit' value='Guardar'>
<input type='hidden' value="${nro_env}" name='envio' id='envio'>
</form></p>
<form action='/cambiartipoenvio' method='POST'>
Pasar a: <select name='tipoEnvio' required>
<option value=""></option>
  <option value=2>Flexs</option>
  <option value=13>Recorrido</option>
  <option value=15>Chips</option>
</select><input type='submit' value='Guardar'></input>
<input type='hidden' value="${nro_env}" name='envio' id='envio'>
</form></p>`



contenido = contenido + 
"<form action='/cambiozona' method='POST'><select name='zona' id='zona'>"+
"<option value='"+zona+"' selected disabled hidden>"+zona+"</option>"+
"<option value='null'>Limpiar zona</option>"+
options+
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


function geolocalizarFaltantes()
{
fetch('/descargalogixs', {
  method: 'GET',
})
  .then(response => {
    if (response.status === 200) {
      alert("Geolocalizacion exitosa")
    } else {
      alert('Se ha producido un error');
    }
  });

}



function clearPolygon(){
  document.getElementById("mensaje").outerHTML = "<div id='mensaje'></div>"
  poligonoZonificador.setMap(null);
  asignaciones = [];
  globales.polygonLocations = []
  for (var i = 0; i < globales.markers.length; i++){
    globales.markers[i].setIcon(getPinIcon(globales.markers[i].zona))
  }
}

function borrarPoligonoYpintarSeleccionado(zon){
  document.getElementById("mensaje").outerHTML = "<div id='mensaje'></div>"
  poligonoZonificador.setMap(null);
  for (var i = 0; i < globales.markers.length; i++){
    for(var e = 0; e < asignaciones.length; e++){
      if (asignaciones[e].Paquete == globales.markers[i].Paquete){
        globales.markers[i].zona = zon;
        globales.markers[i].setIcon(getPinIcon(zon));
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


function zonificarOne(envio,zona){
  var zona = document.getElementById("zonamasiva").value;
  $.ajax({
    url:'/cambiozona',
    type:'post',
    data: {nEnvio: envio, zona: zona},
    success:function(){
    }
  });
}


function zonificar(){
  var zona = document.getElementById("zonamasiva").value;
  document.getElementById("enviosAzonificar").outerHTML = asignacionesToString();
  document.getElementById("mensaje").outerHTML = "<div id='mensaje'><h3>" + asignaciones.length + " Asignados a " + zona + "</h3></div>"
  for (var i;i < globales.markers.length; i++) {
    // @see https://developers.google.com/maps/documentation/javascript/examples/poly-containsLocation
    if (google.maps.geometry.poly.containsLocation(globales.markers[i].position, poligonoZonificador)) {

        if (globales.markers[i].visible) {
          globales.markers[i].setIcon(getPinIcon(zona))
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



function getPinIcon(zona){
  var icon = "";
  if (zona != null){
    if(zona.includes("~En Deposito")){
      icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|000000");
      return icon;
      }else{
    var zn = zona.substring(2, 4);
    switch (zn) {
      case "01":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|FF0000");
        return icon;
      case "02":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|00FF00");
        return icon;
      case "03":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|0000FF");
        return icon;
      case "04":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|F5A623");
        return icon;
      case "05":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|00FFFF");
        return icon;
      case "06":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|FF00FF");
        return icon;
      case "07":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|800000");
        return icon;
      case "08":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|008000");
        return icon;
      case "09":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|000080");
        return icon;
      case "10":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|FF7F50");
        return icon;
      case "11":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|FF0000");
        return icon;
      case "12":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|800080");
        return icon;
      case "13":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|B22222");
        return icon;
      case "14":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|591d47");
        return icon;
      case "15":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|00FFFF");
        return icon;
      case "16":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|FF00FF");
        return icon;
      case "17":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|800000");
        return icon;
      case "18":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|008000");
        return icon;
      case "19":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|000080");
        return icon;
      case "20":
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|808000");
        return icon;
      default:
        icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|FF7F50")
      return icon; 
    }
  }
  }
  else{
    return new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|F3FF33")
  }
  
}

