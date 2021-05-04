import os

from utils.utils import Utils


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def get_workspace():
    return os.path.dirname(os.path.realpath(__file__))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process some args.')
    parser.add_argument('debug', nargs='?', default=True)
    parser.add_argument('workspace', nargs='?', default=get_workspace())
    parser.add_argument('output', nargs='?', default=os.path.join(Utils.get_temp_dir(), "notion-down"))
    parser.add_argument('notion_token_v2', nargs='?', default=None)

    args = parser.parse_args()
    if args.debug:
        args.output = os.path.join(args.workspace, "build/outputs")
        args.notion_token_v2 = os.environ['NOTION_TOKEN_V2']
        pass

    print("Running args:")
    print("workspace = {}".format(args.workspace))
    print("output = {}".format(args.output))
    print("notion_token_v2 = {}".format(args.notion_token_v2))


