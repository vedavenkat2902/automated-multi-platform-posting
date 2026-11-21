
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Blogger publishing permission
SCOPES = [
    "https://www.googleapis.com/auth/blogger"
]

# File locations
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def authenticate_blogger():

    credentials = None

    # Load previously saved credentials
    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    # Refresh or request new authorization
    if not credentials or not credentials.valid:

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            credentials = flow.run_local_server(
                port=0,
                access_type="offline",
                prompt="consent"
            )

        # Save credentials locally
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(credentials.to_json())

    # Connect to Blogger API
    service = build(
        "blogger",
        "v3",
        credentials=credentials
    )

    return service


def get_blog_details():

    try:
        service = authenticate_blogger()

        # Retrieve blogs belonging to the authenticated user
        response = service.blogs().listByUser(
            userId="self"
        ).execute()

        blogs = response.get("items", [])

        if not blogs:
            print("No Blogger blogs found.")
            return

        print("\nBlogger authentication successful!")
        print("\nYour blogs:\n")

        for blog in blogs:
            print("Blog Name:", blog.get("name"))
            print("Blog URL:", blog.get("url"))
            print("Blog ID:", blog.get("id"))
            print("-" * 40)

    except Exception as error:
        print("Blogger authentication failed.")
        print("Error:", error)


if __name__ == "__main__":
    get_blog_details()
