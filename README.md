
![Page Cover](https://www.notion.so/image/https%3A%252F%252Fwww.notion.so%252Fimages%252Fpage-cover%252Fnasa_buzz_aldrin_on_the_moon.jpg)

# Notion Down

![](/assets/notion_down.svg)

[Notion Down](https://github.com/kaedea/notion-down), python tools that convert Notion blog pages into Markdown files, along with integration to build static webpages such as Hexo.  Its inspiration and goal is to __avoid separation  of writing__ by keep writing drafts or posts within [notion.so](http://notion.so) and then publish them into MD webpages automatically. 

 * [Notion Down](#notion-down)
 * &nbsp;&nbsp;&nbsp;&nbsp;[Example](#example)
 * &nbsp;&nbsp;&nbsp;&nbsp;[Features](#features)
 * &nbsp;&nbsp;&nbsp;&nbsp;[Hot It Works](#hot-it-works)
 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Basic usage](#basic-usage)
 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Advanced usage](#advanced-usage)
 * &nbsp;&nbsp;&nbsp;&nbsp;[Getting Started](#getting-started)
 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Prepare](#prepare)
 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Run NotionDown](#run-notiondown)
 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CI Build Script](#ci-build-script)
 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Showcase Jobs](#showcase-jobs)
 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[UnitTest Examples](#unittest-examples)

## Example

[kaedea.com](http://www.kaedea.com)  
[hexo.kaedea.com](http://hexo.kaedea.com)  
[基于 Notion 的笔记写作和博客分享自动化方案](https://www.kaedea.com/2021/05/20/devops/notion-to-markdown-file-automating-solution/)

## Features

What can NotionDown do now:

 - Notion pages to MarkDown files
     - ~~Basic Notion PageBlocks parsing~~
     - ~~Notion images refer & download~~
     - ~~Notion nested list blocks~~
     - ~~Notion obfuscated-links parsing~~
     - ~~Notion table block (Collection)~~
     - Notion subpage / alias link parsing
 - Advanced Notion PageBlocks support
     - ~~Pullquote Blocks (Notion ColumnList)~~
     - Image source replacing 
         - ~~Replace notion image url with image file~~
         - Replace notion image url with other CDN urls
     - Notion page embed blocks
 - Writing optimized integration
     - ~~Noton custom `ShortCode` blocks that control parametered MD files generating~~
     - ~~Mixed CN-EN text separation format~~ ([by pangu](https://github.com/vinta/pangu))
     - ~~Spelling inspect~~ (by [pycorrector](https://github.com/shibing624/pycorrector))
 - HEXO Integration
     - ~~HEXO page properties config~~
     - ~~HEXO generate~~
     - HEXO tags plugin
 - PyPI Publish
 - Notion APIs
     - ~~notion-py (3rd party)~~
     - notion-sdk (official)

## Hot It Works

![NotionDown Workflows](/assets/notiondown_workflows_notiondown.png)

NotionDown read Notion pages data using [notion-py](https://github.com/jamalex/notion-py), and then write pages into MD files.

### Basic usage

> notion-down >> Notion APIs (notion-py) >> Notion pages data >> generating MD files

### Advanced usage

> WebHook >> notion-down >> Notion APIs (notion-py) >> Notion pages data >> generating MD files >> Copy into Hexo source >> generating webpages >> push to GitHub pages

## Getting Started

### Prepare

To get started with NotionDown, you should:

1. Prepare `notion_token_v2`.
1. Prepare `public notion blog_url` as root post for NotionDown to get the pages you want to handle.
1. Run `notion-down/main.py` with your configs.

Check [here](https://github.com/kaedea/notion-down/blob/master/dist/parse_readme/notiondown_gettokenv2.md) to get `notion_token_v2`. 

Duplicate [NotionDown Posts Template](https://www.notion.so/kaedea/NotionDown-Posts-Template-f77f3322915a4ab48caa0f2e76e9d733) to your own notion and take it as `blog_url` (or you can just use your existing blog post url). Note that, for now the root page should be public  as well as placed in root path of notion workspace.


### Run NotionDown

Basically just run `notion-down/main.py` :

```Bash
# Run with cli cmd
PYTHONPATH=./ python main.py \
    --blog_url <Notion Post Url> \
    --token_v2 <token_v2>

# or
PYTHONPATH=./ python main.py \
    --config_file '.config_file.json'

# Your can configure notion-down args by cli-args, config_file or SysEnv parameters
# Priority: cli args > config_file > SysEnv parameters > NotionDown default
```


For custom configurations in details, see [Custom Configurations](https://github.com/kaedea/notion-down/blob/master/dist/parse_readme/notiondown_custom_configs.md).

Also check the following procedures as showcase usages for NotionDown.

### CI Build Script

See building script at `/.circleci/config.yaml`.

 - `test-build-readme`: CircleCI jobs generating README for this repo. 
 - `test-build-hexo`: CircleCI jobs generating Hexo posts for [https://github.com/kaedea/notion-down-hexo-showcase](https://github.com/kaedea/notion-down-hexo-showcase).
 - `test-run-pycorrector`: CircleCI jobs that executing spelling check for the test posts.

### Showcase Jobs

See the usage showcase jobs at [/jobs](/jobs), and jobs outputs at [/dist](/dist).

 - [README generating](/jobs/parse_readme/)
 - [Notion sample post generating](/jobs/parse_sample_posts/)
 - [HEXO public generating](/jobs/parse_sample_posts_for_hexo/)
 - Notion image page source replacing (WIP)

### UnitTest Examples

See unittest cases at `test/`.


---

> This page is generated by [notion-down](https://github.com/kaedea/notion-down) from [notion.so NotionDown-README](https://www.notion.so/kaedea/NotionDown-README-d3463f3d398743879d663caf87efa029).






<!-- Generated by NotionPageWriter
notion-down.version = 0.1.0
notion-down.revision = b'5bfb07c'
-->
