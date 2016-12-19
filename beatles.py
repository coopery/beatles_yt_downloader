from googleapiclient.discovery import build
import os
import requests

YOUTUBE_API_KEY = ''
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def sanitize_track_name(name):
    name = name.replace('\n', '')
    return name

def get_youtube_id(title):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            developerKey=YOUTUBE_API_KEY)

    search_response = youtube.search().list(
            part='id',
            q=title,
            type='video',
            maxResults=1,
        ).execute()

    result = search_response.get('items')[0]
    return result['id']['videoId']

def get_mp3_link(ytid):
    converter_link = 'http://www.youtubeinmp3.com/fetch'
    converter_params = {
            'format': 'JSON',
            'video': 'http://www.youtube.com/watch?v=%s' % ytid
        }

    resp = requests.get(converter_link, params=converter_params)
    resp_data = resp.json()
    return resp_data['link']

def get_directory(disc):
    return disc.split('.')[0]

def get_filename(track):
    return track.replace('/', '') + '4.mp3'

def download_mp3(url, disc, track):
    print('Getting track')
    resp = requests.get(url, stream=True)

    directory = get_directory(disc)
    filename = get_filename(track)

    print('Writing file')
    with open(os.path.join('./'+directory, filename), 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print('Wrote file')

def download_track(track, disc):
    print('Downloading track: %s' % track)

    ytid = get_youtube_id(track)
    print('Got youtube id: %s\n' % ytid)

    mp3_link = get_mp3_link(ytid)
    download_mp3(mp3_link, disc, track)

if __name__ == '__main__':

    with open('ytapikey.txt') as keyfile:
        YOUTUBE_API_KEY = keyfile.read()

    discs = ['disc1.txt', 'disc2.txt', 'disc3.txt']

    errors = []

    for disc in discs:
        print('*** Working on %s...\n' % disc)

        with open(disc) as tracks:
            for track in tracks:
                track = sanitize_track_name(track)
                try:
                    download_track(track, disc)
                except Exception as e:
                    print(e)
                    errors.append(track)

        print('*** Finished disc!\n')

    print('Errors: %d' % len(errors))
    print(errors)
