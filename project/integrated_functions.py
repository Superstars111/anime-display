from project.models import Show, Series, User, Feedback, Rating, List
from flask_login import current_user
from . import db
from project.standalone_functions import request_show_data, process_show_data, sort_series_relations


def update_full_series(anilist_id: int, position: int = 1, main: int = 1, series_id: int = None, checked_shows: list = None) -> list:
    """
    Uses recursion and other functions to update the show data of an entire series from a given entry point.


    :param anilist_id: The ID for the AniList database entry for the first show in the series. Exceptions made if
        using recursion within this function.
    :param position: The position of the show within the series- 1st season, 2nd season, etc.
    :param main: The priority level of this show in the series. 1 for the main series, 2 for side content like OVAs,
        and 3 for minor relations like promotional material and music videos.
    :param series_id: The ID number of the series within the local database.
    :param checked_shows: A list of AniList ID numbers of shows which have already been checked through recursion.
        Leave blank if not calling from within the function itself.
    :return: A list of updated AniList ID numbers that have been checked by the function.
    """
    if not checked_shows:
        checked_shows = []

    if anilist_id not in checked_shows:
        gql_request = request_show_data(anilist_id)
        relations = gql_request["relations"]["edges"]
        update_show_entry(anilist_id, gql_request)
        update_show_series_data(anilist_id, position, priority=main, series_id=series_id)
        checked_shows.append(anilist_id)
        sorted_relations = sort_series_relations(relations)
    else:
        sorted_relations = []

    if not series_id:
        series_id = update_series_entry(anilist_id)

    for show_id in sorted_relations["sequels"]:
        if show_id not in checked_shows:
            checked_shows = update_full_series(show_id, position=position + 1, main=main, series_id=series_id, checked_shows=checked_shows)

    for show_id in sorted_relations["side_stories"]:
        if show_id not in checked_shows:
            checked_shows = update_full_series(show_id, position=position, main=2, series_id=series_id, checked_shows=checked_shows)

    for show_id in sorted_relations["minor_relations"]:
        if show_id not in checked_shows:
            checked_shows = update_full_series(show_id, position=position, main=3, series_id=series_id, checked_shows=checked_shows)

    for show_id in sorted_relations["related_series"]:
        if show_id not in checked_shows:
            checked_shows = update_full_series(show_id, checked_shows=checked_shows)

    return checked_shows


def update_show_series_data(anilist_id: int, position: int, priority: int = 1, series_id: int = None):
    """
    Updates a show's series data to be current and accurate. If a series does not currently exist, a new one can be
    created with `update_series_entry()`.

    :param anilist_id: The AniList ID number for the show to be updated
    :param position: The position of the show within the series- e.g., season 1, 2, etc.
    :param priority: 1 if the show is part of the main series, 2 for side content like OVAs, 3 for minor content such
        as promotional material or music videos
    :param series_id: The local ID number of the associated series for the show, if any
    """

    show = Show.query.filter_by(anilist_id=anilist_id).first()

    show.position = position
    show.priority = priority

    if series_id:
        series = Series.query.filter_by(id=series_id).first()
        show.series_id = series.id

    db.session.commit()


def update_show_entry(anilist_id: int, new_data: dict):
    """
    Updates a show's database entry or creates a new one based on a dictionary of data from AniList.

    :param anilist_id: The ID number of a show in AniList's database
    :param new_data: A collection of data about a show, received from `request_show_data()`
    """
    show = Show.query.filter_by(anilist_id=anilist_id).first()

    if not show:
        print(f"Adding new show {new_data['title']['romaji']}, Anilist ID: {anilist_id}")
        create_show_entry(anilist_id, new_data)

    else:
        print(f"Updating show {show.rj_name}, Anilist ID: {show.anilist_id}")
        show.update_entry(new_data)

    db.session.commit()


def create_show_entry(anilist_id: int, new_data: dict):
    """
    Creates a new database entry for a show based on data from AniList

    :param anilist_id: The ID number of a show in AniList's database
    :param new_data: A collection of data about a show, received from `request_show_data()`
    """
    show = Show(
        en_name=new_data["title"]["english"],
        jp_name=new_data["title"]["native"],
        rj_name=new_data["title"]["romaji"],
        anilist_id=anilist_id,
        type=new_data["format"],
        status=new_data["status"],
        episodes=new_data["episodes"],
        cover_med=new_data["coverImage"]["medium"],
        cover_large=new_data["coverImage"]["large"],
        cover_xl=new_data["coverImage"]["extraLarge"],
        description=new_data["description"],
    )

    # FIXME: sqlalchemy.exc.DatabaseError: (mysql.connector.errors.DatabaseError) 1364 (HY000):
    #  Field 'id' doesn't have a default value
    # TODO: Check if error still exists- should be patched
    db.session.add(show)
    db.session.commit()

    return show


def update_series_entry(initial_anilist_id: int, series_id: int = None) -> int:
    show = Show.query.filter_by(anilist_id=initial_anilist_id).first()
    if series_id:
        series = Series.query.filter_by(id=series_id).first()
    else:
        print(f"Finding series for {show.rj_name}")
        series = Series.query.filter_by(entry_point_id=show.id).first()

    if series:
        print(f"Updating existing series")
        series_names = {
            "en_name": show.en_name,
            "jp_name": show.jp_name,
            "rj_name": show.rj_name
        }
        series.update_entry_names(series_names)

    else:
        print(f"Adding new series for {show.rj_name}")
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


def collect_feedback() -> list:
    feedback_list = []
    for feedback_item in db.session.query(Feedback).all():

        user = User.query.filter_by(id=feedback_item.user_id).first()

        if feedback_item.type == 1:
            feedback_type = "Bug Report"
        elif feedback_item.type == 2:
            feedback_type = "Feature Request"
        elif feedback_item.type == 3:
            feedback_type = "Data Request"
        else:
            feedback_type = "Other Feedback"

        if feedback_item.status == 1:
            feedback_status = "New Feedback"
        elif feedback_item.status == 2:
            feedback_status = "Planned"
        elif feedback_item.status == 3:
            feedback_status = "In Progress"
        else:
            feedback_status = "Closed"

        feedback_list.append({
            "id": feedback_item.id,
            "user": user.username,
            "type": feedback_type,
            "status": feedback_status,
            "description": feedback_item.description,
            "note": feedback_item.note
        })

    return feedback_list


def update_feedback_status(feedback_id: int, new_status: int):
    feedback = Feedback.query.filter_by(id=feedback_id).first()
    feedback.status = new_status
    db.session.commit()


def update_feedback_note(feedback_id: int, note: str):
    feedback = Feedback.query.filter_by(id=feedback_id).first()
    feedback.note = note
    db.session.commit()


def update_user_show_rating(show_id: int, old_rating: object, new_rating: dict):
    new_rating = intify_dict_values(new_rating)
    if not old_rating:
        rating = Rating(show_id=show_id, user_id=current_user.id)
        rating.update(new_rating)
        db.session.add(rating)

    else:
        old_rating.update(new_rating)

    db.session.commit()


def add_show_to_list(list_id: int, show: object):
    selected_list = List.query.filter_by(id=list_id).first()
    selected_list.shows += [show]
    db.session.commit()


def update_user_series_rating(new_rating: dict, series_id: int):
    current_seen_list = List.query.filter_by(owner_id=current_user.id, name="Seen").first()
    new_rating = intify_dict_values(new_rating)
    series = Series.query.filter_by(id=series_id).first()

    for show in series.shows:
        if show in current_seen_list.shows:
            user_rating = Rating.query.filter_by(user_id=current_user.id, show_id=show.id).first()
            if not user_rating:
                user_rating = Rating(user_id=current_user.id, show_id=show.id)
                db.session.add(user_rating)

            user_rating.update(new_rating)

        db.session.commit()


def intify_dict_values(item: dict) -> dict:
    for key in item:
        item[key] = int(item[key])

    return item


def sort_series_names(sort_style: str):
    all_series = db.session.query(Series).all()

    if sort_style == "alpha":
        if current_user.names_preference in (1, 2):
            sorted_series = sorted(all_series, key=lambda x: x.rj_name.lower())
        else:
            sorted_series = sorted(all_series, key=lambda x: x.en_name.lower() if x.en_name else x.rj_name.lower())
    elif sort_style == "total-avg-score":
        sorted_series = sorted(all_series, key=lambda x: x.average_ratings()["score"])
    elif sort_style == "main-avg-score":
        sorted_series = sorted(all_series, key=lambda x: x.average_ratings(only_main=True)["score"])
    else:
        sorted_series = all_series

    series_names = []
    for series in sorted_series:
        if current_user.names_preference == 1:
            series_names.append(series.jp_name)
        elif current_user.names_preference == 2:
            series_names.append(series.rj_name)
        else:
            if series.en_name:
                series_names.append(series.en_name)
            else:
                series_names.append(series.rj_name)
    series_ids = [series.id for series in sorted_series]

    return series_names, series_ids
