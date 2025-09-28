import os
from urllib import response

import aiofiles
from domain.imagem import Imagem
import base64
from datetime import datetime
import httpx

class InmetService:
    def __init__(self):
        self.root = "downloads"
        os.makedirs(self.root, exist_ok=True)

    def fetch_data(link_image, image_name, terminal) -> Imagem | None:
        datetime_now = datetime.now().strftime("%Y%m%d")
        link_template = "https://apiprevmet3.inmet.gov.br/meteograma/4216206/{datetime_now}/00"
        link_image = link_template.format(datetime_now=datetime_now)

        with httpx.Client(timeout=30) as client:
            response = client.get(link_image)
            response.raise_for_status

        try:
            encoded_data = response.json()["base64"]
            decoded_bytes = base64.b64decode(encoded_data.replace("data:image/png;base64,", ""), validate=True)
            with open( os.path.join("downloads", terminal, f"{image_name}.png"), "wb") as file:
                file.write(decoded_bytes)
            with open(os.path.join("downloads", terminal, "list.anexo"), "a", encoding="UTF-8",) as anx:
                anx.write(f"{image_name};{link_image}\n")
            
        except Exception:
            return "Error processing data"
