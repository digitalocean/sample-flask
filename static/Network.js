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

  
function fetchGET(url)
{
fetch(url, {
  method: 'GET',
})
  .then(response => {
    if (response.status === 200) {
      return response
    } else {
      return null;
    }
  });
}

async function fetchPOST(url,JsonString)
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify()
  })
    .then(response => {
      if (response.status === 200) {
        return response
      } else {
        alert(`Se ha producido un error de red`);
      }
    });