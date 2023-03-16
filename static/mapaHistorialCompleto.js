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


 function actualizarMapa()
{
  getJSON(ruta + "/historial/mapa",
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
        ultimoEstado = fechaUltimoEstado + " " + horaUltimoEstado;
        addPoint(jsonEnvio,jsonLatitud,jsonLongitud,jsonDir,jsonLoc,jsonChofer,jsonEstado,jsonZona,jsonFecha,jsonVendedor,jsonmotivo,ultimoEstado)
      }  
    }
  });
}
function addPoint(nro_env,lati,lng,dir,loc,chofer,est,zona,fecha,vendedor,motivo,ult_estado){
    const marker = new google.maps.Marker({
      Paquete:nro_env,
      estado:est,
      zona:zona,
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
"<br>Motivo: " + motivo +
"<br>Zona: "+zona
    const infowindow = new google.maps.InfoWindow({
      content:contenido,
     });
     
    google.maps.event.addListener(marker, "click", () => {
      infowindow.open(map, marker);
    });
    globales.markers.push(marker);
}



function getPinIcon(zona,est){
  var icon = "";
  if (est == "Entregado" || est == "No entregado" ||  est == "No Entregado" || est == "En Camino" || zona === null){
    icon = new google.maps.MarkerImage("https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + getPinColor(est))
    return(icon)
  }
  
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