# confluence.md

Push markdown files straight to a Confluence page.

## What it does?

`confluence.md` allows you to push any markdown file to Confluence. You can create
a new page (under given parent) or update an existing one.

## How to install?

It's as easy as:

```sh
$ pip install confluence.md

# If the above doesn't work, your `pip` command points to different
# python than installation than `python` command. If so, run:
$ python -m pip install confluence.md
```

## How to use it in command-line?

Markdown to Confluence

Example workflow:

#### 1. Create page

Create a new page under `--parent_id`:
```sh
$ confluence.md --user user@name.net \             # Atlassian username
        --token 9a8dsadsh \                        # API token or --password
        --url https://your-domain.atlassian.net \  # Confluence instance URL
        create \                                   # create or update
        --file README.md \                         # markdown file
        --parent_id 182371 \                       # parent page
        --title "new title"                        # title for a new page
        --add_meta                                 # adds meta to source.md file
```

#### 2. Verify markdown

The page is created and the file is decorated with metadata:

```sh
$ head -n 3 markdown.md
---
confluence-url: https://your-domain.atlassian.net/wiki/spaces/SP/pages/18237182/new+title
---
```

#### 3. Update page

Performing an update does not require providing `--page_id` and `--url`:

```sh
$ confluence.md --user user@name.net --token 9a8dsadsh update --file README.md
```

Doing an update with `--page_id` and `--url` is still possible.

Consider adding useful `--add_info` option.

To create Atlassian API Token go to [api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).

## Command line arguments

**Actions:**

- `update`    		Updates page content based on given `page_id` or metadata in Markdown file
- `create`    		Creates new page under given `parent_id`

**positional arguments:**

- `{update,create}`         Action to run

**optional arguments:**

- `-h`, `--help`            show this help message and exit
- `--file FILE`             input markdown file to process
- `--add_meta`              adds metadata to .md file for easy editing
- `--add_info`              adds info panel **automatic content** do not edit on top of the page
- `--add_label` `ADD_LABEL` adds label to page
- `--convert_jira`          convert all Jira links to issue snippets (either short [KEY-ID] format or full URL)
                            **note**: this options works only in Cloud instances with [Secure Markdown](https://marketplace.atlassian.com/plugins/secure-markdown-for-confluence) installed
- `-v`, `--verbose`         verbose mode
- `-q`, `--quiet`           quiet mode

**required auth parameters:**

- `-u` `USER`, `--user` `USER`    Atlassian username/email
- `-t` `TOKEN`, `--token` `TOKEN` Atlassian API token
- `-p` `PWD`, `--password` `PWD`  Atlassian password (used in on-prem instances)
- `-l` `URL`, `--url` `URL`       Atlassian instance URL
- `-n`, `--no_verify_ssl`         don't verify SSL cert (useful in on-prem instances)

**create page parameters:**

- `--parent_id` `PARENT_ID` define parent page id while creating a new page
- `--title` `TITLE`         define page title while creating a new page
- `--overwrite`             force overwrite if page with this title already exists

**update page arguments:**

- `--page_id` `PAGE_ID`     define (or override) page id while updating a page

## How to use it in a Python script?

ConfluenceMD wasn't designed to be used this way, but it's fairly simple to embed
it in a Python script. See this example:

```python
from md2cf.utils.confluencemd import ConfluenceMD

conf_md = ConfluenceMD(username=user,
                       md_file=md_file,
                       token=token,
                       url=url,
                       convert_jira=convert_jira)

# create new page under parent_id
new_page_id = conf_md.create_new("parent_id", "title")

# update existing page with given page_id
page_id = conf_md.update_existing("page_id")
```