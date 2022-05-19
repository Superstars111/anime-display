import json
import requests as rq
import decimal as dc
from project.models import Show, Series
from . import db
import time

url = "https://graphql.anilist.co/"

query = """query($id: Int){
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
      large
    }
  }
}"""

stream_info = {
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
            tone_scores.append(rating.drama)
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


def update_full_series(anilist_id: int, position: int = 1, main: int = 1, series_id: int = None, checked_shows: list = None) -> list:
    if not checked_shows:
        checked_shows = []
    sequels = []
    side_stories = []
    minor_relations = []
    related_series = []

    relations = add_show_to_series(anilist_id, position, checked_shows, main=main, series_id=series_id)
    checked_shows.append(anilist_id)

    series_id = update_series_entry(anilist_id)

    for relation in relations:
        if relation["node"]["type"] == "ANIME":

            if relation["relationType"] == "SEQUEL":
                sequels.append(relation["node"]["id"])

            elif relation["relationType"] == "SIDE_STORY":
                side_stories.append(relation["node"]["id"])

            elif relation["relationType"] in ("SPIN_OFF", "ALTERNATIVE"):
                related_series.append(relation["node"]["id"])

            elif relation["relationType"] not in ("PREQUEL", "PARENT", "CHARACTER"):
                minor_relations.append(relation["node"]["id"])

    for show_id in sequels:
        if show_id not in checked_shows:
            checked_shows = update_full_series(show_id, position=position + 1, main=main, series_id=series_id, checked_shows=checked_shows)

    for show_id in side_stories:
        if show_id not in checked_shows:
            checked_shows = update_full_series(show_id, position=position, main=2, series_id=series_id, checked_shows=checked_shows)

    for show_id in minor_relations:
        if show_id not in checked_shows:
            checked_shows = update_full_series(show_id, position=position, main=3, series_id=series_id, checked_shows=checked_shows)

    for show_id in related_series:
        if show_id not in checked_shows:
            checked_shows = update_full_series(show_id, checked_shows=checked_shows)

    return checked_shows


def add_show_to_series(anilist_id: int, position: int, checked_shows: list, main: int = 1, series_id: int = None) -> list:
    if anilist_id not in checked_shows:
        GQL_request = request_show_data(anilist_id)
        show = Show.query.filter_by(anilist_id=anilist_id).first()
        if not show:
            show = create_show_entry(anilist_id, GQL_request)
        else:
            show.update_entry(GQL_request)

        show.position = position
        show.priority = main

        if series_id:
            series = Series.query.filter_by(id=series_id).first()
            show.series_id = series.id

        # db.session.commit()

        # Return list of related shows
        return GQL_request["relations"]["edges"]

    else:
        # Needed for when it iterates over the list later
        return []


def request_show_data(anilist_id: int) -> dict:
    id_var = {"id": anilist_id}
    try:
        GQL_request = rq.post(url, json={"query": query, "variables": id_var}).json()['data']["Media"]
    except TypeError:
        print("Timeout- sleeping")
        time.sleep(65)
        print("Waking up")
        GQL_request = rq.post(url, json={"query": query, "variables": id_var}).json()['data']["Media"]

    return GQL_request


def update_show_entry(anilist_id: int, new_data: dict):
    show = Show.query.filter_by(anilist_id=anilist_id).first()

    if not show:
        print(f"+show {new_data['title']['romaji']}, Anilist ID: {anilist_id}")
        create_show_entry(anilist_id, new_data)

    else:
        print(f"Updating show {show.rj_name}, Anilist ID: {show.anilist_id}")


    db.session.commit()


def create_show_entry(anilist_id: int, new_data: dict):
    show = Show(
        en_name=new_data["title"]["english"],
        jp_name=new_data["title"]["native"],
        rj_name=new_data["title"]["romaji"],
        anilist_id=anilist_id,
        type=new_data["format"],
        status=new_data["status"],
        episodes=new_data["episodes"],
        cover_image=new_data["coverImage"]["large"],
        description=new_data["description"],
    )

    db.session.add(show)
    db.session.commit()

    return show


def update_series_entry(initial_anilist_id: int, series_id: int = None) -> int:
    if series_id:
        series = Series.query.filter_by(id=series_id).first()
    else:
        show = Show.query.filter_by(anilist_id=initial_anilist_id).first()
        series = Series.query.filter_by(entry_point_id=show.id).first()

    if not series:
        show = Show.query.filter_by(anilist_id=initial_anilist_id).first()
        print(f"+series for {show.rj_name}")
        series = Series(en_name=show.en_name, jp_name=show.jp_name, rj_name=show.rj_name, entry_point_id=show.id)
        db.session.add(series)
        db.session.commit()
        show.series_id = series.id
        show.series_entry_id = series.id

        db.session.commit()

    return series.id


def collect_seasonal_data(series_id: int) -> dict:
    series = Series.query.get(series_id)
    sorted_shows = series.sort_shows()
    seasonal_data = {
        "totalEpisodes": 0,
        "mainSeriesEpisodes": 0,
        "mainTags": {},
        "mainGenres": [],
        "mainAvailability": {},
        "sideAvailability": {}
    }

    for show in series.shows:
        seasonal_data["totalEpisodes"] += show.episodes if show.episodes else 0

        if show.priority == 1:
            seasonal_data["mainSeriesEpisodes"] += show.episodes if show.episodes else 0

    processed_data = process_show_data(sorted_shows["main_shows"])
    seasonal_data["mainAvailability"] = processed_data["availability"]
    seasonal_data["mainGenres"] = processed_data["genres"]
    seasonal_data["mainTags"] = processed_data["tags"]
    seasonal_data["sideAvailability"] = process_show_data(sorted_shows["side_shows"])["availability"]

    return seasonal_data


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


def get_average(numbers: list, length: int = None) -> int:
    average = 0
    if not length:
        length = len(numbers)
    if numbers:
        dc.getcontext().rounding = dc.ROUND_HALF_UP
        average = sum(filter(int_filter, numbers)) / length
        average = int(dc.Decimal(str(average)).quantize(dc.Decimal("1")))

    return average


def int_filter(x):
    if type(x) == int:
        return True
    else:
        return False
