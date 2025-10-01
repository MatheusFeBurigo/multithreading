import asyncio
import os
from service.inmet_service import InmetService as inmet_service
from service.oceanop_service import OceanOpService as oceanop_service

class DataServiceHandler:

    async def handle_data(terminal, area_marinha, marine_area, anexos, fuso, lista_destinatarios):
        marinha_anexos = [i for i in anexos if "marinha" in i["link"]]
        inmets_anexos = [i for i in anexos if "inmet" in i["link"]]
        oceanop_anexos = [i for i in anexos if "https://" not in i["link"]]

        tasks = []

        for anexo in oceanop_anexos:
            tasks.append(
                DataServiceHandler._process_oceanop(anexo, terminal)
            )

        for anexo in inmets_anexos:
            tasks.append(
                inmet_service.fetch_data(anexo["link"], anexo["nome"], terminal)
            )

        await asyncio.gather(*tasks)

    @staticmethod
    async def _process_oceanop(anexo, terminal):
        headers = {"Authorization": await oceanop_service.oAuthenticate(force=False)}
        area_id = await oceanop_service.search_for_area_json(anexo["link"], headers)
        if area_id is not None:
            await oceanop_service.get_pdf(
                headers,
                area_id,
                terminal,
                f"{anexo['nome']}.{anexo['extension']}",
            )
        
