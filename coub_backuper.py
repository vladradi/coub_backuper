import requests
import json
from lxml import etree
import os
import time
import sys
import config
import json
import urllib
from optparse import OptionParser

debug = False

def printdebug(msg):
    if debug:
        print(msg)

def parseChannelUrl(channelUrl):
    channel = {}
    url = channelUrl.rstrip(" ")
    channelId = url.replace("https://coub.com/", "")
    channel[channelId] = channelId
    return channel

usage = "usage: %prog [options] arg"
parser = OptionParser(usage)
parser.add_option("-u", "--url", dest="channelUrl", help="URL of the channel, default is None'", default=None)
parser.add_option("-j", "--json", dest="jsonFile", help="JSON file with coubs, default is None'", default=None)
parser.add_option("-t", "--type",  dest="type",  help="Type from from {coubs, reposts, all}, default is coubs", default="all")
parser.add_option("-d", "--downloads",  dest="downloads",  help="Download folder for coubs", default=None)

MAX_PAGES=200
COUBS_PER_PAGE=25
(options, args) = parser.parse_args()
channelUrl = options.channelUrl
jsonFile = options.jsonFile
typeFilter = options.type
if options.downloads is not None:
    config.download_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), options.downloads)

user_agent = config.user_agent
download_folder = config.download_folder
proxies = config.proxies

printdebug("channelUrl=%s" % channelUrl)
printdebug("jsonFile=%s" % jsonFile)
printdebug("typeFilter=%s" % typeFilter)
printdebug("downloadFolder=%s" % config.download_folder)

if channelUrl is not None and len(channelUrl) > 10:
    channels = parseChannelUrl(channelUrl)

if options.channelUrl is None and options.jsonFile is None:
    print("Missing arguments. Use --help to show options")
    exit(1)


def get_json_by_url_parsed(url):
    request = requests.get(url, proxies=proxies, headers={"User-Agent": user_agent})
    if request.status_code == 200:
        dom = etree.HTML(request.content.decode("utf-8"))
        return json.loads(dom.xpath("//script[@id='coubPageCoubJson']/text()")[0])


def download_coub_from_json(json_coub, download_folder=download_folder):
    printdebug("[INFO] Starting downloading coub with permalink https://coub.com/view/{0} and name {1}".format(
        json_coub["permalink"], json_coub["title"]))
    folder_save_to = os.path.join(download_folder, "[{0}]".format(json_coub["permalink"]))
    if not os.path.isdir(folder_save_to):
        os.makedirs(folder_save_to)

    ls = os.listdir(folder_save_to)
    video = [s for s in ls if ".mp4" in s]
    audio = [s for s in ls if ".mp3" in s]
    first_frame = [s for s in ls if ".jpg" in s]

    printdebug("[INFO] Save coub.json with metadata of this coub")
    open(os.path.join(folder_save_to, "coub.json"), "wb").write(
        json.dumps(json_coub, ensure_ascii=False).encode("utf-8"))
    file_urls = json_coub["file_versions"]["html5"]
    printdebug("[INFO] Starting download this coub")
    if ("video" in file_urls) and len(video) == 0:
        printdebug("[INFO] Starting download video")
        if "higher" in file_urls["video"]:
            download_file(file_urls["video"]["higher"]["url"],
                          os.path.join(folder_save_to, file_urls["video"]["higher"]["url"].split('/')[-1]))
            printdebug("[INFO] Video downloaded successful")
        elif "high" in file_urls["video"]:
            download_file(file_urls["video"]["high"]["url"],
                          os.path.join(folder_save_to, file_urls["video"]["high"]["url"].split('/')[-1]))
            printdebug("[INFO] Video downloaded successful")
        elif "med" in file_urls["video"]:
            download_file(file_urls["video"]["med"]["url"],
                          os.path.join(folder_save_to, file_urls["video"]["med"]["url"].split('/')[-1]))
            printdebug("[INFO] Video downloaded successful")
        else:
            print("[WARN] No video found! I just save json with properties of this coub")

    if ("first_frame_versions" in json_coub) and len(first_frame) == 0:
        printdebug("[INFO] Starting download first frame of this coub")
        template = json_coub["first_frame_versions"]["template"]
        if "big" in json_coub["first_frame_versions"]["versions"]:
            download_file(template.replace("%{version}", "big"),
                          os.path.join(folder_save_to, template.replace("%{version}", "big").split('/')[-1]))
            printdebug("[INFO] First frame downloaded successful")
        elif "med" in json_coub["first_frame_versions"]["versions"]:
            download_file(template.replace("%{version}", "med"),
                          os.path.join(folder_save_to, template.replace("%{version}", "med").split('/')[-1]))
            printdebug("[INFO] First frame downloaded successful")
        elif "small" in json_coub["first_frame_versions"]["versions"]:
            download_file(template.replace("%{version}", "small"),
                          os.path.join(folder_save_to, template.replace("%{version}", "small").split('/')[-1]))
            printdebug("[INFO] First frame downloaded successful")

    if ("audio" in file_urls) and len(audio) == 0:
        printdebug("[INFO] Starting download audio")
        if "high" in file_urls["audio"]:
            download_file(file_urls["audio"]["high"]["url"],
                          os.path.join(folder_save_to, file_urls["audio"]["high"]["url"].split('/')[-1]))
            printdebug("[INFO] Audio downloaded successful")

        elif "med" in file_urls["audio"]:
            download_file(file_urls["audio"]["med"]["url"],
                          os.path.join(folder_save_to, file_urls["audio"]["med"]["url"].split('/')[-1]))
            printdebug("[INFO] Audio downloaded successful")
        else:
            print("[WARN] coub has audio but i cant download it")
    else:
        print("[WARN] coub without audio")


def download_file(url, path):
    local_filename = path
    # NOTE the stream=True parameter below
    with requests.get(url, proxies=proxies, headers={"User-Agent": user_agent}, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return local_filename


def download_coub_from_coub_property_list(path_to_coub_json):
    coublist = json.loads(open(path_to_coub_json, encoding="utf-8").read())
    length = len(coublist)
    counter = 1
    for coub in coublist:
        print(
            "[{0}/{1}] Starting downloading coub with permalink https://coub.com/view/{2} and name {3} "
                .format(counter,
                        length,
                        coub[
                            "permalink"],
                        coub[
                            "title"]))
        download_coub_from_json(coub)
        counter+=1
        time.sleep(1)


def getJsonOfChannelPage(COUBS_PER_PAGE, timelineOfChannel, currentPage):
    requestUrl = "%s?page=%s&per_page=%s" % (timelineOfChannel, currentPage, COUBS_PER_PAGE)
    return getJsonFrom(requestUrl)


def getJsonFrom(requestUrl):
    try:
        response = requests.get(requestUrl, proxies=proxies, headers={"User-Agent": user_agent})
        if response.status_code == 200:
            return json.loads(response.content.decode("utf-8"))
    except urllib.HTTPError as httpError:
        print("ERROR while reading %s : '%s'" % (requestUrl, httpError))
    return None


timelineApiUrl = "https://coub.com/api/v2/timeline/channel/"
coubs_json = []

for channel in channels.keys():
    timelineOfChannel = "%s%s" % (timelineApiUrl, channel)
    print("[INFO] Reading %s from channel %s" % (typeFilter, timelineOfChannel))
    currentPage = 1
    total_pages = 1
    while (currentPage <= total_pages and int(currentPage) <= int(MAX_PAGES)):
        # gets all coubs from current page
        jsonObject = getJsonOfChannelPage(COUBS_PER_PAGE, timelineOfChannel, currentPage)
        if jsonObject is None:
            break  # skip not existing channels

        total_pages = jsonObject["total_pages"]
        coubs = jsonObject["coubs"]
        if total_pages < MAX_PAGES:
            print("[INFO] reading page %s of %s" % (currentPage, total_pages))
        else:
            print("[INFO] reading page %s of %s" % (currentPage, MAX_PAGES))

        for coub in coubs:
            if (typeFilter == "all" or typeFilter == "reposts") and coub["type"] == "Coub::Recoub":
                coubs_json.append(coub)
            if (typeFilter == "all" or typeFilter == "coubs") and coub["type"] == "Coub::Simple":
                coubs_json.append(coub)

        currentPage += 1
        sys.stdout.flush()
    print("[INFO] Found json with %s coubs" % len(coubs_json))

if len(coubs_json) > 0:
    resFilename = open('%s' % jsonFile, 'w')
    formatted_json = json.dumps(coubs_json)
    resFilename.write("%s" % formatted_json)
    resFilename.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: coub_backuper.py -j <path_to_json_with_coubs>")
        parser.print_help(sys.stderr)
        exit()
    print("[INFO] Starting download from file %s into %s" % (jsonFile, config.download_folder))
    property_list_file_path = jsonFile
    download_coub_from_coub_property_list(property_list_file_path)
