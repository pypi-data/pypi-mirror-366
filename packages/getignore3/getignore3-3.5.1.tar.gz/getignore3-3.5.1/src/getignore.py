"""
A tool to fetch and manage `.gitignore` templates from GitHub with minimal effort
"""

import appdirs
import argparse
import os
import sys

import requests


CACHE_DIR = appdirs.user_cache_dir("getignore3")


argparser = argparse.ArgumentParser(
    prog="getignore",
    description="Get gitignore files without bothering yourself",
)

argparser.add_argument(
    "template_name",
    nargs="*",
    help="Name(s) of gitignore templates to fetch (e.g., Python, Node and etc.)",
)
argparser.add_argument(
    "-L",
    "--list-cached-templates",
    action="store_true",
    help="List cached gitignore templates",
)
argparser.add_argument(
    "-l",
    "--list-templates",
    action="store_true",
    help="List available gitignore templates",
)
argparser.add_argument(
    "-n",
    "--no-cache",
    action="store_true",
    help="Don't cache the gitignore template file when downloaded",
)
argparser.add_argument(
    "-c",
    "--offline",
    action="store_true",
    help="Get the cached gitignore template instead of downloading",
)
argparser.add_argument(
    "-o",
    "--output",
    default=".gitignore",
    help="Where to write the gitignore template content to",
)
argparser.add_argument(
    "-w",
    "--override",
    action="store_true",
    help="Override existing gitignore file instead of appending",
)


def getignore() -> None:
    """
    A tool to fetch and manage `.gitignore` templates from GitHub with minimal effort
    """

    args = argparser.parse_args()

    if args.list_templates:
        repository_contents = requests.get(
            "https://api.github.com/repos/github/gitignore/contents/"
        ).json()
        available_templates = [
            item["name"]
            for item in repository_contents
            if item["name"].endswith(".gitignore")
        ]

        print("Available gitignore templates:")
        print(", ".join(available_templates), end="\n\n")

    if args.list_cached_templates:
        cached_templates = [
            item
            for item in os.listdir(CACHE_DIR)
            if item.endswith(".gitignore")
            and os.path.isfile(os.path.join(CACHE_DIR, item))
        ]

        print("Cached gitignore templates:")
        print(", ".join(cached_templates), end="\n\n")

    template_names = args.template_name

    content_to_write = ""

    if template_names == []:
        print("Nothing happened!")
        return

    for name in template_names:
        path_to_cache_file = os.path.join(CACHE_DIR, f"{name}.gitignore")

        if args.offline:
            if not os.path.isfile(path_to_cache_file):
                print(f"Couldn't find the {name!r} gitignore template! (offline)")
                args.offline = False

            if args.offline:
                with open(path_to_cache_file) as cache_file:
                    content_to_write += cache_file.read() + "\n"
                print(f"Got the {name!r} gitignore template!")

        if not args.offline:
            getignore_request = requests.get(
                f"https://raw.githubusercontent.com/github/gitignore/main/{name}.gitignore"
            )

            if getignore_request.status_code >= 400:
                print(
                    f"Error {getignore_request.status_code}, Couldn't get the {name!r} gitignore template!",
                    file=sys.stderr,
                )
                continue

            content_to_write += getignore_request.text + "\n"
            print(f"Got the {name!r} gitignore template!")

            if not args.no_cache:
                with open(path_to_cache_file, "w") as cache_file:
                    cache_file.write(getignore_request.text)
                print(
                    f"Cached the {name!r} gitignore template at {path_to_cache_file!r}!"
                )

    did_output_file_exist = os.path.exists(args.output)

    with open(args.output, "w" if args.override else "a") as output_file:
        output_file.write(content_to_write)

    if not did_output_file_exist:
        print("Created the gitignore file!")

    elif args.override:
        print("Overwrote the gitignore file!")

    else:
        print("Appended new things to the gitignore file!")


if __name__ == "__main__":
    getignore()
