# Functions that do not import from other project files
import json
import requests as rq
import decimal as dc
import time

QUERY_URL = "https://graphql.anilist.co/"

QUERY = """query($id: Int){
  Media(id: $id, type: ANIME){
    title {
      romaji
      english
      native
    },
    genres,
    tags {
      name,
      rank,
      isMediaSpoiler
    },
    averageScore,
    externalLinks {
      site
    }
    format,
    status,
    description,
    episodes,
    relations{
      edges{
        relationType,
        node{
          id,
          type,
        }
      }
    },
    coverImage {
      medium,
      large,
      extraLarge
    }
  }
}"""

STREAM_INFO = {
            "crunchyroll": {"seasons": 0,
                            "movies": 0
                            },
            "funimation":  {"seasons": 0,
                            "movies": 0
                            },
            "prison":      {"seasons": 0,
                            "movies": 0
                            },
            "amazon":      {"seasons": 0,
                            "movies": 0
                            },
            "vrv":         {"seasons": 0,
                            "movies": 0
                            },
            "hulu":        {"seasons": 0,
                            "movies": 0
                            },
            "youtube":     {"seasons": 0,
                            "movies": 0
                            },
            "tubi":        {"seasons": 0,
                            "movies": 0
                            },
            "hbo":         {"seasons": 0,
                            "movies": 0
                            },
            "hidive":      {"seasons": 0,
                            "movies": 0
                            }
        }


def graph_data_selection(ratings: list, x_data: str, y_data: str):
    """
    Selects and returns the data to be displayed on a graph.

    From a list of dictionaries containing appropriate keys, data is sorted into categories. The user's selection is
    determined, and the appropriate lists of ratings are sorted into coordinates and put into a list which is turned
    into a json string.

    :param ratings: A list of dictionaries containing the keys used in a Rating() object
    :param x_data: A string of one key from a Rating() object
    :param y_data: A string of one key from a Rating() object
    :return: A list of dictionaries of integers with x and y keys, converted into a json string
    """
    all_scores = [[], [], [], [], [], []]
    data = []
    if ratings:
        for rating in ratings:
            all_scores[0].append(rating["pacing"])
            all_scores[1].append(rating["tone"])
            all_scores[2].append(rating["energy"])
            all_scores[3].append(rating["fantasy"])
            all_scores[4].append(rating["abstraction"])
            all_scores[5].append(rating["propriety"])

    x = find_rating_type(x_data)
    x = all_scores[x]
    y = find_rating_type(y_data)
    y = all_scores[y]

    for idx, value in enumerate(x):
        point = {
            "x": value,
            "y": y[idx]
        }
        # Allows for Null ratings
        if type(point["x"]) == int and type(point["y"]) == int:
            data.append(point)

    data = json.dumps(data)

    return data


def find_rating_type(rating_type: str) -> int:
    """
    Uses a string to find the correct index for a list.

    Assuming a list of lists, each internal list corresponding to one of the keys from a Rating() object, this will
    take a key and convert it into an integer for indexing.

    - 0 = pacing
    - 1 = tone
    - 2 = energy
    - 3 = fantasy
    - 4 = abstraction
    - 5 = propriety

    :param rating_type: One of the keys from a Rating() object
    :return: The index for a list of lists
    """
    if rating_type == "pacing":
        rating_type = 0
    elif rating_type == "tone":
        rating_type = 1
    elif rating_type == "energy":
        rating_type = 2
    elif rating_type == "fantasy":
        rating_type = 3
    elif rating_type == "abstraction":
        rating_type = 4
    else:  # rating_type == "propriety"
        rating_type = 5

    return rating_type


def dictify_ratings_list(ratings: list) -> list:
    """
    Turns a list of Rating() objects into a list of dictionaries.

    :param ratings: A list of Rating() objects
    :return: A list of rating dictionaries
    """
    dict_ratings = []
    for rating in ratings:
        dict_ratings.append(rating.dictify())

    return dict_ratings


def request_show_data(anilist_id: int) -> dict:
    """
    Sends a GraphQL request to AniList for information on a given show and returns a dictionary of the
    collected data.

    The dictionary returned contains the following keys:

    - title, dict
        - romaji, string
        - english, string
        - native, string
    - genres, list of strings
    - tags, dict
        - name, string
        - rank, int
        - isMediaSpoiler, bool
    - averageScore, int
    - externalLinks, dict
        - site, string
    - format, string
    - status, string
    - description, string
    - episodes, int
    - relations, dict
        - edges, list of dicts
            - relationType, dict
            - node, dict
                - id, int
                - type, string
    - coverImage, dict
        - medium, string
        - large, string
        - extraLarge, string

    :param anilist_id: The ID for a given show in the AniList database

    :returns: Nested data about the show
    """

    id_var = {"id": anilist_id}
    # This requires an internet connection. If this bit breaks while testing locally, check your connection first.
    try:
        gql_request = rq.post(QUERY_URL, json={"query": QUERY, "variables": id_var}).json()['data']["Media"]
    except TypeError:
        print("Timeout- sleeping")
        time.sleep(65)
        print("Waking up")
        gql_request = rq.post(QUERY_URL, json={"query": QUERY, "variables": id_var}).json()['data']["Media"]

    return gql_request


# def process_show_data(main_shows: list) -> dict:
#     sorted_data = {
#         "availability": {
#             "crunchyroll": 0,
#             "funimation": 0,
#             "hidive": 0,
#             "vrv": 0,
#             "hulu": 0,
#             "amazon": 0,
#             "youtube": 0,
#             "prison": 0,
#             "hbo": 0,
#             "tubi": 0,
#         },
#         "genres": [],
#         "tags": {},
#     }
#     tags_list = []
#     for show in main_shows:
#         # TODO: Split into three functions for availability, tags, and genres. Move request_show_data() up a level.
#         gql_request = request_show_data(show.anilist_id)
#         show_availability = check_stream_locations(gql_request["externalLinks"])
#         for service in show_availability.items():
#             sorted_data["availability"][service[0]] += service[1]
#
#         if show.priority == 1:
#             for genre in gql_request["genres"]:
#                 if genre not in sorted_data["genres"]:
#                     sorted_data["genres"].append(genre)
#
#             for tag in gql_request["tags"]:
#                 try:
#                     if sorted_data["tags"][tag["name"]]:
#                         pass
#                 except KeyError:
#                     sorted_data["tags"][tag["name"]] = {}
#                     sorted_data["tags"][tag["name"]]["name"] = tag["name"]
#                     sorted_data["tags"][tag["name"]]["ranksList"] = []
#                     sorted_data["tags"][tag["name"]]["isMediaSpoiler"] = False
#
#                 sorted_data["tags"][tag["name"]]["ranksList"].append(tag["rank"])
#                 if tag["isMediaSpoiler"]:
#                     sorted_data["tags"][tag["name"]]["isMediaSpoiler"] = True
#
#     for tag in sorted_data["tags"].items():
#         tag[1]["rank"] = get_average(tag[1]["ranksList"], length=len(main_shows))
#         tags_list.append(tag[1])
#
#     sorted_data["tags"] = tags_list
#
#     return sorted_data


def process_genres(show_genres, collected_genres=None):
    """

    :param show_genres: gql_request["genres"]
    :param collected_genres:
    :return:
    """
    if not collected_genres:
        collected_genres = []

    for genre in show_genres:
        if genre not in collected_genres:
            collected_genres.append(genre)

    return collected_genres


def process_tags(show_tags, collected_tags=None):
    if not collected_tags:
        collected_tags = {}
    for tag in show_tags:
        try:
            if collected_tags[tag["name"]]:
                pass
        except KeyError:
            collected_tags[tag["name"]] = {}
            collected_tags[tag["name"]]["name"] = tag["name"]
            collected_tags[tag["name"]]["ranksList"] = []
            collected_tags[tag["name"]]["isMediaSpoiler"] = False

        collected_tags[tag["name"]]["ranksList"].append(tag["rank"])
        if tag["isMediaSpoiler"]:
            collected_tags[tag["name"]]["isMediaSpoiler"] = True

    return collected_tags


def count_series_episodes(shows_list):
    episode_count = 0
    for show in shows_list:
        episode_count += show.episodes if show.episodes else 0

    return episode_count


def check_stream_locations(streaming_links: list[dict]) -> dict:
    """
    Given a list of dictionaries, {"site": "string"}, this function will check for a specific set of sites
    and return a dictionary with 1 or 0 for each streaming service.

    :param streaming_links: A list of dictionaries containing the key "site" and a string with the name of the
        streaming service

    :returns: A dictionary with streaming services as keys and 1 or 0 as items
    """
    checked = []
    availability = {
        "crunchyroll": 0,
        "funimation": 0,
        "prison": 0,
        "amazon": 0,
        "vrv": 0,
        "hulu": 0,
        "youtube": 0,
        "tubi": 0,
        "hbo": 0,
        "hidive": 0,
    }
    for link in streaming_links:
        if link["site"] == "Crunchyroll" and "crunchyroll" not in checked:
            checked.append("crunchyroll")
            availability["crunchyroll"] = 1

        elif link["site"] == "Funimation" and "funimation" not in checked:
            checked.append("funimation")
            availability["funimation"] = 1

        elif link["site"] == "Netflix" and "prison" not in checked:
            checked.append("prison")
            availability["prison"] = 1

        elif link["site"] == "Amazon" and "amazon" not in checked:
            checked.append("amazon")
            availability["amazon"] = 1

        elif link["site"] == "VRV" and "vrv" not in checked:
            checked.append("vrv")
            availability["vrv"] = 1

        elif link["site"] == "Hulu" and "hulu" not in checked:
            checked.append("hulu")
            availability["hulu"] = 1

        elif link["site"] == "Youtube" and "youtube" not in checked:
            checked.append("youtube")
            availability["youtube"] = 1

        elif link["site"] == "Tubi TV" and "tubi" not in checked:
            checked.append("tubi")
            availability["tubi"] = 1

        elif link["site"] == "HBO Max" and "hbo" not in checked:
            checked.append("hbo")
            availability["hbo"] = 1

        elif link["site"] == "Hidive" and "hidive" not in checked:
            checked.append("hidive")
            availability["hidive"] = 1

    return availability


def get_average(numbers: list, length: int = None, allow_null: bool = False) -> int:
    """
    Returns the "round half up" average of the integers in a list.
    Null or other non-int list items are filtered out before averaging.

    :param numbers: A list containing the integers to be averaged
    :param length: A set number to divide the sum by instead of the number of integers given
    :param allow_null: A list with no integers will return an average of None instead of 0.
    :return: The average of the integers in the given list. A list with no integers will return 0 by default.
    """
    average = 0
    filtered_numbers = []

    # Filters out Null ratings
    for item in numbers:
        if type(item) == int:
            filtered_numbers.append(item)

    if not length:
        length = len(filtered_numbers)

    if len(filtered_numbers):
        dc.getcontext().rounding = dc.ROUND_HALF_UP
        average = sum(filtered_numbers) / length
        average = int(dc.Decimal(str(average)).quantize(dc.Decimal("1")))
    elif allow_null:
        average = None

    return average


def int_filter(x: any) -> bool:
    """
    Checks if a given parameter is an integer.
    """
    if type(x) == int:
        return True
    else:
        return False


def average_ratings(ratings_set: dict) -> dict:
    """
    Receives a dictionary of lists and returns a dictionary of integers.

    :param ratings_set: A dictionary with lists of ratings to be averaged
    :return: A dictionary with the average of each given list, or 0 if the list contained no ratings
    """
    average_ratings_set = {
        "score": get_average(ratings_set["score"]),
        "pacing": get_average(ratings_set["pacing"]),
        "energy": get_average(ratings_set["energy"]),
        "tone": get_average(ratings_set["tone"]),
        "fantasy": get_average(ratings_set["fantasy"]),
        "abstraction": get_average(ratings_set["abstraction"]),
        "propriety": get_average(ratings_set["propriety"])
    }

    return average_ratings_set


def avg_series_score(series_id):
    pass


def sort_series_relations(relations_list: list) -> dict:
    """
    Sorts the IDs of a set of shows into lists based on their relation to another show.

    -----

    The list given must contain dictionaries with the keys `relationType` and `node`. The `node` key must further
    contain a dictionary with the keys `type` and `id`.
    An appropriate list can be recieved from `request_show_data()["relations"]["edges"]`.

    :param relations_list: A list of dictionaries containing appropriate keys
    :return: A dictionary containing lists of show ID numbers, sorted by their relation to another show
    """
    sorted_relations = {
        "sequels": [],
        "side_stories": [],
        "related_series": [],
        "minor_relations": []
    }

    for relation in relations_list:
        if relation["node"]["type"] == "ANIME":

            if relation["relationType"] == "SEQUEL":
                sorted_relations["sequels"].append(relation["node"]["id"])

            elif relation["relationType"] == "SIDE_STORY":
                sorted_relations["side_stories"].append(relation["node"]["id"])

            elif relation["relationType"] in ("SPIN_OFF", "ALTERNATIVE"):
                sorted_relations["related_series"].append(relation["node"]["id"])

            elif relation["relationType"] not in ("PREQUEL", "PARENT", "CHARACTER"):
                sorted_relations["minor_relations"].append(relation["node"]["id"])

    return sorted_relations


def intify_dict_values(item: dict) -> dict:
    """
    Converts the values in a dictionary into ints. Values should be convertable to int.

    :param item: A dictionary of int-able values
    :return: A dictionary with contents converted to int
    """
    for key in item:
        # TODO: Account for Null entries
        item[key] = int(item[key])

    return item
