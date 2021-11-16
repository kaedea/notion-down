import shutil

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils, FileUtils


def start():
    print('\nHello, NotionDown sample posts for Hexo\n')
    NotionWriter.clean_output()
    channel = 'Hexo'

    notion_pages = NotionReader.handle_post()
    dir_outputs = NotionWriter.handle_pages(notion_pages)

    if not dir_outputs[channel] or not dir_outputs[channel].has_output():
        raise Exception("job fail, output dir not found: {}".format(dir_outputs[channel]))

    output_dir = dir_outputs[channel].output_dir
    print("get writer output dir: {}".format(output_dir))

    dist_dir = FileUtils.new_file(Utils.get_workspace(), "dist/parse_sample_posts_for_hexo")
    FileUtils.create_dir(dist_dir)
    print("publish file to: {}".format(dist_dir))

    # Copy dir append
    # noinspection PyArgumentList
    shutil.copytree(
        output_dir,
        dist_dir,
        dirs_exist_ok=True
    )
    print("done\n")


if __name__ == '__main__':
    Config.parse_configs()
    Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
    Config.set_download_image(True)
    Config.set_writer('Hexo')
    Config.set_page_titles_match(["^(Hexo page -)"])

    print("")
    print("Run with configs:")
    print("config = {}".format(Config.to_string()))
    start()
