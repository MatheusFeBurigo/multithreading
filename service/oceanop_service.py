from glob import glob
import json
import os
import aiofiles
import httpx

class OceanOpService:

    async def oAuthenticate(self, force=False):
        token_file = "downloads/oceanop_token.txt"
        btoken = [] if force else glob(token_file)
        username = os.getenv("OCEANOP_USER")
        password = os.getenv("OCEANOP_PASSWORD")

        if len(btoken) == 1:
            async with aiofiles.open(btoken[0], "r") as f:
                oauth_token = json.loads(await f.read())
            return f"{oauth_token['token_type']} {oauth_token['access_token']}"

        url = "https://petrobras.ttforecast.com.br/api/v1/login/oauth"
        payload = {
            "username": username,
            "password": password,
        }

        with httpx.Client(timeout=30) as client:
            response = client.post(url, data=payload)

        if response.status_code == 200:
            data = response.json()
            async with aiofiles.open("downloads/oceanop_token.txt", "w") as f:
                await f.write(json.dumps(data, indent=4))
            return f"{data['token_type']} {data['access_token']}"
        return None

    async def search_for_area_json(area, force=False):
        data_areas = glob("downloads/oceanop_areas.json")
        if len(data_areas) == 0 or force:
            areas = await OceanOpService._get_areas(force)
            if areas is None:
                return None
        else:
            async with aiofiles.open("downloads/oceanop_areas.json", "r") as f:
                areas = json.loads(await f.read())

        return [a["id"] for a in areas if a["name"] == area][0]

    async def get_pdf(area_id, terminal, name_report, force=False):
        url = f"https://petrobras.ttforecast.com.br/api/v1/bulletins/{area_id}/pdf"
        headers = {"Authorization": await OceanOpService.oAuthenticate(force)}

        with httpx.Client(timeout=60) as client:
            response = client.get(url, headers=headers)
            
        if response.status_code == 200:
            os.makedirs(f"downloads/{terminal}", exist_ok=True)
            file_path = f"downloads/{terminal}/{name_report}"

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(response.content)

            async with aiofiles.open(
                f"downloads/{terminal}/list.anexo", "a", encoding="utf-8"
            ) as f:
                await f.write(f"{name_report};{url}\n")
        else:
            self.get_pdf(area_id, terminal, name_report, force=True)

    async def _get_areas(force):
        url = "https://petrobras.ttforecast.com.br/api/v1/areas/ids"
        headers = {"Authorization": await OceanOpService.oAuthenticate(force)}

        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers)

        if response.status_code == 200:
            response = response.json()
            async with aiofiles.open("/downloads/oceanop_areas.json", "w") as f:
                await f.write(json.dumps(response, indent=4))
            return response
        elif response.status_code == 403:
            return OceanOpService._get_areas(await OceanOpService.oAuthenticate(force=True))
        return None
