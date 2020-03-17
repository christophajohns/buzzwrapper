from . import session
from .helper import print_progress
from bs4 import BeautifulSoup
import time
import datetime
import csv
import xlrd


class Monitor(object):
    def __init__(self, id=None, title=None, sources=None, languages=[], keywords=None, start=None, end=None):
        self.title = title
        self.sources = sources
        self.languages = languages
        self.keywords = keywords
        self.start = start
        self.end = end
        if id == None and all([title, sources, keywords, start, end]):
            self.id = Monitor.add(title=title, sources=sources, languages=languages, keywords=keywords,
                start=start, end=end)
        else:
            self.id = id
            #TODO: Get info about monitor via API


    @staticmethod
    def add(title, sources, keywords, start, end, languages=[]):
        """Adds buzz monitor via Crimson Hexagon UI and returns monitor id after data is fully gathered."""
        url = "https://forsight.crimsonhexagon.com/ch/monitor/unifiedsetup?run=1"

        doc_types = [] # Build sources array with ids
        if "twitter" in sources:
            id = 16
            name = "twitter"
            dict = {'id': id, 'name': name}
            doc_types.append(dict)
        if "instagram" in sources:
            id = 733609702
            name = "instagram"
            dict = {'id': id, 'name': name}
            doc_types.append(dict)
        if "blogs" in sources:
            id = 10
            name = "blogs"
            options = [{'name': 'Posts', 'enabled': True}, {'name': 'Comments', 'enabled': True}]
            dict = {'id': id, 'name': name, 'options': options, 'genderIgnored': False, 'locationsIgnored': False}
            doc_types.append(dict)
        if "forums" in sources:
            id = 11
            name = "forums"
            dict = {'id': id, 'name': name}
            doc_types.append(dict)
        if "reddit" in sources:
            id = 8633753035
            name = "reddit"
            dict = {'id': id, 'name': name}
            doc_types.append(dict)
        if "googleplus" in sources:
            id = 733129938
            name = "googleplus"
            dict = {'id': id, 'name': name, 'genderIgnored': False}
            doc_types.append(dict)
        if "tumblr" in sources:
            id = 1177677775
            name = "tumblr"
            dict = {'id': id, 'name': name, 'genderIgnored': False, 'locationsIgnored': False}
            doc_types.append(dict)
        if "qq" in sources:
            id = 21
            name = "qq"
            dict = {'id': id, 'name': name}
            doc_types.append(dict)
        if "reviews" in sources:
            id = 20
            name = "reviews"
            dict = {'id': id, 'name': name, 'locationsIgnored': False}
            doc_types.append(dict)
        if "news" in sources:
            id = 12
            name = "news"
            dict = {'id': id, 'name': name, 'genderIgnored': False, 'locationsIgnored': False}
            doc_types.append(dict)
        if "youtube" in sources:
            id = 436455888
            name = "youtube"
            dict = {'id': id, 'name': name, 'locationsIgnored': False}
            doc_types.append(dict)


        params = {
            'brandAnalysisInfo': {
                'brandSearchTypeInfos': ['logos_and_keywords'],
                'enabled': True
            },
            'description': "",
            'docTypes': doc_types,
            'enabled': False,
            'endDate': end,
            'hasResults': False,
            'imageAnalysisInfo': {'enabled': True},
            'keywords': keywords,
            'keywordsMode': "freeform",
            'languages': languages,
            'languagesExcluded': False,
            'locationsExcluded': False,
            'monitorType': "BUZZ",
            'name': title,
            'privileged': False,
            'realTime': False,
            'runDelay': 0,
            'startDate': start
        }

        response = session.post(url, json=params)
        json_data = response.json()
        monitor_id = json_data['monitorId']
        # Return ID only when gathering data is finished
        status_percent = Monitor.get_status(monitor_id)
        while (status_percent != 100):
            status_percent = Monitor.get_status(monitor_id)
            # Update Progress Bar
            print_progress(status_percent, 100, prefix = 'Progress:', suffix = 'Complete', bar_length=50)
            time.sleep(5)
        return monitor_id


    def delete(self):
        """Deletes monitor specified by monitor id and returns response dict whether action was successful."""
        url = "https://forsight.crimsonhexagon.com/ch/monitor/unifiedsetup?id="+str(self.id)
        resp = session.delete(url)
        status = resp.status_code

        if status == 200:
            status = 'success'
            message = 'The filter was successfully deleted.'
        else:
            status = 'error'
            message = 'There must have been an error. Maybe the cookie is not valid anymore.'
        response = {'status': status, 'message': message}
        return response


    @staticmethod
    def get_status(id):
        """Returns progress in gathering data for monitor or filter in percent."""
        url = "https://forsight.crimsonhexagon.com/ch/opinion/status?id=" + str(id)
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        status_text = soup.find('h2').get_text()
        status_percent = int(status_text.split(': ')[1].split('%')[0])
        return status_percent


    def get_age_data(self, start, end):
        """Return age data of monitor with a certain id for the specified time range as a list of dicts."""
        url = "https://api.crimsonhexagon.com/api/monitor/demographics/age"
        params = {
            "auth": session.params['auth'],
            "id": self.id,
            "start": start,
            "end": end
        }
        session.params = params
        response = session.get(url)
        json_data = response.json()
        return json_data["ageCounts"]


    def age_to_csv(self, start, end, output_filename="age_data.csv"):
        """Saves age data of monitor with id=id for specified time range as a csv-file."""
        age_data = self.get_age_data(start=start, end=end)
        with open(output_filename, 'w+') as output_file:
            writer = csv.writer(output_file)
            writer.writerow([
                'date',
                'number_of_documents',
                'total_age_count',
                'zero_to_seventeen',
                'eighteen_to_twentyfour',
                'twentyfive_to_thirtyfour',
                'thirtyfive_and_over'
            ])

            for i in range(len(age_data)):
                start = age_data[i]['startDate']
                number_of_documents = age_data[i]['numberOfDocuments']
                total_age_count = age_data[i]['ageCount']['totalAgeCount']
                zero_to_seventeen = None
                eighteen_to_twentyfour = None
                twentyfive_to_thirtyfour = None
                thirtyfive_and_over = None

                if 'ZERO_TO_SEVENTEEN' in age_data[i]['ageCount']['sortedAgeCounts'].keys(): zero_to_seventeen = age_data[i]['ageCount']['sortedAgeCounts']['ZERO_TO_SEVENTEEN']
                if 'EIGHTEEN_TO_TWENTYFOUR' in age_data[i]['ageCount']['sortedAgeCounts'].keys(): eighteen_to_twentyfour = age_data[i]['ageCount']['sortedAgeCounts']['EIGHTEEN_TO_TWENTYFOUR']
                if 'TWENTYFIVE_TO_THIRTYFOUR' in age_data[i]['ageCount']['sortedAgeCounts'].keys(): twentyfive_to_thirtyfour = age_data[i]['ageCount']['sortedAgeCounts']['TWENTYFIVE_TO_THIRTYFOUR']
                if 'THIRTYFIVE_AND_OVER' in age_data[i]['ageCount']['sortedAgeCounts'].keys(): thirtyfive_and_over = age_data[i]['ageCount']['sortedAgeCounts']['THIRTYFIVE_AND_OVER']

                writer.writerow([
                    start,
                    number_of_documents,
                    total_age_count,
                    zero_to_seventeen,
                    eighteen_to_twentyfour,
                    twentyfive_to_thirtyfour,
                    thirtyfive_and_over
                ])


    def get_gender_data(self, start, end):
        """Return gender data of monitor with a certain id for the specified time range as a list of dicts."""
        url = "https://api.crimsonhexagon.com/api/monitor/demographics/gender"
        params = {
            "auth": session.params['auth'],
            "id": self.id,
            "start": start,
            "end": end
        }
        session.params = params
        response = session.get(url)
        json_data = response.json()
        return json_data["genderCounts"]


    def gender_to_csv(self, start, end, output_filename="gender_data.csv"):
        """Saves gender data of monitor with id=id for specified time range as a csv-file."""
        gender_data = self.get_gender_data(start=start, end=end)
        with open(output_filename, 'w+') as output_file:
            writer = csv.writer(output_file)
            writer.writerow([
                'date',
                'number_of_documents',
                'total_gendered_count',
                'male_count',
                'female_count'
            ])

            for i in range(len(gender_data)):
                start = gender_data[i]['startDate']
                number_of_documents = gender_data[i]['numberOfDocuments']
                total_gendered_count = gender_data[i]['genderCounts']['totalGenderedCount']
                male_count = None
                female_count = None

                if 'maleCount' in gender_data[i]['genderCounts'].keys(): male_count = gender_data[i]['genderCounts']['maleCount']
                if 'femaleCount' in gender_data[i]['genderCounts'].keys(): female_count = gender_data[i]['genderCounts']['femaleCount']

                writer.writerow([
                    start,
                    number_of_documents,
                    total_gendered_count,
                    male_count,
                    female_count
                ])


    def get_sentiment_data(self, start, end):
        """Return sentiment data of monitor by id for the specified time range as a list of dicts."""
        url = "https://api.crimsonhexagon.com/api/monitor/results"
        params = {
            "auth": session.params['auth'],
            "id": self.id,
            "start": start,
            "end": end
        }
        session.params = params
        response = session.get(url)
        json_data = response.json()
        return json_data['results']


    def sentiment_to_csv(self, start, end, output_filename="sentiment_data.csv"):
        """Saves sentiment data of monitor by id for specified time range as a csv-file."""
        sentiment_data = self.get_sentiment_data(start=start, end=end)
        with open(output_filename, 'w+') as output_file:
            writer = csv.writer(output_file)
            writer.writerow([
                'date',
                'number_of_documents',
                'number_of_relevant_documents',
                'basic_negative',
                'basic_neutral',
                'basic_positive',
                'fear',
                'surprise',
                'sadness',
                'anger',
                'disgust',
                'joy',
                'neutral',
            ])

            for i in range(len(sentiment_data)):
                start = sentiment_data[i]['startDate']
                numberOfDocuments = sentiment_data[i]['numberOfDocuments']
                numberOfRelevantDocuments = sentiment_data[i]['numberOfRelevantDocuments']
                categories_by_id = build_dict(sentiment_data[i]['categories'], key='category')
                basicNegative = categories_by_id.get('Basic Negative')['volume']
                basicNeutral = categories_by_id.get('Basic Neutral')['volume']
                basicPositive = categories_by_id.get('Basic Positive')['volume']
                emotions_by_id = build_dict(sentiment_data[i]['emotions'], key='category')
                fear = emotions_by_id.get('Fear')['volume']
                surprise = emotions_by_id.get('Surprise')['volume']
                sadness = emotions_by_id.get('Sadness')['volume']
                anger = emotions_by_id.get('Anger')['volume']
                disgust = emotions_by_id.get('Disgust')['volume']
                joy = emotions_by_id.get('Joy')['volume']
                neutral = emotions_by_id.get('Neutral')['volume']

                writer.writerow([
                    start,
                    numberOfDocuments,
                    numberOfRelevantDocuments,
                    basicNegative,
                    basicNeutral,
                    basicPositive,
                    fear,
                    surprise,
                    sadness,
                    anger,
                    disgust,
                    joy,
                    neutral
                ])


    def get_volume_data(self, start, end):
        """Return volume data of monitor by id for the specified time range as a list of dicts."""
        url = "https://api.crimsonhexagon.com/api/monitor/volume"
        params = {
            "auth": session.params['auth'],
            "id": self.id,
            "start": start,
            "end": end
        }
        session.params = params
        response = session.get(url)
        json_data = response.json()
        return json_data['volume']


    def volume_to_csv(self, start, end, output_filename="volume_data.csv"):
        """Saves volume data of monitor by id for specified time range as a csv-file."""
        volume_data = self.get_volume_data(start=start, end=end)
        with open(output_filename, 'w+') as output_file:
            writer = csv.writer(output_file)
            writer.writerow([
                'date',
                'volume'
            ])

            for i in range(len(volume_data)):
                start = volume_data[i]['startDate']
                volume = volume_data[i]['numberOfDocuments']

                writer.writerow([
                    start,
                    volume
                ])


    def get_posts_data(self, start, end):
        """Return posts data of monitor with a certain id for the specified time range as a list of dicts."""
        url = "https://api.crimsonhexagon.com/api/monitor/posts"
        params = {
            "auth": session.params['auth'],
            "id": self.id,
            "start": start,
            "end": end,
            "extendLimit": True,
            "fullContents": True
        }
        session.params = params
        response = session.get(url)
        json_data = response.json()
        return json_data["posts"]


    def posts_to_csv(self, start, end, output_filename="posts_data.csv"):
        """Saves posts data of monitor with id=id for spcified time range as a csv-file."""
        posts_data = self.get_posts_data(start=start, end=end)
        with open(output_filename, 'w+') as output_file:
            writer = csv.writer(output_file)
            writer.writerow([
                'url',
                'date',
                'author',
                'contents',
                'title',
                'type',
                'language',
                'assigned_category',
                'assigned_emotion',
                'basic_positive',
                'basic_neutral',
                'basic_negative',
                'fear',
                'anger',
                'joy',
                'sadness',
                'surprise',
                'neutral',
                'disgust'
            ])

            for i in range(len(posts_data)):
                url = posts_data[i]['url'] if ('url' in posts_data[i]) else None
                date = posts_data[i]['date'] if ('date' in posts_data[i]) else None
                author = posts_data[i]['author'] if ('author' in posts_data[i]) else None
                contents = posts_data[i]['contents'] if ('contents' in posts_data[i]) else None
                title = posts_data[i]['title'] if ('title' in posts_data[i]) else None
                type = posts_data[i]['type'] if ('type' in posts_data[i]) else None
                language = posts_data[i]['language'] if ('language' in posts_data[i]) else None
                assigned_category = None
                if ('assignedCategoryId' in posts_data[i]):
                    assigned_category_id = int(posts_data[i]['assignedCategoryId'])
                    if assigned_category_id == 3618925528: assigned_category = "Basic Positive"
                    if assigned_category_id == 3618925529: assigned_category = "Basic Neutral"
                    if assigned_category_id == 3618925530: assigned_category = "Basic Negative"
                assigned_emotion = None
                if ('assignedEmotionId' in posts_data[i]):
                    assigned_emotion_id = int(posts_data[i]['assignedEmotionId'])
                    if assigned_emotion_id == 3618925540: assigned_emotion = "Fear"
                    if assigned_emotion_id == 3618925536: assigned_emotion = "Anger"
                    if assigned_emotion_id == 3618925537: assigned_emotion = "Joy"
                    if assigned_emotion_id == 3618925538: assigned_emotion = "Sadness"
                    if assigned_emotion_id == 3618925539: assigned_emotion = "Surprise"
                    if assigned_emotion_id == 3618925534: assigned_emotion = "Neutral"
                    if assigned_emotion_id == 3618925535: assigned_emotion = "Disgust"
                category_scores = posts_data[i]['categoryScores']
                basic_positive_dict = next((category for category in category_scores if int(category['categoryId']) == 3618925528), None)
                basic_positive = basic_positive_dict['score'] if basic_positive_dict else None
                basic_neutral_dict = next((category for category in category_scores if int(category['categoryId']) == 3618925529), None)
                basic_neutral = basic_neutral_dict['score'] if basic_neutral_dict else None
                basic_negative_dict = next((category for category in category_scores if int(category['categoryId']) == 3618925530), None)
                basic_negative = basic_negative_dict['score'] if basic_negative_dict else None
                emotion_scores = posts_data[i]['emotionScores']
                fear_dict = next((emotion for emotion in emotion_scores if int(emotion['emotionId']) == 3618925540), None)
                fear = fear_dict['score'] if fear_dict else None
                anger_dict = next((emotion for emotion in emotion_scores if int(emotion['emotionId']) == 3618925536), None)
                anger = anger_dict['score'] if anger_dict else None
                joy_dict = next((emotion for emotion in emotion_scores if int(emotion['emotionId']) == 3618925537), None)
                joy = joy_dict['score'] if joy_dict else None
                sadness_dict = next((emotion for emotion in emotion_scores if int(emotion['emotionId']) == 3618925538), None)
                sadness = sadness_dict['score'] if sadness_dict else None
                surprise_dict = next((emotion for emotion in emotion_scores if int(emotion['emotionId']) == 3618925539), None)
                surprise = surprise_dict['score'] if surprise_dict else None
                neutral_dict = next((emotion for emotion in emotion_scores if int(emotion['emotionId']) == 3618925534), None)
                neutral = neutral_dict['score'] if neutral_dict else None
                disgust_dict = next((emotion for emotion in emotion_scores if int(emotion['emotionId']) == 3618925535), None)
                disgust = disgust_dict['score'] if disgust_dict else None
                writer.writerow([
                    url,
                    date,
                    author,
                    contents,
                    title,
                    type,
                    language,
                    assigned_category,
                    assigned_emotion,
                    basic_positive,
                    basic_neutral,
                    basic_negative,
                    fear,
                    anger,
                    joy,
                    sadness,
                    surprise,
                    neutral,
                    disgust
                ])


    def get_influencers_single_date(self, date):
        """Return influencer data of monitor with a certain id for the specified date as a list of dicts."""
        url = "https://forsight.crimsonhexagon.com/ch/opinion/export?id="+str(self.id)+"&start="+date+"&end="+date+"&export=INFLUENCER_SUMMARY&format=EXCEL&authorsLoaded=100"
        resp = session.get(url, allow_redirects=True)

        day = datetime.datetime.strptime(date, '%Y-%m-%d')
        day_after = day + datetime.timedelta(days=1)

        date = day.isoformat()
        date_after = day_after.isoformat()

        influencer = {
            'startDate': date,
            'endDate': date_after,
            'influencer': []
        }

        xls_file = resp.content
        wb = xlrd.open_workbook(file_contents=xls_file)
        sh = wb.sheet_by_index(0)

        # Print all values, iterating through rows and columns
        for row_idx in range(2, sh.nrows):    # Iterate through rows
            author = sh.cell_value(row_idx, 0)  # Get cell value by row, col
            tweets = int(sh.cell_value(row_idx, 1))  # Get cell value by row, col
            following = int(sh.cell_value(row_idx, 2))  # Get cell value by row, col
            follower = int(sh.cell_value(row_idx, 3))  # Get cell value by row, col
            influencer_score = sh.cell_value(row_idx, 4)  # Get cell value by row, col

            influencer_dict = {
                'author': author.encode('UTF-8'),
                'tweets': tweets,
                'following': following,
                'follower': follower,
                'influencer_score': influencer_score
            }
            influencer['influencer'].append(influencer_dict)

        return influencer


    def get_influencer_data(self, start, end):
        """Return influencer data of monitor with a certain id for the
        specified date range as a list of list dicts."""
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d')

        start_end_daterange = daterange(start_date=start_date, end_date=end_date)

        influencer_data = []

        for single_date in start_end_daterange:
            single_date_str = single_date.strftime('%Y-%m-%d')
            influencer_dict = self.get_influencers_single_date(date=single_date_str)
            influencer_data.append(influencer_dict)

        return influencer_data


    def influencer_to_csv(self, start, end, output_filename="influencer_data.csv"):
        """Saves influencer data of monitor with id=id for specified time range as a csv-file."""
        influencer_data = self.get_influencer_data(start=start, end=end)
        with open(output_filename, 'w+') as output_file:
            writer = csv.writer(output_file)
            writer.writerow([
                'date',
                'author',
                'tweets',
                'following',
                'follower',
                'influencer_score'
            ])

            for i in range(len(influencer_data)):
                start = influencer_data[i]['startDate']
                for influencer in influencer_data[i]['influencer']:
                    author = influencer['author']
                    tweets = influencer['tweets']
                    following = influencer['following']
                    follower = influencer['follower']
                    influencer_score = influencer['influencer_score']
                    writer.writerow([
                        start,
                        author,
                        tweets,
                        following,
                        follower,
                        influencer_score
                    ])


'''
Helper Functions
'''


def daterange(start_date, end_date):
    """
    Returns list of dates from start to end date in format YYYY-MM-DD.
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def build_dict(seq, key):
    """
    Returns from dictionary in form {'id':'1234', 'name':'Tom'} a dictionary in
    form {'index':1, 'id':'1234', 'name':'Tom'} with index signaling position
    of dict and seq where key = value
    Source: https://stackoverflow.com/questions/4391697/find-the-index-of-a-dict-within-a-list-by-matching-the-dicts-value
    """
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))
