from settings import Settings
from pacs_md_executer import PaCSMDExecuter

def main():
    settings = Settings("./config.ini")
    pacs_md_executer = PaCSMDExecuter(settings.base_dir, settings)
    print('unko')

if __name__ == "__main__":
    main()
