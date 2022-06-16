from flask import Blueprint, request, session, render_template, url_for, redirect
from flask_login import current_user
import pandas as pd
import decimal as dc
import matplotlib
import matplotlib.pyplot as plt
from project.config import settings
from project.models import Show, Rating, List, User, Series
from project import db
import requests as rq
import json
from project.integrated_functions import collect_seasonal_data, request_show_data, update_show_entry
from project.standalone_functions import assign_data, check_stream_locations, get_average, average_ratings

template_path = "content/templates/content"

content = Blueprint("content", __name__, template_folder="../../project")


@content.route("/display_all")
def display_all():
    episodes = 0
    seasons = 0
    movies = 0
    unaired = 0
    all_public_scores = []
    all_house_scores = []
    avg_show_scores = []
    avg_show_pacing = []
    avg_show_drama = []
    # for show in library:
    #     episodes += show["episodes"]
    #     seasons += show["seasons"]
    #     movies += show["movies"]
    #     unaired += show["unairedSeasons"]
    #     all_public_scores.append(show["score"])
    #     house_scores, pacing_scores, drama_scores = sort_ratings(show["houseScores"])
    #     if sum(house_scores):
    #         avg_show_scores.append(get_average(house_scores))
    #         avg_show_pacing.append(get_average(pacing_scores))
    #         avg_show_drama.append(get_average(drama_scores))
    #     if house_scores:
    #         for score in house_scores:
    #             all_house_scores.append(score)

    avg_public_score = get_average(all_public_scores)
    avg_house_score = get_average(all_house_scores)
    colors = collect_colors(avg_show_scores)
    # graph = collect_graph(avg_show_pacing, avg_show_drama, colors)
    # TODO: Make this more universal and not as cobbled together
    # if settings.TESTING:
    #     graph.savefig("project\\static\\full_graph.png")
    # else:
    #     graph.savefig("mysite/static/full_graph.png")

    variables = {
        "title": "Displaying All",
        "episodes": episodes,
        "seasons": seasons,
        "movies": movies,
        "unaired": unaired,
        # "synopsis": synopsis,
        "public": avg_public_score,
        # "graph": graph,
        "private": avg_house_score
    }

    return render_template("content/templates/content/lib_display.html", **variables)


@content.route("/compare")
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


@content.route("/options")
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


@content.route("/series/<int:series_id>")
def series(series_id):
    series = Series.query.get(series_id)
    if not series:
        return redirect(url_for("404"))
    entry = Show.query.get(series.entry_point_id)
    if len(series.shows) == 1:
        return redirect(f"/shows/{entry.id}")
    sorted_shows = series.sort_shows()
    all_user_ratings = series.ratings_by_user()

    seasonal_data = collect_seasonal_data(series_id)
    tags, spoilers = collect_tags(seasonal_data["mainTags"])

    x_data = request.args.get("x-coord", "")
    y_data = request.args.get("y-coord", "")
    data = assign_data(all_user_ratings, x_data, y_data)
    if x_data or y_data:
        return data

    new_rating = request.args.get("rate", "")
    if new_rating:
        current_seen_list = List.query.filter_by(owner_id=current_user.id, name="Seen").first()
        new_rating_data = {
            "score": request.args.get("score"),
            "pacing": request.args.get("pacing"),
            "energy": request.args.get("energy"),
            "tone": request.args.get("tone"),
            "fantasy": request.args.get("fantasy"),
            "abstraction": request.args.get("abstraction"),
            "propriety": request.args.get("propriety"),
        }
        for show in series.shows:
            if show in current_seen_list.shows:
                user_rating = Rating.query.filter_by(user_id=current_user.id, show_id=show.id).first()
                if not user_rating:
                    user_rating = Rating(user_id=current_user.id, show_id=show.id)
                    db.session.add(user_rating)

                user_rating.update(new_rating_data)

            db.session.commit()

    if current_user.is_authenticated:
        current_user_show_ratings = []
        for show in series.shows:
            current_user_rating = Rating.query.filter_by(show_id=show.id, user_id=current_user.id).first()
            if current_user_rating:
                current_user_show_ratings.append(current_user_rating)
        current_user_average_ratings = average_ratings(current_user_show_ratings)
    else:
        current_user_average_ratings = None

    variables = {
        "title": collect_title(series),
        "coverMed": entry.cover_med,
        "coverLarge": entry.cover_large,
        "totalEpisodes": seasonal_data["totalEpisodes"],
        "mainEpisodes": seasonal_data["mainSeriesEpisodes"],
        "sorted_shows": sorted_shows,
        "movies": "N/A",
        "unaired": "N/A",
        "main_shows": sorted_shows["main_shows"],
        "main_seasons": len(sorted_shows["main_shows"]),
        "side_seasons": len(sorted_shows["side_shows"]),
        "minor_seasons": len(sorted_shows["minor_shows"]),
        "synopsis": entry.description,
        "genres": collect_genres(seasonal_data["mainGenres"]),
        "tags": tags,
        "spoilers": spoilers,
        "public": "N/A",
        "stream_colors": collect_streaming_colors(seasonal_data["mainAvailability"], series=True),
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
        "url": f"/series/{series_id}"
    }

    return render_template(f"{template_path}/series_display.html", **variables)


@content.route("/shows/<int:show_id>", methods=["GET", "POST"])
def show(show_id):
    show = Show.query.filter_by(id=show_id).first()
    if not show:
        return redirect(url_for("404"))
    series = Series.query.filter_by(id=show.series_id).first()

    GQL_request = request_show_data(show.anilist_id)
    if show.status not in ("FINISHED", "CANCELLED"):
        show.update_entry(GQL_request)
        db.session.commit()

    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(show_id=show_id, user_id=current_user.id).first()
    else:
        user_rating = None

    x_data = request.args.get("x-coord", "")
    y_data = request.args.get("y-coord", "")
    data = assign_data(show.user_ratings, x_data, y_data)
    if x_data or y_data:
        return data

    list_addition = request.form.get("lists")
    if list_addition:
        selected_list = List.query.filter_by(id=list_addition).first()
        selected_list.shows += [show]
        db.session.commit()

    new_rating = request.args.get("rate", "")
    if new_rating:
        new_rating_data = {
            "score": request.args.get("score"),
            "pacing": request.args.get("pacing"),
            "energy": request.args.get("energy"),
            "tone": request.args.get("tone"),
            "fantasy": request.args.get("fantasy"),
            "abstraction": request.args.get("abstraction"),
            "propriety": request.args.get("propriety"),
        }
        if not user_rating:
            rating = Rating(show_id=show_id, user_id=current_user.id)
            rating.update(new_rating_data)
            db.session.add(rating)

        else:
            user_rating.update(new_rating_data)

        db.session.commit()

    tags, spoilers = collect_tags(GQL_request["tags"])
    availability = check_stream_locations(GQL_request["externalLinks"])

    variables = {
        "title": collect_title(show),
        "image": show.cover_large,
        "episodes": show.episodes,
        "type": show.type,
        "synopsis": show.description,
        "priority": show.priority,
        "seasons": len(series.sort_shows()["main_shows"]),
        "series_id": show.series_id,
        "genres": collect_genres(GQL_request["genres"]),
        "tags": tags,
        "spoilers": spoilers,
        "public": GQL_request["averageScore"],
        "stream_colors": collect_streaming_colors(availability),
        "streaming": availability,
        "data": data,
        "avgUserScore": collect_avg_user_score(show_id),
        "score": user_rating.score if user_rating else 0,
        "pacing": user_rating.pacing if user_rating else 0,
        "energy": user_rating.energy if user_rating else 0,
        "tone": user_rating.tone if user_rating else 0,
        "fantasy": user_rating.fantasy if user_rating else 0,
        "abstraction": user_rating.abstraction if user_rating else 0,
        "propriety": user_rating.propriety if user_rating else 0,
        "url": f"/shows/{show_id}"
    }

    return render_template(f"{template_path}/show_display.html", **variables)


@content.route("/series_list")
def series_list():
    all_series = db.session.query(Series).all()
    series_names = [series.rj_name for series in all_series]
    series_ids = [series.id for series in all_series]

    variables = {
        "series_names": series_names,
        "series_ids": series_ids
    }

    return render_template(f"{template_path}/series_list.html", **variables)


def collect_title(show):
    titles = []
    for title in (show.jp_name, show.en_name, show.rj_name):
        # Check to ensure title is not "None" before appending
        if title and title not in titles:
            titles.append(title)
    return f" \u2022 ".join(titles)


def collect_colors(scores):
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


def collect_avg_user_score(show_id):
    all_ratings = []
    for rating in Show.query.filter_by(id=show_id).first().user_ratings:
        all_ratings.append(rating.score)

    avg_user_score = get_average(all_ratings)

    if avg_user_score == 0:
        avg_user_score = "N/A"

    return avg_user_score


def collect_streaming_colors(availability: dict, series=False) -> dict:
    colors = {
        "crunchyroll": [],
        "funimation": [],
        "hidive": [],
        "vrv": [],
        "hulu": [],
        "amazon": [],
        "youtube": [],
        "prison": [],
        "hbo": [],
        "tubi": [],
    }
    for service in availability.items():
        if service[1]:
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
            colors[service[0]] += [color, "#000000"]
        else:
            colors[service[0]] += ["#808080", "#808080"]  # CSS Gray

    return colors


def sort_ratings(ratings):
    # Names are not currently used, but hopefully will be in the future
    names = []
    scores = []
    pacing_scores = []
    drama_scores = []
    # for rating in ratings:
    #     names.append(rating[0])
    #     scores.append(rating[1])
    #     pacing_scores.append(rating[2])
    #     drama_scores.append(rating[3])

    return scores, pacing_scores, drama_scores


def collect_genres(genres_list):
    genres = ", ".join(genres_list)
    return genres


def collect_tags(raw_tags: list):
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
