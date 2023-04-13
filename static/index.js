function nuevaVentana(url,height,width) {
    var nuevaVentana = window.open(url,'_blank', 'modal=true,height='+height+',width='+width);
    nuevaVentana.onload = function() {
        nuevaVentana.document.getElementById('barra').style.display = 'none';
      }
  }


function confirmRedirect(url) {
    if (confirm("¿Estás seguro de que quieres redirigir a esta URL?")) {
    window.location.href = url;
    }
}
function redirect(url,param=null){
    if (param != null) {
        url += param.toString();
    }
    window.location.href = url;
}