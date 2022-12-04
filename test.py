from scriptGeneral import scriptGeneral

scriptGeneral.enviar_correo(["acciaiomatiassebastian@gmail.com"],"Test html",None,None,"""
        <a href='https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=4857198121733101&redirect_uri=https://whale-app-suwmc.ondigitalocean.app/callbacks'>enlace</a>
""")