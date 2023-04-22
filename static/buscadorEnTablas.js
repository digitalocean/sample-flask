// filtra en la tabla entera
function searchTable() {
  // Obtener el valor de búsqueda ingresado por el usuario
  var input = document.getElementById("searchInput").value;
  // Obtener todas las filas de la tabla
  var rows = document.getElementById("myTable").getElementsByTagName("tr");

  // Recorrer cada fila
  for (var i = 1; i < rows.length; i++) {
    // Obtener todas las celdas de la fila actual
    var cells = rows[i].getElementsByTagName("td");
    var found = false;
    // Recorrer cada celda
    for (var j = 0; j < cells.length; j++) {
      // Comparar el valor de la celda con el valor de búsqueda
      if (cells[j].innerHTML.toLowerCase().indexOf(input.toLowerCase()) > -1) {
        found = true;
      }
    }
    if (found) {
      rows[i].style.display = "";
    } else {
      rows[i].style.display = "none";
    }
  }
}

// funcion para buscar por columna
function searchColumn(numeroColumna, idInput) {
  var input = document.getElementById(idInput).value;
  // Obtener todas las filas de la tabla
  var rows = document.getElementById("myTable").getElementsByTagName("tr");
  // Recorrer cada fila
  for (var i = 1; i < rows.length; i++) {
    var displayStyle = window.getComputedStyle(rows[i]).getPropertyValue("display");
    // Obtener todas las celdas de la fila actual
    var cells = rows[i].getElementsByTagName("td");
    var found = false;
    // Recorrer cada celda
    if (cells[numeroColumna].innerHTML.toLowerCase().indexOf(input.toLowerCase()) > -1) {
      found = true;
    }
    if (found) {
      rows[i].style.display = "";
    } else {
      rows[i].style.display = "none";
    }
  }
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