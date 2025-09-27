import asyncio
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

        await asyncio.gather(*tasks)

        for anexo in inmets_anexos:
            inmet_service.fetch_data(
                link_image=anexo["link"],
                image_name=anexo["nome"],
                terminal=terminal,
            )

    @staticmethod
    async def _process_oceanop(anexo, terminal):
        area_id = await oceanop_service.search_for_area_json(anexo["link"])
        if area_id is not None:
            await oceanop_service.get_pdf(
                area_id,
                terminal,
                f"{anexo['nome']}.{anexo['extension']}",
            )

