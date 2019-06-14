from . import session
from .helper import print_progress
from . import Monitor
from bs4 import BeautifulSoup
import time

class Filter(Monitor):
    def __init__(self, id=None, monitor_id=None, title=None, keywords=None):
        self.monitor_id = monitor_id
        self.title = title
        self.keywords = keywords
        if id == None and all([monitor_id, title, keywords]):
            self.id = Filter.add(monitor_id=monitor_id, title=title, keywords=keywords)
        else:
            self.id = id

    @staticmethod
    def add(monitor_id, title, keywords):
        """Adds filter with keywords and title to a buzz monitor specified by id and returns filter id."""
        url = "https://forsight.crimsonhexagon.com/ch/monitor/" + str(monitor_id) + "/filter"
        params = {'description': keywords, 'details': {'keywords': keywords}, 'title': title}
        resp = session.post(url, json=params)
        json_data = resp.json()
        filter_id = json_data['filterId']
        # Return ID only when gathering data is finished
        status_percent = Monitor.get_status(filter_id)
        while (status_percent != 100):
            status_percent = Monitor.get_status(filter_id)
            # Update Progress Bar
            print_progress(status_percent, 100, prefix = 'Progress:', suffix = 'Complete', bar_length=50)
            time.sleep(5)
        return filter_id

    def delete(self):
        """Deletes filter specified by monitor and filter id and returns response dict whether action was successful."""
        url = "https://forsight.crimsonhexagon.com/ch/monitor/" + str(self.monitor_id) + "/filter/" + str(self.id)

        resp = session.delete(url)

        status = resp.status_code

        if status == 200:
            status = 'success'
            message = 'The filter was successfully edited.'
        else:
            status = 'error'
            message = 'There must have been an error. Maybe the cookie is not valid anymore.'
        response = {'status': status, 'message': message}
        return response
