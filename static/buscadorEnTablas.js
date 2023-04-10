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