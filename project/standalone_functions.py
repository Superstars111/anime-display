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
    """Sends a GraphQL request to AniList for information on a given show and returns a dictionary of the
    collected data. \n
    Contains: \n
    "title": {"romaji", "english", "native"},\n
    "genres": [],\n
    "tags": {"name", "rank", "isMediaSpoiler"},\n
    "averageScore": 0,\n
    "externalLinks": {"site"},\n
    "format": "",\n
    "status": "",\n
    "description": "",\n
    "episodes": 0,\n
    "relations": {"edges": {"relationType": {"node": {"id", "type"}}}},\n
    "coverImage": {"medium", "large", "extraLarge"}"""

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
    """Given a list of dictionaries, {"site": "string"}, this function will check for a specific set of sites
    and return a dictionary with True or False for each streaming service."""
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
    average = 0
    filtered_numbers = []
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


def int_filter(x):
    if type(x) == int:
        return True
    else:
        return False


def average_ratings(ratings_set: dict) -> dict:
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
