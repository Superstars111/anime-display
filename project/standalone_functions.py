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


# Admin Functions


# Auth Functions


# Community Functions


# Content Functions


def count_series_episodes(shows_list: list[object]) -> int:
    """
    Counts the episodes in a list of Show() objects.

    :param shows_list: A list of Show() objects
    :return: The total amount of episodes in the shows given
    """
    episode_count = 0
    for show in shows_list:
        episode_count += show.episodes if show.episodes else 0

    return episode_count


def collect_title(show: object) -> str:
    """
    Generates a single string with all non-null titles of a Show() object.

    :param show: A Show() object
    :return: jp_name * en_name * rj_name
    """
    titles = []
    for title in (show.jp_name, show.en_name, show.rj_name):
        # Check to ensure title is not "None" before appending
        if title and title not in titles:
            titles.append(title)
    return f" \u2022 ".join(titles)


def collect_avg_user_score(rating_list: list[dict], field: str):
    """
    Collects the score value from a list of Rating() objects and determines the average.

    :param rating_list: A list of Rating() objects
    :param field: A string to be used as a dict key. Should be compatible with a Rating() dict.
    :return: The average rating of the given field across the dictionaries. Returns "N/A" if the average is 0.
    """
    all_ratings = []
    for rating in rating_list:
        all_ratings.append(rating[field])

    avg_user_score = get_average(all_ratings)

    if avg_user_score == 0:
        avg_user_score = "N/A"

    return avg_user_score


def collect_streaming_colors(availability: dict[str, int], series_length: int = 1) -> dict[str, tuple[str, str]]:
    """
    Determines the colors to use for display of streaming services based on availability of a show or series.

    A dictionary is passed in containing a list of streaming services and an integer indicating how much of a given
    series is available to stream on that platform. For a single show, that number will always be 1 or 0. A new
    dictionary is formed with the streaming service and the appropriate color based on how much is available there. The
    series_length parameter indicates which number should be considered "100%" for a given series. For a single show,
    leave this parameter at the default value.

    - 100% availability = brand color, black
    - Partial availability = black, black
    - No availability = gray, gray

    :param availability: A dict of streaming services with how many shows they have available in a series
    :param series_length: The value to be measured against for 100%
    :return: A dict of streaming services with colors based on what percentage of a series they have
    """
    colors = {}
    for service in availability.items():
        if service[1] == series_length:  # Show or series is fully available on that platform
            # All colors must work in CSS.
            if service[0] == "crunchyroll":
                color = "#FF8C00"  # CSS DarkOrange
            elif service[0] == "funimation":
                color = "#4B0082"  # CSS Indigo
            elif service[0] == "hbo":
                color = "#6495ED"  # CSS CornflowerBlue
            elif service[0] == "hidive":
                color = "#1E90FF"  # CSS DodgerBlue
            elif service[0] == "amazon":
                color = "#00BFFF"  # CSS DeepSkyBlue
            elif service[0] == "vrv":
                color = "#FFD700"  # CSS Gold
            elif service[0] == "hulu":
                color = "#9ACD32"  # CSS YellowGreen
            elif service[0] == "youtube":
                color = "#FF0000"  # CSS Red
            elif service[0] == "prison":
                color = "#B22222"  # CSS FireBrick
            elif service[0] == "tubi":
                color = "#FFA500"  # CSS Orange
            else:
                color = "#000000"  # CSS Black
            colors[service[0]] = (color, "#000000")

        elif service[1]:  # Show or series is partially available on that platform
            colors[service[0]] = ("#000000", "#000000")  # CSS Black

        else:  # Show or series is not available on that platform
            colors[service[0]] = ("#808080", "#808080")  # CSS Gray

    return colors


def collect_genres(genres_list: list[str]) -> str:
    """
    Generates a string joined by commas from a list.

    :param genres_list: The genres to be joined
    :return: A string formed from the list of genres
    """
    genres = ", ".join(sorted(genres_list))
    return genres


def collect_tags(raw_tags: list[dict]):
    """
    Sorts a list of tags by rank and spoiler status, and returns them as strings.

    The list passed as raw_tags will first be sorted by item["rank"]. Tags are then converted into individual strings
    including name and rank, and are then sorted into one of two lists based on spoiler status. Finally, these two
    lists are converted into strings, which are returned.

    :param raw_tags: A list of tags in dict form. Should contain keys "name" "rank" and "isMediaSpoiler".
    :return: Two strings- one of regular tags and one of spoiler tags, both sorted by rank
    """
    raw_tags.sort(key=lambda x: x["rank"], reverse=True)
    tags = []
    spoilers = []
    for tag in raw_tags:
        s = f"{tag['name']} ({tag['rank']}%)"
        if tag['isMediaSpoiler']:
            spoilers.append(s)
        else:
            tags.append(s)

    tags = ", ".join(tags)
    spoilers = ", ".join(spoilers)
    return tags, spoilers


# General Functions


# Other Functions


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


def process_tags(show_tags: list[dict], collected_tags: dict[str, dict] = None) -> dict[str, dict]:
    """
    Collects a group of tags with a list of ranks instead of just one.

    Creates a new dictionary if collected_tags is left blank. Each tag in show_tags is checked to see whether it
    already exists in collected_tags. If not, it is added. If it does, then the rank is appended to ranksList. This is
    intended to be used in a loop, passing the result back into itself with each new list of tags.

    :param show_tags: A list of tags to be checked and added to collected_tags
    :param collected_tags: A dictionary of previously collected tags
    :return: A dictionary of all tags, with ranks appended into a list
    """
    if not collected_tags:
        # Dict instead of list, so we can check by name whether a tag is already here.
        collected_tags = {}
    for tag in show_tags:
        if tag["name"] not in collected_tags.keys():
            collected_tags[tag["name"]] = {}
            collected_tags[tag["name"]]["name"] = tag["name"]
            collected_tags[tag["name"]]["ranksList"] = []
            collected_tags[tag["name"]]["isMediaSpoiler"] = False

        collected_tags[tag["name"]]["ranksList"].append(tag["rank"])
        if tag["isMediaSpoiler"]:
            collected_tags[tag["name"]]["isMediaSpoiler"] = True

    return collected_tags


def int_filter(x: any) -> bool:
    """
    Checks if a given parameter is an integer.
    """
    if type(x) == int:
        return True
    else:
        return False


def sort_series_relations(relations_list: list[dict]) -> dict[str, list[int]]:
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


def collect_colors(scores: list[int]) -> list[str]:
    """
    Turns a list of ints into a list of colors.

    - 0 = black
    - 1-54 = red
    - 55-69 = orange
    - 70-84 = blue
    - 85+ = purple

    :param scores: A list of scores
    :return: A list of colors corresponding to the scores passed in
    """
    colors = []
    for score in scores:
        if score >= 85:
            colors.append("purple")
        elif score >= 70:
            colors.append("blue")
        elif score >= 55:
            colors.append("orange")
        elif score >= 1:
            colors.append("red")
        else:
            colors.append("black")
    return colors


# Multi-use Functions


def graph_data_selection(ratings: list[dict], x_data: str, y_data: str) -> list[dict[str, int]]:
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


def dictify_ratings_list(ratings: list[object]) -> list[dict]:
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


def check_stream_locations(streaming_links: list[dict]) -> dict[str, int]:
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


def average_ratings(ratings_set: dict[str, list[int]], rating_type: str = None) -> dict[str, int]:
    """
    Returns the average of a collection of ratings.

    :param ratings_set: A dictionary with lists of ratings to be averaged
    :param rating_type: Gather only a single rating average. Should be a string from a Rating() object.
    :return: A dictionary with the average of each given list, or 0 if the list contained no ratings
    """
    if rating_type:
        ratings_average = get_average(ratings_set[rating_type])
    else:
        ratings_average = {
            "score": get_average(ratings_set["score"]),
            "pacing": get_average(ratings_set["pacing"]),
            "energy": get_average(ratings_set["energy"]),
            "tone": get_average(ratings_set["tone"]),
            "fantasy": get_average(ratings_set["fantasy"]),
            "abstraction": get_average(ratings_set["abstraction"]),
            "propriety": get_average(ratings_set["propriety"])
        }

    return ratings_average


def avg_series_score(series_id):
    pass
