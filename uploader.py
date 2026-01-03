import json
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    raw = subprocess.check_output(
        ["python", "generate_short.py"],
        text=True
    )

    data = json.loads(raw)
    video_path = data["video"]
    title = data["title"]

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "#shorts #mindset #finance",
                "tags": ["finance", "psychology", "shorts"],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(video_path, resumable=True)
    )

    response = request.execute()
    print("UPLOADED:", response["id"])

if __name__ == "__main__":
    main()
