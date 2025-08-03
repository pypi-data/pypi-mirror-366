from .auth import Auth
from .base import App
from .files import Files
from .messages import Messages
from .permissions import Permissions
from .spreadsheets import SpreadSheets


class OmniClient:
    def __init__(self, app_id: str, app_secret: str):
        self.auth = Auth(app_id, app_secret)
        app = App(self.auth)

        self.files = Files(app)
        self.sheets = SpreadSheets(app)
        self.messages = Messages(app)
        self.permissions = Permissions(app)


# https://open.larkoffice.com/community/articles/7298446935350231044
# https://github.com/larksuite/oapi-sdk-python
