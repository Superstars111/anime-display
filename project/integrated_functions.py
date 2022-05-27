import json
import requests as rq
import decimal as dc
from project.models import Show, Series
from . import db
from project.standalone_functions import request_show_data, process_show_data
import time


def update_full_series(anilist_id: int, position: int = 1, main: int = 1, series_id: int = None, checked_shows: list = None) -> list:
    if not checked_shows:
        checked_shows = []
    sequels = []
    side_stories = []
    minor_relations = []
    related_series = []

    relations = add_show_to_series(anilist_id, position, checked_shows, main=main, series_id=series_id)
    checked_shows.append(anilist_id)

    if not series_id:
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

        db.session.commit()

        # Return list of related shows
        return GQL_request["relations"]["edges"]

    else:
        # Needed for when it iterates over the list later
        return []


def update_show_entry(anilist_id: int, new_data: dict):
    show = Show.query.filter_by(anilist_id=anilist_id).first()

    if not show:
        print(f"+show {new_data['title']['romaji']}, Anilist ID: {anilist_id}")
        create_show_entry(anilist_id, new_data)

    else:
        print(f"Updating show {show.rj_name}, Anilist ID: {show.anilist_id}")
        show.update_entry(new_data)

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
    show = Show.query.filter_by(anilist_id=initial_anilist_id).first()
    if series_id:
        series = Series.query.filter_by(id=series_id).first()
    else:
        print(show.jp_name)
        series = Series.query.filter_by(entry_point_id=show.id).first()

    if series:
        series_names = {
            "en_name": show.en_name,
            "jp_name": show.jp_name,
            "rj_name": show.rj_name
        }
        series.update_entry_names(series_names)

    else:
        print(f"+series for {show.rj_name}")
        series = Series(en_name=show.en_name, jp_name=show.jp_name, rj_name=show.rj_name, entry_point_id=show.id)
        db.session.add(series)
        # FIXME: sqlalchemy.exc.DatabaseError: (mysql.connector.errors.DatabaseError) 1364 (HY000):
        #  Field 'id' doesn't have a default value
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
