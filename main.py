import asyncio
from utils.data_extractor import DataExtractor as data_extractor
from utils.factory_data import FactoryData as factory_data

def main():
    asyncio.run(data_extractor.setup_data())
    asyncio.run(factory_data.organize_data())

if __name__ == "__main__":
    main()
