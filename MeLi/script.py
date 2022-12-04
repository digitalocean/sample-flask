def traducirEstado(estado):
    if estado == "pending":
        estado = "Pendiente"
    elif estado == "handling":
        estado = "manejo"
    elif estado == "ready_to_ship":
        estado = "Listo para Retirar"
    elif estado == "shipped":
        estado = "Enviado"
    elif estado == "delivered":
        estado = "Entregado"
    elif estado == "not_delivered":
        estado = "no entregado"
    elif estado == "cancelled":
        estado = "Cancelado"
    return estado