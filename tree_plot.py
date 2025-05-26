from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import json
from dotenv import load_dotenv

load_dotenv()

# 환경 변수에서 민감 정보 가져오기
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

# 임시 JSON 파일 생성
client_config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

with open("temp_client_secrets.json", "w") as f:
    json.dump(client_config, f)

# 인증 처리
gauth = GoogleAuth()
gauth.LoadClientConfigFile("temp_client_secrets.json")
gauth.LocalWebserverAuth()

# PyDrive 구동
drive = GoogleDrive(gauth)

# 업로드 함수
def upload_to_folder(image_path, folder_id):
    file = drive.CreateFile({
        'title': os.path.basename(image_path),
        'parents': [{'id': folder_id}]
    })
    file.SetContentFile(image_path)
    file.Upload()
    file.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
    return f"https://drive.google.com/uc?id={file['id']}&export=download"

# 인증 후 temp 파일 삭제 (선택 사항)
os.remove("temp_client_secrets.json")
