import asyncio
import json
from utils.data_extractor import DataExtractor as data_extractor
from utils.factory_data import FactoryData as factory_data
from utils.files_validade import FilesValidade as files_validade

def main():
    asyncio.run(data_extractor.setup_data())
    asyncio.run(factory_data.organize_data())

    # Processo responsável pela validação dos arquivos
    # asyncio.run(files_validade.create_report())
    
if __name__ == "__main__":
    main()
