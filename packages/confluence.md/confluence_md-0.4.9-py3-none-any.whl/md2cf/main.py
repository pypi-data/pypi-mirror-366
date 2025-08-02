#!/usr/bin/env python3
"""
confluence.md
Push markdown files straight to a Confluence page.
"""

import sys
import argparse
from argparse import RawTextHelpFormatter

from .utils.log import logger, init_logger, headline
from .utils.confluencemd import ConfluenceMD

ACTIONS = {}

def register_action(function):
    """Register command line action function decorator"""
    ACTIONS[function.__name__] = function.__doc__
    def wrapper(args):
        headline(function.__doc__)
        function(args)
        headline("End " + function.__name__)
    return wrapper

def init_confluence(args):
    """Inits connections to Confluence"""
    return ConfluenceMD(username=args.user,
                        token=args.token,
                        password=args.password,
                        md_file=args.file.name,
                        url=args.url,
                        verify_ssl=(not args.no_verify_ssl),
                        add_meta=args.add_meta,
                        add_info_panel=args.add_info,
                        add_label=args.add_label,
                        convert_jira=args.convert_jira)

@register_action
def update(args):
    """Updates page content based on given page_id or metadata in Markdown file"""
    confluence = init_confluence(args)
    confluence.update_existing(args.page_id)

@register_action
def create(args):
    """Creates new page under given parent_id"""
    assert args.url, ("No --url parameter is provided, gave up")

    confluence = init_confluence(args)
    confluence.create_new(args.parent_id, args.title, args.overwrite)

def main():
    """Markdown to Confluence

Example workflow:

1/ Create a new page under --parent_id:

  $ confluence.md --user user@name.net --token 9a8dsadsh --url https://your-domain.atlassian.net \\
        create --file README.md --parent_id 182371 --title "new title" --add_meta

2/ The page is created and the file is decorated with ### 2. The page is created and the file is
  decorated with metadata:

  $ head -n 3 markdown.md
  ---
  confluence-url: https://your-domain.atlassian.net/wiki/spaces/SP/pages/18237182/new+title
  ---

3/ Performing an update does not require providing --page_id and --url:

  $ confluence.md --user user@name.net --token 9a8dsadsh update --file README.md

  Doing an update with --page_id and --url is still possible.

  Consider adding useful --add_info option.

To create Atlassian API Token go to:
  https://id.atlassian.com/manage-profile/security/api-tokens

While using Atlassian on-premise instance, you need to provide --password instead of
--token parameter.

Actions:
"""

    actions = list(ACTIONS.keys())

    description = main.__doc__
    for action in actions:
        description += f"  {action:10}\t\t{ACTIONS[action]}\n"

    parser = argparse.ArgumentParser(
        add_help=True,
        prog="confluence.md",
        formatter_class=RawTextHelpFormatter,
        description=description)

    auth_args = parser.add_argument_group('required auth parameters')
    auth_args.add_argument("-u", "--user",
                           action="store",
                           required=True,
                           help="Atlassian username/email")
    auth_args.add_argument("-l", "--url",
                           action="store",
                           required=False,
                           help="Atlassian instance URL")
    auth_args.add_argument("-n", "--no_verify_ssl",
                           action="store_true",
                           required=False,
                           default=False,
                           help="Don't verify SSL cert in on-prem instances")

    secret_args = auth_args.add_mutually_exclusive_group(required=True)
    secret_args.add_argument("-t", "--token",
                             action="store",
                             required=False,
                             help="Atlassian API token (used in cloud instances)")
    secret_args.add_argument("-p", "--password",
                             action="store",
                             required=False,
                             help="Atlassian password (used in on-prem instances)")


    create_args = parser.add_argument_group('create page parameters')
    create_args.add_argument("--parent_id",
                             action="store",
                             help="define parent page id while creating a new page")
    create_args.add_argument("--title",
                             action="store",
                             help="define page title while creating a new page")
    create_args.add_argument("--overwrite",
                             action="store_true",
                             help="force overwrite if page with this title already exists")

    update_args = parser.add_argument_group('update page arguments')
    update_args.add_argument("--page_id",
                             action="store",
                             help="define (or override) page id while updating a page")

    parser.add_argument("--file",
                        action="store",
                        type=argparse.FileType('r'),
                        required=True,
                        help="input markdown file to process")

    parser.add_argument("--add_meta", action="store_true",
                        help="adds metadata to .md file for easy editing")
    parser.add_argument("--add_info", action="store_true",
                        help="adds info panel **automatic content** "
                            "do not edit on top of the page")
    parser.add_argument("--add_label", action="store",
                        help="adds label to page")
    parser.add_argument("--convert_jira",
                        action="store_true",
                        default=False,
                        help="convert all Jira links to issue snippets "
                            "(either short [KEY-ID] format or full URL)")

    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="verbose mode")
    parser.add_argument("-q", "--quiet",
                        action="store_true",
                        help="quiet mode")
    parser.add_argument("action",
                        help="Action to run",
                        choices=ACTIONS)

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    init_logger(args)

    try:
        globals()[args.action](args)
    # pylint: disable=broad-exception-caught
    except (RuntimeError, AssertionError, Exception) as error:
        logger.error(error)
        if args.verbose:
            raise error
        quit(-1)


if __name__ == "__main__":
    main()
