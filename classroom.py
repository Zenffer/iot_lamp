import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
]
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"


def get_credentials() -> Credentials:
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def check_assignments() -> str:
    """
    Returns 'green' if all due assignments are turned in or returned,
    'orange' if any are still pending.
    """
    creds = get_credentials()
    service = build("classroom", "v1", credentials=creds)

    courses = service.courses().list(courseStates=["ACTIVE"]).execute()
    course_list = courses.get("courses", [])

    for course in course_list:
        course_id = course["id"]
        works = (
            service.courses()
            .courseWork()
            .list(courseId=course_id)
            .execute()
            .get("courseWork", [])
        )
        for work in works:
            subs = (
                service.courses()
                .courseWork()
                .studentSubmissions()
                .list(courseId=course_id, courseWorkId=work["id"], userId="me")
                .execute()
                .get("studentSubmissions", [])
            )
            for sub in subs:
                state = sub.get("state", "")
                if state not in ("TURNED_IN", "RETURNED"):
                    return "orange"

    return "green"


if __name__ == "__main__":
    result = check_assignments()
    print(f"Assignment status: {result}")
