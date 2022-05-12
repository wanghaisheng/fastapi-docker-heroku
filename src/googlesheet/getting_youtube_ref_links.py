import json
import requests
import re
from tqdm import tqdm

import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

API_KEY = ""
CHANNEL_ID = "UCptRK95GEDXvJGOQIFg50fg"  # Igor Link

# ---- Google authentication ---- #
# credentials.json can be acquired in google spreadsheets api
CREDENTIALS_FILE = 'credentials.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                       'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http = httpAuth)
spreadsheetId = ''


def get_all_video_data():
    """Extract all video information of the channel"""
    print('getting video data...')
    channel_videos = _get_channel_content(limit=50)

    parts = ["snippet", "statistics", "topicDetails"]
    for video_id in tqdm(channel_videos):
        for part in parts:
            data = _get_single_video_data(video_id, part)
            channel_videos[video_id].update(data)

    return channel_videos


def _get_channel_content(limit=None):
    """
    Extract all videos, check all available search pages
    channel_videos = videoId: title, publishedAt
    return channel_videos
    """
    url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date"
    if limit is not None and isinstance(limit, int):
        url += "&maxResults=" + str(limit)

    videos, npt = _get_channel_content_per_page(url)
    while npt is not None:
        nexturl = url + "&pageToken=" + npt
        next_vid, npt = _get_channel_content_per_page(nexturl)
        videos.update(next_vid)

    return videos


def _get_channel_content_per_page(url: str):
    """
    Extract all videos and playlists per page
    video: dict {id: {published_at, title}, ...}
    return channel_videos, nextPageToken
    """
    json_url = requests.get(url)
    data = json.loads(json_url.text)
    channel_videos = dict()
    if 'items' not in data:
        print('Error! Could not get correct channel data!\n', data)
        return channel_videos, None

    nextPageToken = data.get("nextPageToken", None)

    item_data = data['items']
    for item in item_data:
        try:
            kind = item['id']['kind']
            published_at = item['snippet']['publishedAt']
            title = item['snippet']['title']
            if kind == 'youtube#video':
                video_id = item['id']['videoId']
                channel_videos[video_id] = {'publishedAt': published_at, 'title': title}
        except KeyError:
            print('Error! Could not extract data from item:\n', item)

    return channel_videos, nextPageToken


def _get_single_video_data(video_id, part):
    """
    Extract further information for a single video
    parts can be: 'snippet', 'statistics', 'contentDetails', 'topicDetails'
    """

    url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={API_KEY}"
    json_url = requests.get(url)
    data = json.loads(json_url.text)
    try:
        data = data['items'][0][part]
    except KeyError:
        print(f'Error! Could not get {part} part of data: \n{data}')
        data = dict()
    return data


def get_all_video_links(videos: dict) -> dict:
    """
    Extract all links from the video description, save it with unique id and useful data
    link_data = link, publishedAt, tags, viewCount, likeCount
    return link_data
    """
    print("Getting video links")
    link_data = dict()
    tags = ["publishedAt", "tags", "viewCount", "likeCount"]
    link_id = 0
    for video_id, data in tqdm(videos.items()):
        links = re.findall(r'(https?://\S+)', data["description"])
        for link in links:
            link_dict = dict()
            link_dict.update({link_id: {"link": link}})
            for tag in tags:
                try:
                    link_dict[link_id][tag] = data[tag]
                except KeyError as e:
                    print(f"Can not get tag {e} for video {video_id}")
            link_id += 1
            link_data.update(link_dict)
    return link_data


def get_all_link_hosts(links_json: dict) -> None:
    """
    Add domain of link to dict of links
    :param links_json: dict with link id and info about the link
    """
    print("Getting links hosts")
    regex = re.compile("//([www.]?[a-z0-9\-]*\.?[a-z0-9\-]*\.?[a-z0-9\-]*)")
    dummy_links = ["bit.ly", "clc.to", "u.to", "cutt.ly", "clck.ru", "clcr.me", "clik.cc", "clc.am",
                   "tiny.cc", "goo.gl", "play.google.com", "apps.apple.com"]
    for link_id, data in tqdm(links_json.items()):
        if any(substring in data["link"] for substring in dummy_links):
            try:
                url = requests.get(data["link"]).url
            except requests.exceptions.ConnectionError as e:
                print(e)
                url = e.request.url
        else:
            url = data["link"]
        domain = regex.findall(url)[0]
        links_json[link_id]["domain"] = domain


def get_link_dict_with_partiated_tags(links_json: dict) -> dict:
    print("Partiating tags")

    link_data = dict()
    tags = ["publishedAt", "viewCount", "likeCount", "domain"]
    id_ = 0
    for link_id, data in tqdm(links_json.items()):
        link_tags = data.get("tags")
        if link_tags:
            for link_tag in link_tags:
                link_dict = dict()
                link_dict.update({id_: {"link": data["link"]}})
                for tag in tags:
                    try:
                        link_dict[id_][tag] = data[tag]
                    except KeyError as e:
                        print(f"Can not get tag {e} for link {link_id}")
                link_dict[id_]["tag"] = link_tag
                id_ += 1
                link_data.update(link_dict)
        else:
            link_dict = dict()
            link_dict.update({id_: {"link": data["link"]}})
            for tag in tags:
                try:
                    link_dict[id_][tag] = data[tag]
                except KeyError as e:
                    print(f"Can not get tag {e} for link {link_id}")
            id_ += 1
            link_data.update(link_dict)

    return link_data


def dump_data_to_spreadsheet(links_json: dict) -> None:
    """
    Dump data from dict to spreadsheet that you connected
    :param links_json: dict with all link data
    """
    print("Dumping data")

    global service
    result: List[list] = []

    fields = ["link", "publishedAt", "viewCount", "likeCount", "domain", "tag"]

    for link_id, data in tqdm(links_json.items()):
        link_data = []
        for field in fields:
            try:
                link_data.append(data[field])
            except KeyError:
                link_data.append(None)
        result.extend([link_data])

    service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId,
                                                body={
                                                    "valueInputOption": "USER_ENTERED",
                                                    "data": [
                                                        {"range": "A1:G25000",
                                                         "majorDimension": "ROWS",
                                                         "values": result}
                                                    ]
                                                }).execute()


if __name__ == '__main__':
    # video_data_dict = get_all_video_data()
    # with open("video_data.json", "w", encoding="utf-8") as jsonfile:
    #     json.dump(video_data_dict, jsonfile, indent=4, ensure_ascii=False)
    #
    # with open("video_data.json", "r", encoding="utf-8") as jsonfile:
    #     data = json.load(jsonfile)
    #     link_data = get_all_video_links(data)
    #     with open("link_data.json", "w", encoding="utf-8") as linkfile:
    #         json.dump(link_data, linkfile, indent=4, ensure_ascii=False)
    #
    # with open("link_data.json", "r", encoding="utf-8") as jsonfile:
    #     links = json.load(jsonfile)
    #     get_all_link_hosts(links)
    #     with open("link_data_domains.json", "w", encoding="utf-8") as linkfile:
    #         json.dump(links, linkfile, indent=4, ensure_ascii=False)

    # with open("link_data_domains.json", "r", encoding="utf-8") as jsonfile:
    #     links = json.load(jsonfile)
    #     links_with_partiated_tags = get_link_dict_with_partiated_tags(links)
    #     with open("link_data_partiated_tags.json", "w", encoding="utf-8") as linkfile:
    #         json.dump(links_with_partiated_tags, linkfile, indent=4, ensure_ascii=False)
    #
    # with open("link_data_partiated_tags.json", "r", encoding="utf-8") as jsonfile:
    #     links = json.load(jsonfile)
    #     dump_data_to_spreadsheet(links)

    # video_data = get_all_video_data()
    # link_data = get_all_video_links(video_data)
    # get_all_link_hosts(link_data)
    # link_data_partiated_tags = get_link_dict_with_partiated_tags(link_data)
    # dump_data_to_spreadsheet(link_data_partiated_tags)

    pass