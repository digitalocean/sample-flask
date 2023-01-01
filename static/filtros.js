// enDeposito
// enCamino
// noEntregado
// entregado

var paraRetirar = document.getElementById('listaParaRetirar')
paraRetirar.addEventListener('change', function() {
    for (var i = 0; i < globales.markers.length; i++) 
            {
        if (globales.markers[i].estado === "Lista Para Retirar")
            {
                if (paraRetirar.checked) {
                    globales.markers[i].setVisible(true);
                  } else {
                    globales.markers[i].setVisible(false);
                  }}}});

var retirado = document.getElementById('retirado')
retirado.addEventListener('change', function() {
    for (var i = 0; i < globales.markers.length; i++) 
            {
        if (globales.markers[i].estado === "Retirado")
            {
                if (retirado.checked) {
                    globales.markers[i].setVisible(true);
                } else {
                    globales.markers[i].setVisible(false);
                }}}});
                
var enDeposito = document.getElementById('enDeposito')
enDeposito.addEventListener('change', function() {
    for (var i = 0; i < globales.markers.length; i++) 
            {
        if ((globales.markers[i].estado === "Listo para salir (Sectorizado)")
            || ((!globales.markers[i].zona == null) 
                && globales.markers[i].zona === "~En Deposito"))
            {
                if (enDeposito.checked) {
                    globales.markers[i].setVisible(true);
                } else {
                    globales.markers[i].setVisible(false);
                }}}});