
# Notion Down

[notion-down](https://github.com/kaedea/notion-down), python tools that convert Notion blog pages into Markdown files, along with intergation to build static webpages such as Hexo.



 * [Notion Down](#notion-down)
 * &nbsp;&nbsp;&nbsp;&nbsp;[Features](#features)
 * &nbsp;&nbsp;&nbsp;&nbsp;[Hot It Works](#hot-it-works)
 * &nbsp;&nbsp;&nbsp;&nbsp;[Getting Started](#getting-started)
 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[UnitTest Examples](#unittest-examples)
 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CI Build Script](#ci-build-script)



## Features

What can notion-down do now:

 - Notion pages to basic MD files

 - Notion images downloading



## Hot It Works

NotionDown read Notion pages data using [notion-py](https://github.com/jamalex/notion-py), and then write pages into MD files.



Basic usage:

> notion-down >> notion-py >> Notion pages data >> generating MD files

Advanced usage:

> WebHook >> notion-down >> notion-py >> Notion pages data >> generating MD files >> Copy into Hexo source >> generating webpages >> push to GitHub pages



## Getting Started

Set `notion_token_v2` at System ENV or `config.py` first, and then check the following procedures.

### UnitTest Examples

See unitest cases at `/test`.



### CI Build Script

See building script at `/.circleci/config.yaml`.



> This page is generated by [notion-down](https://github.com/kaedea/notion-down) from [notion.so NotionDown-README](https://www.notion.so/kaedea/NotionDown-README-d3463f3d398743879d663caf87efa029).








<!-- NotionPageWriter
-->