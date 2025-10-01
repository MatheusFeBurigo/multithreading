import os
import json
import pandas as pd
from datetime import datetime
import aiofiles
import asyncio

class FilesValidade:

    @staticmethod
    async def check_data():
        df = await asyncio.to_thread(pd.read_csv, os.path.join("downloads", "links_anexos_consolidados.csv"), sep=";")
        data = df.to_dict(orient="records")

        hora_atual = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0).hour
        pastas = await asyncio.to_thread(lambda: [nome for nome in os.listdir("downloads") if os.path.isdir(os.path.join("downloads", nome))])
        resultado = {}

        for infos in data:
            terminal = str(infos["TERMINAL"]).strip()
            anexo_raw = str(infos["NOME DO ANEXO"]).strip()
            link = str(infos.get("LINK", "")).strip()
            anexo = os.path.splitext(anexo_raw)[0]

            if "MARINHA" in anexo.upper():
                continue  

            if terminal not in pastas:
                continue

            hora_anexo = int(str(infos["HORÁRIO"]).split(":")[0])

            if hora_atual < 12 and not (0 <= hora_anexo < 12):  
                continue
            if hora_atual >= 12 and not (12 <= hora_anexo < 24): 
                continue

            if terminal not in resultado:
                resultado[terminal] = {
                    "ARQUIVOS_ENCONTRADOS": [],
                    "ARQUIVOS_NAO_ENCONTRADOS": []
                }

            arquivos = await asyncio.to_thread(lambda: [os.path.splitext(arq)[0] for arq in os.listdir(os.path.join("downloads", terminal))])

            if anexo in arquivos:
                if anexo not in resultado[terminal]["ARQUIVOS_ENCONTRADOS"]:
                    resultado[terminal]["ARQUIVOS_ENCONTRADOS"].append(anexo)
            else:
                if not any(d.get("ANEXO") == anexo for d in resultado[terminal]["ARQUIVOS_NAO_ENCONTRADOS"]):
                    resultado[terminal]["ARQUIVOS_NAO_ENCONTRADOS"].append({
                        "ANEXO": anexo,
                        "LINK": link
                    })

        async with aiofiles.open(os.path.join("downloads","resultado.json"), "w", encoding="utf-8") as f:
            await f.write(json.dumps(resultado, indent=4, ensure_ascii=False))

        return resultado

    @staticmethod
    async def create_report():
        resultado = await FilesValidade.check_data()
        report = []

        for terminal, info in resultado.items():
            for item in info["ARQUIVOS_NAO_ENCONTRADOS"]:
                report.append({
                    "TERMINAL": terminal,
                    "ANEXO_NAO_ENCONTRADO": item["ANEXO"],
                    "LINK": item["LINK"]
                })

        if report:
            return report
        return None
