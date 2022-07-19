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


def assign_data(ratings: list, x_data: str, y_data: str):
    pacing_scores = []
    tone_scores = []
    energy_scores = []
    fantasy_scores = []
    abstraction_scores = []
    propriety_scores = []
    data = []
    if ratings:
        if type(ratings[0]) == dict:
            for rating in ratings:
                pacing_scores.append(rating["pacing"])
                tone_scores.append(rating["tone"])
                energy_scores.append(rating["energy"])
                fantasy_scores.append(rating["fantasy"])
                abstraction_scores.append(rating["abstraction"])
                propriety_scores.append(rating["propriety"])
        else:
            for rating in ratings:
                pacing_scores.append(rating.pacing)
                tone_scores.append(rating.tone)
                energy_scores.append(rating.energy)
                fantasy_scores.append(rating.fantasy)
                abstraction_scores.append(rating.abstraction)
                propriety_scores.append(rating.propriety)

    if x_data == "tone":
        x = tone_scores
    elif x_data == "energy":
        x = energy_scores
    elif x_data == "fantasy":
        x = fantasy_scores
    elif x_data == "abstraction":
        x = abstraction_scores
    elif x_data == "propriety":
        x = propriety_scores
    else:
        x = pacing_scores

    if y_data == "pacing":
        y = pacing_scores
    elif y_data == "energy":
        y = energy_scores
    elif y_data == "fantasy":
        y = fantasy_scores
    elif y_data == "abstraction":
        y = abstraction_scores
    elif y_data == "propriety":
        y = propriety_scores
    else:
        y = tone_scores

    for idx, rank in enumerate(x):
        point = {
            "x": rank,
            "y": y[idx]
        }
        if type(point["x"]) == int and type(point["y"]) == int:
            data.append(point)

    data = json.dumps(data)

    return data


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


def process_show_data(main_shows: list) -> dict:
    sorted_data = {
        "availability": {
            "crunchyroll": 0,
            "funimation": 0,
            "hidive": 0,
            "vrv": 0,
            "hulu": 0,
            "amazon": 0,
            "youtube": 0,
            "prison": 0,
            "hbo": 0,
            "tubi": 0,
        },
        "genres": [],
        "tags": {},
    }
    tags_list = []
    for show in main_shows:
        GQL_request = request_show_data(show.anilist_id)
        show_availability = check_stream_locations(GQL_request["externalLinks"])
        for service in show_availability.items():
            if service[1] is True:
                sorted_data["availability"][service[0]] += 1

        if show.priority == 1:
            for genre in GQL_request["genres"]:
                if genre not in sorted_data["genres"]:
                    sorted_data["genres"].append(genre)

            for tag in GQL_request["tags"]:
                try:
                    if sorted_data["tags"][tag["name"]]:
                        pass
                except KeyError:
                    sorted_data["tags"][tag["name"]] = {}
                    sorted_data["tags"][tag["name"]]["name"] = tag["name"]
                    sorted_data["tags"][tag["name"]]["ranksList"] = []
                    sorted_data["tags"][tag["name"]]["isMediaSpoiler"] = False

                sorted_data["tags"][tag["name"]]["ranksList"].append(tag["rank"])
                if tag["isMediaSpoiler"]:
                    sorted_data["tags"][tag["name"]]["isMediaSpoiler"] = True

    for tag in sorted_data["tags"].items():
        tag[1]["rank"] = get_average(tag[1]["ranksList"], length=len(main_shows))
        tags_list.append(tag[1])

    sorted_data["tags"] = tags_list

    return sorted_data


def check_stream_locations(streaming_links: list) -> dict:
    """
    Given a list of dictionaries, {"site": "string"}, this function will check for a specific set of sites
    and return a dictionary with True or False for each streaming service.

    :param streaming_links: A list of dictionaries containing the key "site" and a string with the name of the
        streaming service
    :type streaming_links: list

    :returns: A dictionary with streaming services as keys and True or False as items
    :rtype: dict
    """
    checked = []
    availability = {
        "crunchyroll": False,
        "funimation": False,
        "prison": False,
        "amazon": False,
        "vrv": False,
        "hulu": False,
        "youtube": False,
        "tubi": False,
        "hbo": False,
        "hidive": False,
    }
    for link in streaming_links:
        if link["site"] == "Crunchyroll" and "crunchyroll" not in checked:
            checked.append("crunchyroll")
            availability["crunchyroll"] = True

        elif link["site"] == "Funimation" and "funimation" not in checked:
            checked.append("funimation")
            availability["funimation"] = True

        elif link["site"] == "Netflix" and "prison" not in checked:
            checked.append("prison")
            availability["prison"] = True

        elif link["site"] == "Amazon" and "amazon" not in checked:
            checked.append("amazon")
            availability["amazon"] = True

        elif link["site"] == "VRV" and "vrv" not in checked:
            checked.append("vrv")
            availability["vrv"] = True

        elif link["site"] == "Hulu" and "hulu" not in checked:
            checked.append("hulu")
            availability["hulu"] = True

        elif link["site"] == "Youtube" and "youtube" not in checked:
            checked.append("youtube")
            availability["youtube"] = True

        elif link["site"] == "Tubi TV" and "tubi" not in checked:
            checked.append("tubi")
            availability["tubi"] = True

        elif link["site"] == "HBO Max" and "hbo" not in checked:
            checked.append("hbo")
            availability["hbo"] = True

        elif link["site"] == "Hidive" and "hidive" not in checked:
            checked.append("hidive")
            availability["hidive"] = True

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
