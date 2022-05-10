import json
import requests as rq
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
    format,
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


def assign_data(ratings, x_data, y_data):
    pacing_scores = [rating.pacing for rating in ratings]
    tone_scores = [rating.drama for rating in ratings]
    energy_scores = [rating.energy for rating in ratings]
    fantasy_scores = [rating.fantasy for rating in ratings]
    abstraction_scores = [rating.abstraction for rating in ratings]
    propriety_scores = [rating.propriety for rating in ratings]
    data = []

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


def add_to_series(anilist_id: int, position: int = 1, main: int = 1, series_id: int = None, checked_shows: list = None):
    if not checked_shows:
        checked_shows = []
    sequels = []
    side_stories = []
    minor_relations = []
    related_series = []

    relations = add_show(anilist_id, position, checked_shows, main=main, series_id=series_id)
    checked_shows.append(anilist_id)

    if series_id:
        series = Series.query.filter_by(id=series_id).first()
    else:
        show = Show.query.filter_by(anilist_id=anilist_id).first()
        series = Series.query.filter_by(entry_point_id=show.id).first()

    if not series:
        show = Show.query.filter_by(anilist_id=anilist_id).first()
        print(f"+series for {show.rj_name}")
        series = Series(en_name=show.en_name, jp_name=show.jp_name, rj_name=show.rj_name, entry_point_id=show.id)
        db.session.add(series)
        db.session.commit()
        show.series_id = series.id
        show.series_entry_id = series.id

        db.session.commit()

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

    print(f"{series.id} - {series.rj_name}")
    for show_id in sequels:
        if show_id not in checked_shows:
            checked_shows = add_to_series(show_id, position=position+1, main=main, series_id=series.id, checked_shows=checked_shows)
    for show_id in side_stories:
        if show_id not in checked_shows:
            checked_shows = add_to_series(show_id, position=position, main=2, series_id=series.id, checked_shows=checked_shows)
    for show_id in minor_relations:
        if show_id not in checked_shows:
            checked_shows = add_to_series(show_id, position=position, main=3, series_id=series.id, checked_shows=checked_shows)
    for show_id in related_series:
        if show_id not in checked_shows:
            checked_shows = add_to_series(show_id, checked_shows=checked_shows)

    return checked_shows


def add_show(anilist_id: int, position: int, checked_shows: list, main: int = 1, series_id: int = None) -> list:
    if anilist_id not in checked_shows:
        id_var = {"id": anilist_id}
        try:
            GQL_request = rq.post(url, json={"query": query, "variables": id_var}).json()['data']["Media"]
        except TypeError:
            print("Timeout- sleeping")
            time.sleep(65)
            print("Waking up")
            GQL_request = rq.post(url, json={"query": query, "variables": id_var}).json()['data']["Media"]

        show = Show.query.filter_by(anilist_id=anilist_id).first()

        if not show:
            print(f"+show {GQL_request['title']['romaji']}, Anilist ID: {anilist_id}")
            show = Show(
                en_name=GQL_request["title"]["english"],
                jp_name=GQL_request["title"]["native"],
                rj_name=GQL_request["title"]["romaji"],
                anilist_id=anilist_id,
                position=position,
                priority=main,
                type=GQL_request["format"],
                episodes=GQL_request["episodes"],
                cover_image=GQL_request["coverImage"]["large"],
                description=GQL_request["description"],
            )

            db.session.add(show)

        else:
            print(f"Updating show {show.rj_name}, Anilist ID: {show.anilist_id}")
            show.en_name = GQL_request["title"]["english"]
            show.jp_name = GQL_request["title"]["native"]
            show.rj_name = GQL_request["title"]["romaji"]
            show.position = position
            show.priority = main
            show.type = GQL_request["format"]
            show.episodes = GQL_request["episodes"]
            show.cover_image = GQL_request["coverImage"]["large"]
            show.description = GQL_request["description"]

        if series_id:
            series = Series.query.filter_by(id=series_id).first()
            show.series_id = series.id

        db.session.commit()

        return GQL_request["relations"]["edges"]

    else:
        # Needed for when it iterates over the list later
        return []


def collect_seasonal_data(show_id, seasonal_data):
    id_var = {"id": show_id}
    season_query = """query($id: Int){
                 Media(id: $id, type:ANIME){
                   format,
                   relations{
                     edges{
                       relationType,
                       node{
                         id,
                         episodes,
                         format,
                         status,
                         },
                       }
                     }
                   externalLinks {
                     site
                   },
                 }
               }"""
    show_data = rq.post(url, json={"query": season_query, "variables": id_var}).json()["data"]["Media"]

    seasonal_data = sort_seasonal_data(show_data, seasonal_data)

    for id_no in seasonal_data["sequel"]:
        seasonal_data = collect_seasonal_data(id_no, seasonal_data)
    return seasonal_data


def sort_seasonal_data(data_tree, seasonal_data):
    check_stream_locations(data_tree, seasonal_data["streaming"])
    seasonal_data["sequel"] = []
    for series in data_tree["relations"]["edges"]:
        if series["relationType"] == "SEQUEL":
            if series["node"]["format"] in ("TV", "TV_SHORT"):
                if series["node"]["status"] == "FINISHED":
                    seasonal_data["total_episodes"] += series["node"]["episodes"]
                    seasonal_data["seasons"] += 1
                else:
                    seasonal_data["unaired_seasons"] += 1
            elif series["node"]["format"] == "MOVIE":
                seasonal_data["movies"] += 1
            seasonal_data["sequel"].append(series["node"]["id"])

    return seasonal_data


def check_stream_locations(data_tree, stream_list):
    checked = []
    for value in data_tree["externalLinks"]:
        if value["site"] == "Crunchyroll" and "crunchyroll" not in checked:
            checked.append("crunchyroll")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["crunchyroll"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["crunchyroll"]["movies"] += 1
        elif value["site"] == "Funimation" and "funimation" not in checked:
            checked.append("funimation")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["funimation"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["funimation"]["movies"] += 1
        elif value["site"] == "Netflix" and "prison" not in checked:
            checked.append("prison")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["prison"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["prison"]["movies"] += 1
        elif value["site"] == "Amazon" and "amazon" not in checked:
            checked.append("amazon")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["amazon"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["amazon"]["movies"] += 1
        elif value["site"] == "VRV" and "vrv" not in checked:
            checked.append("vrv")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["vrv"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["vrv"]["movies"] += 1
        elif value["site"] == "Hulu" and "hulu" not in checked:
            checked.append("hulu")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["hulu"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["hulu"]["movies"] += 1
        elif value["site"] == "Youtube" and "youtube" not in checked:
            checked.append("youtube")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["youtube"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["youtube"]["movies"] += 1
        elif value["site"] == "Tubi TV" and "tubi" not in checked:
            checked.append("tubi")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["tubi"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["tubi"]["movies"] += 1
        elif value["site"] == "HBO Max" and "hbo" not in checked:
            checked.append("hbo")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["hbo"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["hbo"]["movies"] += 1
        elif value["site"] == "Hidive" and "hidive" not in checked:
            checked.append("hidive")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["hidive"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["hidive"]["movies"] += 1
