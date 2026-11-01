
import os
import json
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def download_audio_assets():
    credentials_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    folder_id = os.environ["AUDIO_DRIVE_FOLDER_ID"]

    credentials = service_account.Credentials.from_service_account_info(
        json.loads(credentials_json),
        scopes=SCOPES,
    )

    service = build("drive", "v3", credentials=credentials)

    def download_folder(folder_id, destination):
        destination.mkdir(parents=True, exist_ok=True)

        page_token = None
        while True:
            response = service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="nextPageToken, files(id,name,mimeType)",
                pageToken=page_token,
                pageSize=100,
            ).execute()

            for item in response.get("files", []):
                name = item["name"]
                file_id = item["id"]

                if item["mimeType"] == "application/vnd.google-apps.folder":
                    download_folder(file_id, destination / name)
                elif name.lower().endswith(".mp3"):
                    request = service.files().get_media(fileId=file_id)
                    path = destination / name

                    with path.open("wb") as file_handle:
                        downloader = MediaIoBaseDownload(file_handle, request)
                        done = False
                        while not done:
                            _, done = downloader.next_chunk()

                    print(f"Downloaded: {path}")

            page_token = response.get("nextPageToken")
            if not page_token:
                break

    download_folder(folder_id, Path("assets"))
    print("Audio asset download completed.")
