from . import session


class Team(object):
    def __init__(self):
        pass

    @staticmethod
    def get_free_monitors():
        """Returns number of unused monitors for account."""
        monitors = len(Team.get_monitors())
        free_monitors = 10 - monitors
        return free_monitors

    @staticmethod
    def get_monitors():
        """Returns list of monitors for account."""
        url = "https://api.crimsonhexagon.com/api/monitor/list"
        response = session.get(url)
        json_data = response.json()
        return json_data["monitors"]
