from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter


def start():
    print("Run with configs:")
    print("config = {}".format(Config.to_string()))
    NotionWriter.clean_output()
    notion_pages = NotionReader.handle_post()
    for notion_page in notion_pages:
        NotionWriter.handle_page(notion_page)


# Cli cmd example:
# python main.py \
#     --blog_url 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34' \
#     --token_v2 <token_v2>
#     --username <username>  # Only when token_v2 is not presented
#     --password <password>  # Only when token_v2 is not presented
# or
# python main.py \
#     --config_file '.config_file.json'
#
if __name__ == '__main__':
    Config.parse_configs()
    Config.check_required_args()
    Config.check_required_modules()

    print('\nHello, NotionDown!\n')
    start()
