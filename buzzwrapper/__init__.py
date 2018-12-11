import os
import requests

CH_USERNAME = os.environ.get('CH_USERNAME', None)
CH_PASSWORD = os.environ.get('CH_PASSWORD', None)

class AuthMissingError(Exception):
    pass

if CH_USERNAME is None:
    raise AuthMissingError(
        "All methods require authentication and therefore a valid username."
    )

if CH_PASSWORD is None:
    raise AuthMissingError(
        "All methods require authentication and therefore a valid password."
    )

session = requests.Session()
session.params = {}
session.params["remember-me"] = "on"
session.params["username"] = CH_USERNAME
session.params["password"] = CH_PASSWORD
url = "https://forsight.crimsonhexagon.com/ch/login"
session.post(url)

session.params = {}
session.params["noExpiration"] = "true"
session.params["username"] = CH_USERNAME
session.params["password"] = CH_PASSWORD
url = "https://api.crimsonhexagon.com/api/authenticate"
response = session.get(url)
auth = response.json()["auth"]
session.params = {}
session.params["auth"] = auth

from .team import Team
from .monitor import Monitor
from .filter import Filter
