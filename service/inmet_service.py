import os
import traceback
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

    async def fetch_data(link_image, image_name, terminal) -> Imagem | None:
        datetime_now = datetime.now().strftime("%Y%m%d")
        link_image = link_image.format(datetime_now=datetime_now)

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(link_image)

            if response.status_code == 200:
                response.raise_for_status()
                try:
                    os.makedirs(f"downloads/{terminal}", exist_ok=True)

                    encoded_data = response.json()["base64"]
                    decoded_bytes = base64.b64decode(encoded_data.replace("data:image/png;base64,", ""), validate=True)
                    async with aiofiles.open( os.path.join("downloads", terminal, f"{image_name}.png"), "wb") as file:
                        await file.write(decoded_bytes)
                    async with aiofiles.open (os.path.join("downloads", terminal, "list.anexo"), "a", encoding="UTF-8",) as anx:
                        await anx.write(f"{image_name};{link_image}\n")

                except Exception as e:
                    print("❌ Erro capturado:", e, terminal)
                    traceback.print_exc()
                    return f"Error processing data: {e.__class__.__name__} - {e}"
                
            if response.status_code == 400:
                print(f"⚠️ Requisição inválida (400) para link: {link_image}")
                return None
