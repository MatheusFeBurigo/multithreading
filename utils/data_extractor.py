import json
import os
from os import makedirs
from unidecode import unidecode
import pandas as pd
import aiofiles
import asyncio
from concurrent.futures import ProcessPoolExecutor

class DataExtractor:

    @staticmethod
    def aggroup_itens(key, dicionario):
        tmp = {}
        for d in dicionario:
            chave = f"{d['terminal']}-{key}"
            if chave in tmp:
                tmp[chave]["anexos"].extend(d["anexos"])
            else:
                tmp[chave] = d
        return list(tmp.values())

    @staticmethod
    async def generate_file(horario, arr_json_files):
        dir_save = os.path.join("downloads", f"TERMINAIS_{horario}")
        makedirs(dir_save, exist_ok=True)
        for arr in arr_json_files:
            filename = unidecode(arr["terminal"].split(" - ")[0].replace(" ", "_"))
            arr["list_email"] = DataExtractor.get_emails(arr["terminal"])
            async with aiofiles.open(
                os.path.join(dir_save, f"{filename}.json"), "w", encoding="utf8"
            ) as f:
                await f.write(json.dumps(arr, indent=4))

    @staticmethod
    def get_emails(terminal):
        with open("downloads/destinatarios.csv", encoding="utf-8") as f:
            lines_dest = f.readlines()
        lines_dest = [ld.replace("\n", "").split(";") for ld in lines_dest]
        for l in lines_dest:
            if l[0].strip() == terminal.strip():
                return l[1].split(",")

    @staticmethod
    def convert_to_csv():
        df = pd.read_excel('downloads/links_anexos_consolidados_novo 1.xlsx', sheet_name=0)
        df_destinatarios = pd.read_excel('downloads/links_anexos_consolidados_novo 1.xlsx', sheet_name=1)
        filename_save = os.path.join('downloads', 'links_anexos_consolidados.csv')
        filename_save_destintarios = os.path.join('downloads', 'destinatarios.csv')
        df.to_csv(filename_save, index=False, sep=';')
        df_destinatarios.to_csv(filename_save_destintarios, index=False, sep=';')
        return filename_save_destintarios, filename_save

    @staticmethod
    def data_to_dict(linha):
        colunas = linha.split(";")
        return {
            "terminal": colunas[0].strip(),
            "area_marinha": f"ÁREA {colunas[1].strip()}",
            "marine_area": f"AREA {colunas[1].strip()}",
            "horario": colunas[2],
            "anexos": [
                {
                    "nome": colunas[3].strip(),
                    "link": colunas[4].strip(),
                    "extension": "jpeg" if "marinha" in colunas[4].strip() else "pdf",
                }
            ],
        }

    @staticmethod
    async def process_horario(key, linhas_hora):
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as pool:
            dicionario = await loop.run_in_executor(pool, DataExtractor.aggroup_itens, key, linhas_hora)
        await DataExtractor.generate_file(key, dicionario)

    @staticmethod
    async def setup_data():
        _, filename_save = DataExtractor.convert_to_csv()
        async with aiofiles.open(filename_save, encoding="utf8") as f:
            lines = await f.readlines()
        lines = [line.replace("\n", "") for line in lines]
        lines.pop(0)

        horarios = list(set([line.split(";")[2].split(":")[0] for line in lines]))
        result_dict = {h: [] for h in horarios}
        for linha in lines:
            dados = DataExtractor.data_to_dict(linha)
            hora = dados["horario"].split(":")[0]
            result_dict[hora].append(dados)

        await asyncio.gather(*(DataExtractor.process_horario(k, v) for k, v in result_dict.items()))
