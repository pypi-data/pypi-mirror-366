import os

class Credentials:
    def __init__(self, credentials):
        self.user_name = credentials["user_name"]
        self.password = credentials["password"]
        self.team_id = credentials["team_id"]