import streamlit as st             # streamlit import
from googleapiclient.discovery import build
import mysql.connector
import pandas as pd                 
conn = mysql.connector.connect(
    host="127.0.0.1",           # if you are using The "localhost" leave it it will be the 127.0.0.1
    user="root",                # your user name of your user 
    password="************",    # Password of your database
    database="yt"               # Your database name when your run this query of "CREATE DATABASE <NAME>  you should give that name for it"
)
cursor = conn.cursor()
youtube_api_key = "try_to_make_your_own_APIKEY"         # your  API key buddy
def get_channel_info(channel_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)      
    request = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=channel_id
    )
    response = request.execute()
    return response['items'][0]

def create_videos_table():                  # query for videos table 
    query = """
    CREATE TABLE IF NOT EXISTS videos (
        Video_Id VARCHAR(255) PRIMARY KEY,
        Channel_Name VARCHAR(255) NOT NULL,
        Channel_Id VARCHAR(255),
        Title VARCHAR(255) NOT NULL,
        Tags VARCHAR(255),
        Thumbnail VARCHAR(255),
        Description VARCHAR(255),
        Published_Date VARCHAR(255),
        Duration VARCHAR(255),
        Views VARCHAR(255),
        Likes VARCHAR(255),
        Comments VARCHAR(255),
        Favorite_Count VARCHAR(255),
        Definition VARCHAR(255),
        Caption_Status VARCHAR(255)
    )
    """
    cursor.execute(query)
    conn.commit()
def main():
    create_videos_table()
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Channel Info", "Video Info"])
    if page == "Home":
        st.header("YouTube Data Harvesting and Warehousing using SQL and Streamlit" ,divider='blue')
        st.subheader("Looking for channel ID's")
        
        st.caption("• UCvKzzGO37oT83K0FwnUucxw ")
       
        st.caption("• UCbxRGdwZknPBUFlpkHxrjMQ ")
        
        st.write("Select an option from the sidebar to get started.")
        
    elif page == "Channel Info":
        st.title("YouTube Channel Info to MySQL")
        channel_id = st.text_input("Enter YouTube Channel ID:")
        if st.button("Get Channel Info"):
            channel_info = get_channel_info(channel_id)
            channel_name = channel_info['snippet']['title']
            subscriber_count = int(channel_info['statistics']['subscriberCount'])
            view_count = int(channel_info['statistics']['viewCount'])
            total_videos = int(channel_info['statistics']['videoCount'])
            channel_description = channel_info['snippet']['description']
            try:
                playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
            except KeyError:
                playlist_id = None
            save_to_database(channel_id, channel_name, subscriber_count, view_count, total_videos, channel_description, playlist_id)
            st.success("Channel Info Saved to MySQL!")

    elif page == "Video Info":
        st.title("YouTube Video Info")
        channel_id = st.text_input("Enter YouTube Channel ID:")
        if st.button("Fetch Videos"):
            videos = fetch_videos_by_channel_id(channel_id)
            if videos:
                st.write("Videos for Channel ID:", channel_id)
                df = pd.DataFrame(videos, columns=["Video_Id", "Channel_Name", "Channel_Id", "Title", "Tags", "Thumbnail", "Description", "Published_Date", "Duration", "Views", "Likes", "Comments", "Favorite_Count", "Definition", "Caption_Status"]
)
                st.write(df)
            else:
                st.write("No videos found for the given channel ID.")
    

def save_to_database(channel_id, channel_name, subscriber_count, view_count, total_videos, channel_description, playlist_id):
    query = "INSERT INTO channels (Channel_Id, Channel_Name, Subscribers, Views, Total_Videos, Channel_Description, Playlist_Id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (channel_id, channel_name, subscriber_count, view_count, total_videos, channel_description, playlist_id)
    cursor.execute(query, values)
    conn.commit()
    if playlist_id is not None:
        videos = fetch_videos_for_channel(playlist_id)
        for video in videos:
            insert_video_into_database(video)
def fetch_videos_by_channel_id(channel_id):
    query = "SELECT * FROM videos WHERE Channel_Id = %s"
    cursor.execute(query, (channel_id,))
    return cursor.fetchall()
def fetch_videos_for_channel(playlist_id):
    if playlist_id is None:
        return []
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    videos = []
    for item in response.get('items', []):
        video_id = item['snippet']['resourceId']['videoId']
        video_info = get_video_info(video_id)
        videos.append(video_info)
    return videos
def get_video_info(video_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()
    video_info = response['items'][0]
    return {
        'video_id': video_id,
        'channel_name': video_info['snippet']['channelTitle'],
        'channel_id': video_info['snippet']['channelId'],
        'title': video_info['snippet']['title'],
        'tags': ','.join(video_info['snippet'].get('tags', [])),
        'thumbnail': video_info['snippet']['thumbnails']['default']['url'],
        'description': video_info['snippet']['description'],
        'published_date': video_info['snippet']['publishedAt'],
        'duration': video_info['contentDetails']['duration'],
        'views': video_info['statistics']['viewCount'],
        'likes': video_info['statistics'].get('likeCount', '0'),
        'comments': video_info['statistics'].get('commentCount', '0'),
        'favorite_count': video_info['statistics'].get('favoriteCount', '0'),
        'definition': video_info['contentDetails']['definition'],
        'caption_status': video_info['contentDetails'].get('caption', 'notSet')
    }
def insert_video_into_database(video):
    max_description_length = 255
    description = video['description'][:max_description_length]
    query = """
    INSERT INTO videos (
        Video_Id, Channel_Name, Channel_Id, Title, Tags, Thumbnail, Description,
        Published_Date, Duration, Views, Likes, Comments, Favorite_Count,
        Definition, Caption_Status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        video['video_id'], video['channel_name'], video['channel_id'], video['title'],
        video['tags'], video['thumbnail'], description, video['published_date'],
        video['duration'], video['views'], video['likes'], video['comments'],
        video['favorite_count'], video['definition'], video['caption_status']
    )
    cursor.execute(query, values)
    conn.commit()           # the commit is used to commit the changes in the database
if __name__ == "__main__":
    main()
