import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# Placeholder for your YouTube Data API key
# It's recommended to load this from environment variables or a secure configuration management system
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', 'YOUR_YOUTUBE_API_KEY_HERE')

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube_service():
    """Initializes and returns a YouTube Data API service object."""
    # Disable OAuthlib's HTTPS verification when running locally.
    # DO NOT leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # For simple API key access (read-only for public data)
    if YOUTUBE_API_KEY and YOUTUBE_API_KEY != 'YOUR_YOUTUBE_API_KEY_HERE':
        return googleapiclient.discovery.build(api_service_name, api_version, developerKey=YOUTUBE_API_KEY)
    else:
        # For authenticated access (e.g., if you need to download private captions)
        # This part requires client_secrets.json and a more involved OAuth flow
        # For this application's scope (public captions), an API key is usually sufficient.
        # If you need to handle user-specific content, you'll need to implement the full OAuth flow.
        print("Warning: YOUTUBE_API_KEY not set or invalid. Attempting OAuth flow (requires client_secrets.json).")
        try:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES)
            credentials = flow.run_local_server(port=0)
            return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
        except Exception as e:
            print(f"Error during OAuth flow: {e}")
            print("Please ensure 'client_secrets.json' is configured correctly or set YOUTUBE_API_KEY.")
            return None

def get_video_details(video_id):
    """Fetches details for a given YouTube video ID."""
    youtube = get_youtube_service()
    if not youtube:
        return None

    try:
        request = youtube.videos().list(
            part="snippet,contentDetails",
            id=video_id
        )
        response = request.execute()
        if response and response['items']:
            return response['items'][0]
        else:
            print(f"No video found for ID: {video_id}")
            return None
    except googleapiclient.errors.HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching video details: {e}")
        return None

def get_video_captions(video_id):
    """Fetches available caption tracks for a given YouTube video ID."""
    youtube = get_youtube_service()
    if not youtube:
        return None

    try:
        request = youtube.captions().list(
            part="snippet",
            videoId=video_id
        )
        response = request.execute()
        if response and response['items']:
            return response['items']
        else:
            print(f"No captions found for video ID: {video_id}. It might not have captions or they are restricted.")
            return []
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 403:
            print(f"Access denied to captions for video ID: {video_id}. Video owner may have restricted access.")
        else:
            print(f"An HTTP error {e.resp.status} occurred while listing captions: {e.content}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while listing captions: {e}")
        return None

def download_caption_track(caption_id):
    """Downloads a specific caption track by its ID."""
    youtube = get_youtube_service()
    if not youtube:
        return None

    try:
        # Note: The captions.download method requires OAuth 2.0 authorization,
        # even for public captions. An API key alone is not sufficient for this specific call.
        # If you are using only an API key, this part will fail.
        # For a full application, you would need to implement the OAuth flow for the user.
        # Alternatively, for public videos, you might use a third-party library like `youtube-dl` or `yt-dlp`
        # to extract captions without direct API `download` method, but that's outside YouTube Data API scope.
        request = youtube.captions().download(
            id=caption_id,
            tfmt="srt" # or "ttml", "vtt"
        )
        response = request.execute()
        return response # This will be the raw caption content (e.g., SRT string)
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 403:
            print(f"Access denied to download caption ID: {caption_id}. This usually requires OAuth 2.0 authorization.")
        else:
            print(f"An HTTP error {e.resp.status} occurred while downloading caption: {e.content}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while downloading caption: {e}")
        return None

if __name__ == '__main__':
    # Example Usage:
    # Replace with a valid YouTube video ID
    video_id = "dQw4w9WgXcQ" # Example: Rick Astley - Never Gonna Give You Up

    print(f"\n--- Fetching details for video ID: {video_id} ---")
    details = get_video_details(video_id)
    if details:
        print(f"Video Title: {details['snippet']['title']}")
        print(f"Published At: {details['snippet']['publishedAt']}")
        print(f"Channel Title: {details['snippet']['channelTitle']}")

    print(f"\n--- Fetching captions for video ID: {video_id} ---")
    captions = get_video_captions(video_id)
    if captions:
        print(f"Found {len(captions)} caption tracks:")
        for caption in captions:
            print(f"  ID: {caption['id']}, Language: {caption['snippet']['language']}, Name: {caption['snippet']['name']}")
            # To download, you would typically pick a specific language, e.g., 'en'
            if caption['snippet']['language'] == 'en':
                print(f"Attempting to download English caption track: {caption['id']}")
                # Note: This download will likely fail without proper OAuth 2.0 credentials
                # as explained in the download_caption_track function.
                # For demonstration, we'll just show the call.
                downloaded_content = download_caption_track(caption['id'])
                if downloaded_content:
                    print("Successfully initiated caption download (content not printed for brevity).")
                else:
                    print("Failed to download caption content (likely due to authorization).")
    else:
        print("No captions or failed to retrieve captions.")
