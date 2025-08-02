import os
from dotenv import load_dotenv
load_dotenv()

from scloud_api.auth.exceptions import AuthException
from scloud_api.auth import AuthToken

bad_credentials = {
    "user_name": "bad_user",
    "password": "bad_password",
    "team_id": "bad_team_id"
}

def test_auth_exception():
    e = AuthException("Error")
    assert e.message == "Error"

def test_bad_team_name():
    try:
        auth = AuthToken(cred=bad_credentials)
        auth.get_auth()
    except AuthException as e:
        assert e.message == "Team name not found. Please try again."

def test_bad_credentials():
    try:
        bad_credentials["team_id"] = os.getenv("TEAM_ID") # Set to a good team_id
        auth = AuthToken(cred=bad_credentials)
        auth.get_auth()
    except AuthException as e:
        assert e.message == "Sorry, invalid username or password"
