
# Install required packages --------------
# !pip install google-api-python-client
# !pip install pytube
# !pip install python-dotenv

# Import required libraries --------------
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Set your YouTube API key
YOUTUBE_KEY = os.getenv('YOUTUBE_API_KEY')

# 1. 채널 정보 ----------------------------

def get_channel_details(channel_id, api_key, json_filename):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.channels().list(part='snippet,statistics', id=channel_id)
    response = request.execute()

    # Save the channel details to a JSON file
    with open(json_filename, 'w') as file:
        json.dump(response, file, indent=4)

    return response

# "@thekpop": "UCoRXPcv8XK5fAplLbk9PTww"
# "@thekpop2": "UCITH7URIRpb8yoshUwGE9jg"

channel_id = 'UCoRXPcv8XK5fAplLbk9PTww'
json_filename = 'data/kpop_channel.json'
channel_details = get_channel_details(channel_id, YOUTUBE_KEY, json_filename)

# 2. 비디오 목록 ----------------------------

def get_playlist_id(channel_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.channels().list(part='contentDetails', id=channel_id)
    response = request.execute()

    if 'items' in response and response['items']:
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return None

def get_video_list(playlist_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.playlistItems().list(part='snippet', playlistId=playlist_id, maxResults=50)
    video_ids = []

    while request:
        response = request.execute()
        video_ids += [item['snippet']['resourceId']['videoId'] for item in response['items']]
        request = youtube.playlistItems().list_next(request, response)

    return video_ids

def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Usage
channel_id = 'UCoRXPcv8XK5fAplLbk9PTww'
playlist_id = get_playlist_id(channel_id, YOUTUBE_KEY)

if playlist_id:
    video_list = get_video_list(playlist_id, YOUTUBE_KEY)
    save_to_json(video_list, 'data/kpop_video_ids.json')
    print(f"Video IDs saved to 'data/kpop_video_ids.json'")
else:
    print("No playlist found.")
    
# 3. 비디오 정보 ----------------------------
import time

def get_video_details(video_id, api_key, max_retries=3):
    youtube = build('youtube', 'v3', developerKey=api_key)
    attempt = 0

    while attempt < max_retries:
        try:
            request = youtube.videos().list(part='snippet,statistics', id=video_id)
            response = request.execute()
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            attempt += 1
            time.sleep(2)  # Wait for 2 seconds before retrying

    print(f"Failed to fetch details for video ID: {video_id} after {max_retries} attempts.")
    return None

def get_video_statistics(details):
    video_id = details['items'][0]['id']
    title = details['items'][0]['snippet']['title']
    published_date = details['items'][0]['snippet']['publishedAt']
    view_count = details['items'][0]['statistics']['viewCount']
    like_count = details['items'][0]['statistics']['likeCount']
    favorite_count = details['items'][0]['statistics']['favoriteCount']
    comment_count = details['items'][0]['statistics']['commentCount']

    return {
        'id': video_id,
        'title': title,
        'published_date': published_date,
        'view_count': view_count,
        'like_count': like_count,
        'favorite_count': favorite_count,
        'comment_count': comment_count
    }

def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


# Main code to process a list of video IDs and save statistics
# videos_list = ['S2AUt1j90o4']  # Replace with your list of video IDs

# details = get_video_details('S2AUt1j90o4', YOUTUBE_KEY)

with open('data/kpop_video_ids.json', 'r') as file:
    videos_list = json.load(file)

all_video_stats = []

for count, video_id in enumerate(videos_list, start=1):
    details = get_video_details(video_id, YOUTUBE_KEY)
    if details and 'items' in details and details['items']:
        stats = get_video_statistics(details)
        all_video_stats.append(stats)
    else:
        print(f"No details found for video ID: {video_id}")

    # Print progress after each iteration
    print(f"Processed {count}/{len(videos_list)} videos")


# Save to JSON
save_to_json(all_video_stats, 'data/kpop_video_statistics.json')
print("Video statistics saved to 'data/kpop_video_statistics.json'")


# 4. 플레이리스트 목록 ----------------------------

def get_uploads_playlist_id(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    request = youtube.channels().list(part='contentDetails', id=channel_id)
    response = request.execute()

    if 'items' in response and response['items']:
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return None

def get_all_playlists(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    request = youtube.playlists().list(part='snippet', channelId=channel_id, maxResults=50)
    playlist_ids = []

    while request:
        response = request.execute()
        playlist_ids += [item['id'] for item in response['items']]
        request = youtube.playlists().list_next(request, response)

    return playlist_ids

# Usage
channel_id = 'UCITH7URIRpb8yoshUwGE9jg'
uploads_playlist_id = get_uploads_playlist_id(channel_id)
print("Uploads Playlist ID:", uploads_playlist_id)

all_playlists = get_all_playlists(channel_id)
print("All Playlist IDs:", all_playlists)

# 4. 플레이리스트 상세 ----------------------------

def get_playlist_details(playlist_id):
    youtube = build('youtube', 'v3', developerKey='YOUR_API_KEY')
    request = youtube.playlists().list(part='snippet', id=playlist_id)
    response = request.execute()
    return response

playlist_id = 'PL3seOLd6q4fx4TamIESH-HqZwI2VB2KDK'
details = get_playlist_details(playlist_id)
print(details)

# 5. 댓글 ----------------------------

def get_comments(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    request = youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id,
        maxResults=100,  # Adjust as needed
        textFormat='plainText'
    )

    while request:
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_data = {
                'user_id': comment['authorChannelId']['value'],
                'username': comment['authorDisplayName'],
                'comment': comment['textDisplay'],
                'likes': comment['likeCount'],
                'replies': []  # Will be filled later
            }

            # Check for replies
            if item['snippet']['totalReplyCount'] > 0:
                for reply in item['replies']['comments']:
                    reply_snippet = reply['snippet']
                    reply_data = {
                        'user_id': reply_snippet['authorChannelId']['value'],
                        'username': reply_snippet['authorDisplayName'],
                        'comment': reply_snippet['textDisplay'],
                        'likes': reply_snippet['likeCount']
                    }
                    comment_data['replies'].append(reply_data)

            comments.append(comment_data)
        
        request = youtube.commentThreads().list_next(request, response)

    return comments

# Example usage
video_id = 'A3eDb9ClCzg'  # Replace with the actual video ID
comments = get_comments(video_id, YOUTUBE_KEY)
print(comments)



