from settings import Settings
from pacs_md_executer import PaCSMDExecuter
import logging
import argparse

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

def main(parser):

    parser.add_argument('--config_path', type=str, help='config path')
    arg = parser.parse_args()
    arranged_args = { k: v for k, v in vars(arg).items() if v is not None }

    settings = Settings(arranged_args['config_path'])
    pacs_md_executer = PaCSMDExecuter(settings.base_dir, settings)
    pacs_md_executer.execute_PaCS_MD()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    main(parser)
