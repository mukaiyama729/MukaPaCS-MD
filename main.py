from settings import Settings
from pacs_md_executer import PaCSMDExecuter
import logging
logger = logging.getLogger('pacs_md')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('./pacs_log.log')
fmt = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)

selection_logger = logging.getLogger('selection')
selection_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('./selection_log.log')
fmt = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(fmt)
selection_logger.addHandler(handler)

def main():
    settings = Settings("./config.ini")
    pacs_md_executer = PaCSMDExecuter(settings.base_dir, settings)
    pacs_md_executer.execute_PaCS_MD()
    print('unko')

if __name__ == "__main__":
    main()
