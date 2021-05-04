import os

from notion.client import NotionClient


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    notion_token = os.environ['NOTION_TOKEN_V2']

    # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so
    client = NotionClient(token_v2=notion_token)

    # Replace this URL with the URL of the page you want to edit
    page = client.get_block("https://www.notion.so/kaedea/Blog-Post-2-8c01234b227a4c978dd0a3934e303ac3")

    print("The old title is:", page.title)
    print("SubPage = {}", len(page.children))

    for subpage in page.children:
        if subpage.children:
            for block in subpage.children:
                pass
        pass

    # Note: You can use Markdown! We convert on-the-fly to Notion's internal formatted text data structure.
    page.title = "The title has now changed, and has *live-updated* in the browser!"

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
