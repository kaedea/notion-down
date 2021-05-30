import os

from config import Config, ArgsParser
from utils.utils import Utils


def start():
    print('\nHello\n')


def get_workspace():
    return os.path.dirname(os.path.realpath(__file__))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ArgsParser.parse()

    print("")
    print("Run with configs:")
    print("config = {}".format(Config.to_string()))

    start()
