import asyncio
from datetime import datetime
from glob import glob
import json
import os

import aiofiles

from service.data_service_handler import DataServiceHandler as data_service_handler

class FactoryData:
    async def organize_data():
        fuso = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        json_files = glob(os.path.join("downloads", f"TERMINAIS_{fuso.hour:02d}", "*.json"))

        tasks = []
        for file_path in json_files:
            tasks.append(FactoryData.process_file(file_path, fuso))

        await asyncio.gather(*tasks)
    
    async def process_file(file_path, fuso):
        async with aiofiles.open(file_path, encoding="utf8") as f:
            content = await f.read()
            item = json.loads(content)

        await data_service_handler.handle_data(
            item["terminal"],
            item["area_marinha"],
            item["marine_area"],
            item["anexos"],
            fuso,
            item["list_email"],
        )
