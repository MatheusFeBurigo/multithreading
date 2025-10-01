import asyncio
import os
from time import time
import traceback
from urllib import response
from typing import Optional
import aiofiles
from domain.imagem import Imagem
import base64
from datetime import datetime
import httpx

class InmetService:
    def __init__(self):
        self.root = "downloads"
        os.makedirs(self.root, exist_ok=True)

    async def fetch_from_api(url: str, terminal, max_retries: int = 3) -> Optional[str]:
        for tentativa in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url)

                    if(tentativa > 2):
                        await asyncio.sleep(10)
                    else:
                        await asyncio.sleep(1)

                if response.status_code == 200:
                    return response.json().get("base64")
                elif response.status_code == 400:
                    print(f"⚠️ Requisição inválida (400) - não vou tentar de novo: {url}")
                    return None
                else:
                    print(f"❌ Tentativa {tentativa} falhou. Status {response.status_code} para {url} no terminal: {terminal}")

            except Exception as e:
                print(f"❌ Erro na tentativa {tentativa}: {e}")

        return None


    async def save_image(base64_data: str, image_name: str, terminal: str, link: str) -> bool:
        try:
            os.makedirs(f"downloads/{terminal}", exist_ok=True)

            decoded_bytes = base64.b64decode(base64_data.replace("data:image/png;base64,", ""), validate=True)

            async with aiofiles.open(os.path.join("downloads", terminal, f"{image_name}.png"), "wb") as file:
                await file.write(decoded_bytes)

            async with aiofiles.open(os.path.join("downloads", terminal, "list.anexo"), "a", encoding="UTF-8") as anx:
                await anx.write(f"{image_name};{link}\n")

            return True
        except Exception as e:
            print("❌ Erro ao salvar arquivo:", e, terminal)
            traceback.print_exc()
            return False


    async def fetch_data(link_image: str, image_name: str, terminal: str) -> Optional[str]:
        datetime_now = datetime.now().strftime("%Y%m%d")
        link_image = link_image.format(datetime_now=datetime_now)

        base64_data = await InmetService.fetch_from_api(link_image, terminal)

        if base64_data:
            sucesso = await InmetService.save_image(base64_data, image_name, terminal, link_image)
            if sucesso:
                print(f"✅ {image_name} salvo com sucesso para {terminal}")
                return image_name
        else:
            print(f"⛔ Falha ao obter dados para {terminal} - {image_name}")

        return None
