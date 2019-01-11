from buzzwrapper import Team, Monitor, Filter
import os
import itertools
import datetime
import pandas
import multiprocessing.pool

def make_data_dir(source):
    """Make Directory for Output Data"""
    data_dir = "data_sequ/" + source + "/"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def make_brand_dir(data_dir, corporate_brand):
    """Make Directory for Output Data"""
    brand_dir = data_dir + corporate_brand + "/"
    if not os.path.exists(brand_dir):
        os.makedirs(brand_dir)
    return brand_dir


def make_query_dir(brand_dir, short_query):
    """Make Directory for Output Data"""
    return make_brand_dir(brand_dir, short_query)


def get_brands_dict(xl_file):
    """Makes list of dicts that holds data about brands like name, abbreviation and keywords"""
    df = pandas.read_excel(xl_file)
    corporate_brands = df.corporate_brand.unique()
    brands = []
    for corporate_brand in corporate_brands:
        product_brands = df.loc[df.corporate_brand == corporate_brand]
        pbrands = []
        for prodcut_brand in product_brands.itertuples():
            pbrand = {"name": prodcut_brand.brand, "keywords": prodcut_brand.keywords, "short": prodcut_brand.abbreviation}
            pbrands.append(pbrand)
        cb_dict = {"corporate_brand": corporate_brand, "brands": pbrands}
        brands.append(cb_dict)
    return brands


def print_progress(index, length, description, single_desc):
    """print progress and description (e.g. [1/10] sources: twitter)"""
    print "[" + str(index+1) + "/" + str(length) + "] " + description + ": " + single_desc


def get_or_query(brands):
    """keyword query used for monitor, e.g. Abercrombie&Fitch OR Hollister OR Abercrombie Kids"""
    or_query = "(" + ") OR (".join([brand["keywords"] for brand in brands]) + ")"
    return or_query


def get_keyword_query(combination):
    """keyword query used for filter, e.g. Abercrombie&Fitch AND Hollister"""
    keyword_query = "(" + ") AND (".join([brand["keywords"] for brand in combination]) + ")"
    return keyword_query


def get_short_query(combination):
    """short version of the keyword query, e.g. A&F_HL for Abercrombie&Fitch AND Hollister"""
    short_query = "_".join([brand["short"] for brand in combination])
    return short_query


def chunks(l, n):
    """Return successive n-sized chunks from l as list."""
    l_total = []
    for i in range(0, len(l), n):
        l_total.append(l[i:i + n])
    return l_total


def get_combinations(brands):
    combinations = []
    for L in range(1, len(brands)+1):
        for subset in itertools.combinations(brands, L):
            combinations.append(list(subset))
    return combinations


def get_monitor_data(combinations, title, source, keywords, data_dir, progress):
    print progress + " monitors: Adding monitor for " + title + "..."
    # add buzz monitor
    new_monitor = Monitor(title=title, sources=source, languages=languages, keywords=keywords, start=start, end=end)
    monitor_id = new_monitor.id
    # for each combination
    for combi_index, combination in enumerate(combinations):
        progress = "[" + str(combi_index+1) + "/" + str(len(combinations)) + "]"
        # make keyword query
        keyword_query = get_keyword_query(combination)
        # make short query
        short_query = get_short_query(combination)
        # make a data directory
        query_dir = make_query_dir(data_dir, short_query)
        # save keyword query in txt-file
        with open(query_dir + "keywords.txt", "w+") as txt_file: txt_file.write(keyword_query)
        # get data for combination (sequential)
        get_filter_data(monitor_id, keyword_query, short_query, query_dir, progress)
    # delete buzz monitor
    new_monitor.delete()


def get_filter_data(monitor_id, keywords, title, query_dir, progress):
    print progress + " filters: Adding filter for " + title + "..."
    # make filter
    new_filter = Filter(monitor_id=monitor_id, title=title, keywords=keywords)
    # save volume_data to csv
    print "Getting volume data for "+title+"..."
    new_filter.volume_to_csv(start=start, end=end, output_filename=query_dir+"volume_data.csv")
    # save sentiment_data to csv
    print "Getting sentiment data for "+title+"..."
    new_filter.sentiment_to_csv(start=start, end=end, output_filename=query_dir+"sentiment_data.csv")


# -- MAIN ----------------
if __name__ == '__main__':
    # Start Time
    start_time = datetime.datetime.now()

    # number of usable free monitors
    free_monitors = Team.get_free_monitors()

    # Input
    start = "2008-06-01"
    end = "2018-06-01"
    xl_file = "keywords.xlsx"
    brands = get_brands_dict(xl_file)
    sources = [
        ["twitter"],
        # ["blogs"],
        # ["forums"],
        # ["reddit"],
        # ["googleplus"],
        # ["tumblr"],
        # ["qq"],
        # ["reviews"],
        # ["news"],
        # ["youtube"],
        # ["blogs", "news"], # Control for Overlap between Blogs and News by having an additional monitor with sources "Blogs AND News"
    ]
    languages = [
        "en",
    ]


    # for each source
    for source_index, source in enumerate(sources):
        # print progress and source (e.g. [1/10] sources: twitter)
        print_progress(source_index, len(sources), "sources", " AND ".join(source))
        # make data directory
        data_dir = make_data_dir("&".join(source))
        # for each corporate_brand
        for cbrand_index, corporate_brand in enumerate(brands):
            progress = "[" + str(cbrand_index+1) + "/" + str(len(brands)) + "]"
            # make data directory
            brand_dir = make_brand_dir(data_dir, corporate_brand["corporate_brand"])
            # make OR query
            pbrands = corporate_brand["brands"] # product_brands / brands
            or_query = get_or_query(pbrands)
            # save or query in txt-file
            with open(brand_dir + "keywords.txt", "w+") as txt_file: txt_file.write(or_query)
            # make combinations (due to filter limit of 50 per monitor we have to process the combinations in chunks of 50)
            all_combinations = get_combinations(pbrands)
            combi_chunks = chunks(all_combinations, 50)
            # get data for every combination
            for combinations in combi_chunks:
                get_monitor_data(combinations, corporate_brand["corporate_brand"], source, or_query, brand_dir, progress)
    # Print Total Time elapsed
    print datetime.datetime.now() - start_time
