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




document.getElementById('search').addEventListener('input', function() {
    // Obtén el valor del cuadro de texto
    var searchValue = this.value;
    // Itera a través de todos los marcadores y oculta aquellos que no coinciden con la búsqueda del usuario
    for (var i = 0; i < globales.markers.length; i++) {
        if (
            (globales.markers[i].Paquete.toLowerCase().indexOf(searchValue.toLowerCase()) === -1)
        && (globales.markers[i].direccion.toLowerCase().indexOf(searchValue.toLowerCase()) === -1) 
        && (globales.markers[i].localidad.toLowerCase().indexOf(searchValue.toLowerCase()) === -1)
        && (globales.markers[i].vendedor.toLowerCase().indexOf(searchValue.toLowerCase()) === -1)) {
        globales.markers[i].setVisible(false);
        } else {
        globales.markers[i].setVisible(true);
        }
    }
    });