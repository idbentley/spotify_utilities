from apiclient.discovery import build
from apiclient.errors import HttpError
from private_conf import conf


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = conf["youtube_developer_key"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(artist, track):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q="{} {}".format(track["name"], artist),
    part="id,snippet",
    maxResults=10
  ).execute()

  videos = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos.append(search_result)

  print ("Videos:")
  for video in videos:
    if (track["name"] in video["snippet"]["title"] or track["name"] in video["snippet"]["description"]) and (artist in video["snippet"]["title"] or artist in video["snippet"]["description"]):
      print ("{} http://youtube.com/watch?v={}".format(video["snippet"]["title"], video["id"]["videoId"]))