function nuevaVentana(url,height,width) {
    var nuevaVentana = window.open(url,'_blank', 'modal=true,height='+height+',width='+width);
    nuevaVentana.onload = function() {
        nuevaVentana.document.getElementById('barra').style.display = 'none';
      }
  }