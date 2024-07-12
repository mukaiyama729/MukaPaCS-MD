from settings import Settings
from pacs_md_executer import PaCSMDExecuter
import logging
import argparse
import os


def main(parser):

    parser.add_argument('--config_path', type=str, help='config path')
    arg = parser.parse_args()
    arranged_args = { k: v for k, v in vars(arg).items() if v is not None }


    settings = Settings(arranged_args['config_path'])
    settings.set_logger(logging=logging, level='info')

    pacs_md_executer = PaCSMDExecuter(settings.base_dir, settings)
    pacs_md_executer.execute_PaCS_MD()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    main(parser)
