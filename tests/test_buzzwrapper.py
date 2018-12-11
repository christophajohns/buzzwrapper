from pytest import fixture
from buzzwrapper import Team, Monitor, Filter
import vcr

@fixture
def monitor_keys():
    # Responsible only for returning the test data
    return ['geolocations', 'name', 'tags', 'gender', 'enabled', 'teamName', 'languages',
            'sources', 'resultsEnd', 'resultsStart', 'subfilters', 'keywords', 'timezone',
            'type', 'id', 'description']

@fixture
def age_data_keys():
    # Responsible only for returning the test data
    return ['startDate', 'endDate', 'numberOfDocuments', 'ageCount']

@fixture
def gender_data_keys():
    # Responsible only for returning the test data
    return ['startDate', 'endDate', 'numberOfDocuments', 'genderCounts']

@fixture
def sentiment_data_keys():
    # Responsible only for returning the test data
    return ['startDate', 'endDate', 'creationDate', 'numberOfDocuments', 'numberOfRelevantDocuments',
            'categories', 'emotions']

@fixture
def volume_data_keys():
    # Responsible only for returning the test data
    return ['startDate', 'endDate', 'numberOfDocuments']

@fixture
def posts_data_keys():
    # Responsible only for returning the test data
    return ['url', 'title', 'type', 'location', 'language', 'geolocation', 'assignedCategoryId',
            'assignedEmotionId', 'categoryScores', 'emotionScores']

@fixture
def delete_monitor_keys():
    # Responsible only for returning the test data
    return ['status', 'message']

@fixture
def delete_filter_keys():
    # Responsible only for returning the test data
    return ['status', 'message']


@vcr.use_cassette('tests/vcr_cassettes/team_get_monitors.yml', filter_query_paramters=['auth'])
def test_team_get_monitors(monitor_keys):
    """Tests an API call to get list of monitors"""

    response = Team.get_monitors()

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(monitor_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/team_get_free_monitors.yml', filter_query_paramters=['auth'])
def test_team_get_free_monitors():
    """Tests an API call to get number of free monitors"""

    response = Team.get_free_monitors()

    assert isinstance(response, int)

@vcr.use_cassette('tests/vcr_cassettes/monitor_get_age_data.yml', filter_query_paramters=['auth'])
def test_monitor_get_age_data(age_data_keys):
    """Tests an API call to get age counts for specific monitor"""

    response = Monitor(16180624304).get_age_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(age_data_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/monitor_get_gender_data.yml', filter_query_paramters=['auth'])
def test_monitor_get_gender_data(gender_data_keys):
    """Tests an API call to get gender counts for specific monitor"""

    response = Monitor(16180624304).get_gender_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(gender_data_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/monitor_get_sentiment_data.yml', filter_query_paramters=['auth'])
def test_monitor_get_sentiment_data(sentiment_data_keys):
    """Tests an API call to get sentiment counts for specific monitor"""

    response = Monitor(16180624304).get_sentiment_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(sentiment_data_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/monitor_get_volume_data.yml', filter_query_paramters=['auth'])
def test_monitor_get_volume_data(volume_data_keys):
    """Tests an API call to get volume counts for specific monitor"""

    response = Monitor(16180624304).get_volume_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(volume_data_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/monitor_get_posts_data.yml', filter_query_paramters=['auth'])
def test_monitor_get_posts_data(posts_data_keys):
    """Tests an API call to get posts for specific monitor"""

    response = Monitor(16180624304).get_posts_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(posts_data_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/monitor_add_delete.yml', filter_query_paramters=['auth'])
def test_add_delete_monitor(delete_monitor_keys):
    """Tests an API call to add and delete a monitor"""

    response_add = Monitor(title="Test Title", sources=["twitter"], keywords="Twitter", start="2016-01-01", end="2016-01-03")

    assert isinstance(response_add, Monitor)
    assert isinstance(response_add.id, int)

    response_delete = response_add.delete()

    assert isinstance(response_delete, dict)
    assert set(delete_monitor_keys).issubset(response_delete.keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/filter_add_delete.yml', filter_query_paramters=['auth'])
def test_add_delete_filter(delete_filter_keys):
    """Tests an API call to add and delete a filter"""

    response_add = Filter(monitor_id=17906955697 ,title="Test Title", keywords="Twitter")

    assert isinstance(response_add, Filter)
    assert isinstance(response_add.id, int)

    response_delete = response_add.delete()

    assert isinstance(response_delete, dict)
    assert set(delete_filter_keys).issubset(response_delete.keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/filter_get_age_data.yml', filter_query_paramters=['auth'])
def test_filter_get_age_data(age_data_keys):
    """Tests an API call to get age counts for specific filter"""

    response = Filter(17109666567).get_age_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(age_data_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/filter_get_gender_data.yml', filter_query_paramters=['auth'])
def test_filter_get_gender_data(gender_data_keys):
    """Tests an API call to get gender counts for specific filter"""

    response = Filter(17109666567).get_gender_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(gender_data_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/filter_get_sentiment_data.yml', filter_query_paramters=['auth'])
def test_filter_get_sentiment_data(sentiment_data_keys):
    """Tests an API call to get sentiment counts for specific filter"""

    response = Filter(17109666567).get_sentiment_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(sentiment_data_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/filter_get_volume_data.yml', filter_query_paramters=['auth'])
def test_filter_get_volume_data(volume_data_keys):
    """Tests an API call to get volume counts for specific filter"""

    response = Filter(17109666567).get_volume_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(volume_data_keys).issubset(response[0].keys()), "All keys should be in the response"

@vcr.use_cassette('tests/vcr_cassettes/filter_get_posts_data.yml', filter_query_paramters=['auth'])
def test_filter_get_posts_data(posts_data_keys):
    """Tests an API call to get posts for specific filter"""

    response = Filter(17109666567).get_posts_data(start="2016-01-01", end="2016-01-03")

    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert set(posts_data_keys).issubset(response[0].keys()), "All keys should be in the response"
