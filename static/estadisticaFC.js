function searchColumn(numeroColumna){
  console.log()
}


function showSelect() {
    var select = document.getElementById("mySelect");
    select.size = 3;
  }
  function hideSelect() {
    var select = document.getElementById("mySelect");
    select.size = 1;
  }
  function filterOptions() {
    // Obtiene el valor del input de búsqueda
    var input, filter, options, texto;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    
    // Obtiene las opciones del select
    options = document.getElementById("mySelect").options;
    
    // Recorre las opciones y las oculta si no contienen la palabra buscada
    for (var i = 0; i < options.length; i++) {
      texto = options[i].textContent.toUpperCase();
      if (texto.indexOf(filter) > -1) {
        options[i].style.display = "";
      } else {
        options[i].style.display = "none";
      }
    }
  }