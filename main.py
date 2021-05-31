from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter


def start():
    print('\nHello, NotionDown!\n')

    NotionWriter.clean_output()
    notion_pages = NotionReader.handle_post()
    for notion_page in notion_pages:
        NotionWriter.handle_page(notion_page)


# Cli cmd example:
# python main.py \
#     --blog_url 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34' \
#     --token_v2 <token_v2>
if __name__ == '__main__':
    Config.parse_configs()
    Config.check_required_args()

    print("")
    print("Run with configs:")
    print("config = {}".format(Config.to_string()))

    start()
