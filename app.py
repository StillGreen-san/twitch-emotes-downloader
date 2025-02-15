from bs4 import BeautifulSoup as bs4
from requests import get as fetch
from requests import request
from zipfile import ZipFile as ZipFile
from os import remove as fileRemove
from re import match as regexMatch
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-U",
    "--url",
    help=
    "URL of the emotes you want.\nDefault is https://www.twitchmetrics.net/emotes",
    default="https://www.twitchmetrics.net/emotes")

parser.add_argument("-O",
                    "--output",
                    help="Output filename of zip.\nDefault is 'output.zip'",
                    default="output.zip")

parser.add_argument("-V",
                    "--verbose",
                    help="Adds verbosity to program. It shows what is doing",
                    type=int,
                    choices=[0, 1, 2],
                    default=1)

args = parser.parse_args()


def parsePage(page):
    return bs4(page, "html.parser")


def writeZip(file, emotes):
    # Opens a zip to write
    with ZipFile(f"{file}", "w") as zipFile:
        # Iterates over all images
        for emote in emotes:
            if (args.verbose > 1):
                print(f"Writing {emote.get('name')} to {file}")

            # Opens a {imageName}.{type} to write image
            filename = f"{emote.get('name')}.{emote.get('type').split('/')[1]}"
            with open(filename, "wb") as imageFile:
                imageFile.write(emote.get("content"))
            imageFile.close()
            zipFile.write(filename)
            fileRemove(filename)
    zipFile.close()


def buildAllEmotes(names):
    emotes = []

    for name in names:
        if regexMatch(r"^[a-zA-Z0-9]+$", name.text):
            url = name.find_previous_sibling("div").find("img")["src"]
            url = url.replace('/static/', '/default/')
            if (args.verbose > 1):
                print(f"Downloading {name.text} from {url}")

            response = fetch(url)
            emotes.append({"name": name.text, "content": response.content, "type": response.headers["content-type"]})

    return emotes


def main():
    if (args.verbose > 0):
        print(f"Downloading page from {args.url}")
    parsed_html = parsePage(fetch(args.url).content)

    if (args.verbose > 0):
        print(f"Downloading emotes from {args.url}")
    emotes = buildAllEmotes(parsed_html.body.find_all("samp"))

    if (args.verbose > 0):
        print(f"Writing emotes to {args.output}")
    writeZip(args.output, emotes)


main()
