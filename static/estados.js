
function noVino(nro_env)
{
fetch(`/logistica/mapa/novino`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ nro_envio: nro_env })
})
  .then(response => {
    if (response.status === 200) {
      console.log(`${nro_env} No Vino`)
      initMap()
    } else {
      alert(`Se ha producido un error con ${nro_env}`);
    }
  });
}

function cancelado(nro_env)
{
    if (confirm("¿seguro que es el envio "+nro_env+" esta cancelado?")) {
        fetch(`/logistica/mapa/cancelado`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nro_envio: nro_env })
        })
  .then(response => {
    if (response.status === 200) {
      console.log(`${nro_env} Cancelado`)
      alert(`${nro_env} Cancelado`);
    } else {
      alert(`Se ha producido un error con ${nro_env}`);
    }
  });
}
}

function fueraDeZona(nro_env)
{
    if (confirm("¿seguro que es el envio "+nro_env+" es fuera de zona?")) {
fetch(`/logistica/mapa/fueradezona`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ nro_envio: nro_env })
})
  .then(response => {
    if (response.status === 200) {
      console.log(`${nro_env} Fuera de Zona`)
      alert(`${nro_env} Fuera de zona`);
    } else {
      alert(`Se ha producido un error con ${nro_env}`);
    }
  });
}
}