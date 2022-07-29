from flask import Blueprint, request, session, render_template, url_for, redirect, abort
from flask_login import current_user
from project.models import Show, Rating, Series
from project import db
import project.integrated_functions as intf
import project.standalone_functions as sf

TEMPLATE_PATH = "content/templates/content"

CONTENT_BLUEPRINT = Blueprint("content", __name__, template_folder="../../project")


@CONTENT_BLUEPRINT.route("/compare")
def compare():
    pass
    # show_id = request.args.get("options_list", "")
    # if "selected_shows" not in session:
    #     session["selected_shows"] = []
    #
    # if show_id:
    #     show = find_show(show_id)
    # else:
    #     show = {
    #         "romajiTitle": "",
    #         "englishTitle": "Displaying All",
    #         "nativeTitle": "",
    #         "coverMed": "",
    #         "episodes": 0,
    #         "seasons": 0,
    #         "movies": 0,
    #         "unairedSeasons": 0,
    #         "description": "Once upon a time there was mad anime. It was so cool.",
    #         "score": 0,
    #         "houseScores": [],
    #         "streaming": {}
    #     }
    #
    # scores, pacing_scores, drama_scores = sort_ratings(show["houseScores"])
    # colors = collect_colors(scores)
    # graph = collect_graph(pacing_scores, drama_scores, colors)
    # # TODO: Make this better and more universal. Maybe use url_for()?
    # if settings.TESTING:
    #     graph.savefig("project\\static\\graph.png")
    # else:
    #     graph.savefig("mysite/static/graph.png")
    # # genres = collect_genres(show)
    # # tags = collect_tags(show)
    # # warnings = collect_warnings(show)
    # # spoilers = collect_spoilers(show)
    # streaming = collect_streaming_colors(show)
    #
    # variables = {
    #     "title": collect_title(show),
    #     "image": f"{show['coverMed']}",
    #     "episodes": f"{show['episodes']}",
    #     "seasons": f"{show['seasons']}",
    #     "movies": f"{show['movies']}",
    #     "unaired": f"{show['unairedSeasons']}",
    #     "synopsis": show['description'],
    #     "public": f"{show['score']}",
    #     "graph": graph,
    #     "private": collect_private_score(show["houseScores"]),
    #     "chosen": session["selected_shows"],
    #     "stream_colors": streaming,
    # }
    #
    # return render_template("content/templates/content/display.html", **variables)


@CONTENT_BLUEPRINT.route("/options")
def options():
    show_id = request.args.get("selection", "")
    removal_id = request.args.get("chosen", "")
    clear = request.args.get("reset", "")
    if "selected_shows" not in session:
        session["selected_shows"] = []
    # if show_id:
    #     for show in library:
    #         if show["id"] == show_id and show not in session["selected_shows"]:
    #             session["selected_shows"].append({"id": show["id"], "defaultTitle": show["defaultTitle"]})
    #             session.modified = True
    if removal_id:
        for show in session["selected_shows"]:
            if show["id"] == removal_id:
                session["selected_shows"].remove(show)
                session.modified = True
    if clear:
        session["selected_shows"].clear()
        session.modified = True

    return render_template("content/templates/content/selection.html", chosen=session["selected_shows"])


@CONTENT_BLUEPRINT.route("/series/<int:series_id>", methods=["GET", "POST"])
def series(series_id):
    # Collecting house database information
    series = Series.query.get(series_id)
    if not series:
        abort(404)
    entry = Show.query.get(series.entry_point_id)

    if len(series.shows) == 1:
        return redirect(f"/shows/{entry.id}")
    sorted_shows = series.sort_shows()
    all_user_ratings = series.ratings_by_user()

    if current_user.is_authenticated:
        base_ratings = series.ratings_from_single_user(current_user.id)
        if base_ratings:
            current_user_average_ratings = sf.average_ratings(base_ratings)
        else:
            current_user_average_ratings = None
        spoiler_display = intf.spoiler_display_status(sorted_shows["main_shows"])
    else:
        current_user_average_ratings = None
        spoiler_display = "none"

    # Collecting Anilist database information
    seasonal_data = intf.seasonal_anilist_data(series_id)
    tags, spoilers = sf.collect_tags(seasonal_data["mainTags"])

    # Collecting user input
    x_data = request.args.get("x-coord", "")
    y_data = request.args.get("y-coord", "")
    data = sf.graph_data_selection(all_user_ratings, x_data, y_data)
    if x_data or y_data:
        return data

    if request.is_json:
        new_rating = request.get_json()
        intf.update_user_series_rating(new_rating, series_id)

    # Setting data and sending to user
    variables = {
        "title": sf.collect_title(series),
        "coverMed": entry.cover_med,
        "coverLarge": entry.cover_large,
        "totalEpisodes": sf.count_series_episodes(series.shows),
        "mainEpisodes": sf.count_series_episodes(sorted_shows["main_shows"]),
        "sorted_shows": sorted_shows,
        "movies": "N/A",
        "unaired": "N/A",
        "main_shows": sorted_shows["main_shows"],
        "main_seasons": len(sorted_shows["main_shows"]),
        "side_seasons": len(sorted_shows["side_shows"]),
        "minor_seasons": len(sorted_shows["minor_shows"]),
        "synopsis": entry.description,
        "genres": sf.collect_genres(seasonal_data["mainGenres"]),
        "tags": tags,
        "spoilers": spoilers,
        "public": "N/A",
        "stream_colors": sf.collect_streaming_colors(seasonal_data["mainAvailability"], series_length=len(sorted_shows["main_shows"])),
        "mainStreaming": seasonal_data["mainAvailability"],
        "sideStreaming": seasonal_data["sideAvailability"],
        "data": data,
        # "avgUserScore": collect_avg_user_score(show_id),
        "score": current_user_average_ratings["score"] if current_user_average_ratings else 0,
        "pacing": current_user_average_ratings["pacing"] if current_user_average_ratings else 0,
        "energy": current_user_average_ratings["energy"] if current_user_average_ratings else 0,
        "tone": current_user_average_ratings["tone"] if current_user_average_ratings else 0,
        "fantasy": current_user_average_ratings["fantasy"] if current_user_average_ratings else 0,
        "abstraction": current_user_average_ratings["abstraction"] if current_user_average_ratings else 0,
        "propriety": current_user_average_ratings["propriety"] if current_user_average_ratings else 0,
        "spoiler_display": spoiler_display,
        "url": f"/series/{series_id}"
    }

    return render_template(f"{TEMPLATE_PATH}/series_display.html", **variables)


@CONTENT_BLUEPRINT.route("/shows/<int:show_id>", methods=["GET", "POST"])
def show(show_id):
    # Collecting house database information
    show = Show.query.filter_by(id=show_id).first()
    if not show:
        abort(404)

    series = Series.query.filter_by(id=show.series_id).first()

    # TODO: Check whether this if statement is even necessary. If so, leave a comment on why.
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(show_id=show_id, user_id=current_user.id).first()
        spoiler_display = intf.spoiler_display_status([show])
    else:
        user_rating = None
        spoiler_display = "none"

    # Collecting Anilist database information
    anilist_request = sf.request_show_data(show.anilist_id)
    tags, spoilers = sf.collect_tags(anilist_request["tags"])
    availability = sf.check_stream_locations(anilist_request["externalLinks"])
    if show.status not in ("FINISHED", "CANCELLED"):
        show.update_entry(anilist_request)
        db.session.commit()

    # Collecting user input
    x_data = request.args.get("x-coord", "")
    y_data = request.args.get("y-coord", "")
    show_user_ratings = sf.dictify_ratings_list(show.user_ratings)
    data = sf.graph_data_selection(show_user_ratings, x_data, y_data)
    if x_data or y_data:
        return data

    list_addition = request.form.get("lists")
    if list_addition:
        intf.add_show_to_list(int(list_addition), show)

    if request.is_json:
        new_rating = request.get_json()
        intf.update_user_show_rating(show_id, user_rating, new_rating)

    # Setting data and sending to user
    variables = {
        "title": sf.collect_title(show),
        "image": show.cover_large,
        "episodes": show.episodes,
        "type": show.type,
        "synopsis": show.description,
        "position": show.position,
        "seasons": len(series.sort_shows()["main_shows"]),
        "series_id": show.series_id,
        "genres": sf.collect_genres(list(anilist_request["genres"])),
        "tags": tags,
        "spoilers": spoilers,
        "public": anilist_request["averageScore"],
        "stream_colors": sf.collect_streaming_colors(availability),
        "streaming": availability,
        "data": data,
        "avgUserScore": sf.collect_avg_user_score(show_user_ratings, "score"),
        "score": user_rating.score if user_rating else 0,
        "pacing": user_rating.pacing if user_rating else 0,
        "energy": user_rating.energy if user_rating else 0,
        "tone": user_rating.tone if user_rating else 0,
        "fantasy": user_rating.fantasy if user_rating else 0,
        "abstraction": user_rating.abstraction if user_rating else 0,
        "propriety": user_rating.propriety if user_rating else 0,
        "spoiler_display": spoiler_display,
        "url": f"/shows/{show_id}"
    }

    return render_template(f"{TEMPLATE_PATH}/show_display.html", **variables)


@CONTENT_BLUEPRINT.route("/series_list")
def series_list():
    # all_series = db.session.query(Series).all()
    sort_style = request.args.get("series-sorting")
    if sort_style:
        sorted_names, sorted_ids = intf.sort_series_names(sort_style)
        # return {"series_names": sorted_names, "series_ids": sorted_ids}
    elif current_user.names_preference == 1:
        sorted_names, sorted_ids = intf.sort_series_names("total-avg-score")
        sort_style = "total-avg-score"
    else:
        sorted_names, sorted_ids = intf.sort_series_names("alpha")
        sort_style = "alpha"

    variables = {
        "series_names": sorted_names,
        "series_ids": sorted_ids,
        "sort_style": sort_style
    }

    return render_template(f"{TEMPLATE_PATH}/series_list.html", **variables)
