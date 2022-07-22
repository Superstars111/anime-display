from project.models import Show, Series, User, Feedback, Rating, List
from flask_login import current_user
from . import db
from project.standalone_functions import request_show_data, sort_series_relations, \
    intify_dict_values, process_tags, check_stream_locations, get_average


# Admin Functions


# Auth Functions


# Community Functions


def collect_feedback() -> list:
    """
    Collects and returns a list of all feedback entries.

    Each row in the feedback table is taken, converted into a dictionary, and appended to a list for iteration.
    :return: List of dictionaries with keys: id, user, type, status, description, note
    """
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
    """
    Updates the status column for a given feedback entry.

    :param feedback_id: The ID number for the feedback database entry
    :param new_status: 1 for New Feedback, 2 for Planned, 3 for In Progress, 4 for Closed
    """
    feedback = Feedback.query.filter_by(id=feedback_id).first()
    feedback.status = new_status
    db.session.commit()


def update_feedback_note(feedback_id: int, note: str):
    """
    Adds a developer note to a given feedback entry. This will overwrite any existing note.

    :param feedback_id: The ID number for the feedback database entry
    :param note: The developer note to be added
    """
    feedback = Feedback.query.filter_by(id=feedback_id).first()
    feedback.note = note
    db.session.commit()


# Content Functions


def seasonal_anilist_data(series_id: int) -> dict:
    """
    Collects variable AniList data for an entire series.

    A request is sent to the AniList API for every show (with a priority of 1 or 2) in a given series. The variable
    data (tags, genres, and availability) is collected for priority 1 shows, and only availability is collected for
    priority 2 shows. This data is then collected into a dictionary to represent the series as a whole.

    :param series_id: The ID number for the series to collect data on
    :return: dict with keys: mainTags, mainGenres, mainAvailability, sideAvailability
    """
    series = Series.query.get(series_id)
    sorted_shows = series.sort_shows()
    seasonal_data = {
        "mainTags": {},
        "mainGenres": set(),
        "mainAvailability": {
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
        "sideAvailability": {
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
        }
    }
    tags_list = []

    for show in series.shows:
        if show.priority in (1, 2):
            # Requests to the AniList API should be kept to a minimum, so this should stay as one function.
            gql_request = request_show_data(show.anilist_id)

            # Availability
            show_availability = check_stream_locations(gql_request["externalLinks"])
            for service in show_availability.items():
                seasonal_data["mainAvailability" if show.priority == 1 else "sideAvailability"][service[0]] += service[1]

            # Genres
            if show.priority == 1:
                seasonal_data["mainGenres"] = seasonal_data["mainGenres"].union(gql_request["genres"])
            # Tags
                seasonal_data["mainTags"] = process_tags(gql_request["tags"], collected_tags=seasonal_data["mainTags"])

    for tag in seasonal_data["mainTags"].items():
        tag[1]["rank"] = get_average(tag[1]["ranksList"], length=len(sorted_shows["main_shows"]))
        tags_list.append(tag[1])

    seasonal_data["mainTags"] = tags_list

    return seasonal_data


def update_user_show_rating(show_id: int, old_rating: object, new_rating: dict):
    """
    Updates the current user's rating entry for a given show.

    The new rating data will overwrite the old data, even if the new data is 0 or Null.
    If the old_rating parameter does not exist, a new rating will be created. A query should always be submitted for an
    old rating and the result submitted as old_rating, even if the query results in None. Failure to do so may result
    in duplicate ratings for a show. The dictionary submitted to new_rating must contain the same keys as would be
    returned by the Rating() object.

    :param show_id: The local database ID for the show to rate
    :param old_rating: A Rating() object from the database
    :param new_rating: Updated values for the rating object
    """
    new_rating = intify_dict_values(new_rating)
    if not old_rating:
        rating = Rating(show_id=show_id, user_id=current_user.id)
        rating.update(new_rating)
        db.session.add(rating)

    else:
        old_rating.update(new_rating)

    db.session.commit()


def add_show_to_list(list_id: int, show: object):
    """
    Adds a show to a user's custom list.

    :param list_id: The ID for the database entry of the list to update
    :param show: The Show() object to be added to the list
    """
    selected_list = List.query.filter_by(id=list_id).first()
    selected_list.shows += [show]
    db.session.commit()


def update_user_series_rating(new_rating: dict, series_id: int):
    """
    Updates the current user's rating for every seen show within a series.

    For every show in the selected series, this function checks whether the show is in the current user's list named
    "Seen," which is generated by default upon registration. If the show is found in the list, the current user's
    rating for the show is pulled (or created if it doesn't exist) and updated with the new values. The old ratings
    will be overwritten, even if the new values consist of 0 or Null. The dictionary submitted should contain the same
    keys as would be returned by a Rating() object.

    :param new_rating: The set of new values to be applied to the Rating() objects
    :param series_id: The ID number for the series database entry to be checked
    """
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


def sort_series_names(sort_style: str):
    """
    Sorts every series in the database by a given method.

    The database is queried for all series entries, which are then sorted by title according to a given sort method.
    The series' may be sorted alphabetically, by average score of the main shows in the series, or by average score of
    all the shows in the series. Any invalid string submitted as sort_style will result in the series being returned
    without being sorted. Two lists will be returned, the first of series names, and the second of series IDs. The
    lists should be the same length, and a given index for one will match to the same series in the other.

    :param sort_style: alpha, total-avg-score, or main-avg-score
    :return: A list of series names, and a list of series IDs, both sorted in the same manner
    """
    all_series = db.session.query(Series).all()

    if sort_style == "alpha":
        if current_user.names_preference in (1, 2):  # Japanese, Romaji
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

    # TODO: Make it return a list of tuples instead of two lists, to better avoid mix-ups
    return series_names, series_ids


# General Functions


# Other Functions


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


def create_show_entry(anilist_id: int, new_data: dict) -> object:
    """
    Creates a new database entry for a show based on data from AniList

    :param anilist_id: The ID number of a show in AniList's database
    :param new_data: A collection of data about a show, received from `request_show_data()`
    :returns: The created database entry in object form
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
    """
    Updates the names for a series in the database.

    If the series_id parameter is left blank, the series will check for a series anyway based on the AniList ID of the
    first season. If no series is found, a new one will be created with the associated show as the entry point. The
    show in question will be updated to reflect this.

    :param initial_anilist_id: The ID for AniList's database entry for the first season of the series.
    :param series_id: The local database ID for the series to be updated. (Default is None)
    :return: The local ID number for the series which was updated or created.
    """
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


# Multi-use Functions


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
