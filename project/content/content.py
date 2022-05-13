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
from project.functions import assign_data, collect_seasonal_data, check_stream_locations, request_show_data, \
    update_show_entry, get_average

# if settings.TESTING:
#     full_data = pd.read_json("project/anime_data.json", typ="series", orient="records")
# else:
#     full_data = pd.read_json("/home/Superstars111/mysite/anime_data.json", typ="series", orient="records")
#
# library = full_data[2]

template_path = "content/templates/content"

# url = "https://graphql.anilist.co/"
# query = """query($id: Int){
#   Media(id: $id, type: ANIME){
#     genres,
#     tags {
#       name,
#       rank,
#       isMediaSpoiler
#     },
#     averageScore,
#     externalLinks {
#       site
#     }
#   }
# }"""
# stream_info = {
#             "crunchyroll": {"seasons": 0,
#                             "movies": 0
#                             },
#             "funimation":  {"seasons": 0,
#                             "movies": 0
#                             },
#             "prison":      {"seasons": 0,
#                             "movies": 0
#                             },
#             "amazon":      {"seasons": 0,
#                             "movies": 0
#                             },
#             "vrv":         {"seasons": 0,
#                             "movies": 0
#                             },
#             "hulu":        {"seasons": 0,
#                             "movies": 0
#                             },
#             "youtube":     {"seasons": 0,
#                             "movies": 0
#                             },
#             "tubi":        {"seasons": 0,
#                             "movies": 0
#                             },
#             "hbo":         {"seasons": 0,
#                             "movies": 0
#                             },
#             "hidive":      {"seasons": 0,
#                             "movies": 0
#                             }
#         }


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
    series = Series.query.filter_by(id=series_id).first()
    if not series:
        return redirect(url_for("404"))
    entry = Show.query.filter_by(id=series.entry_point_id).first()

    seasonal_data = collect_seasonal_data(series_id)
    tags, spoilers = collect_tags(seasonal_data["mainTags"])

    variables = {
        "title": collect_title(series),
        "image": entry.cover_image,
        "totalEpisodes": sum([show.episodes for show in series.shows]),
        "seasons": len(seasonal_data["mainShows"]),
        "movies": "N/A",
        "unaired": "N/A",
        "synopsis": entry.description,
        "genres": collect_genres(seasonal_data["mainGenres"]),
        "tags": tags,
        "spoilers": spoilers,
        "public": "N/A",
        "stream_colors": collect_streaming_colors(seasonal_data["mainAvailability"], series=True),
        "mainStreaming": seasonal_data["mainAvailability"],
        "sideStreaming": seasonal_data["sideAvailability"],
        # "data": data,
        # "avgUserScore": collect_avg_user_score(show_id),
        # "score": user_rating.score if user_rating else 0,
        # "pacing": user_rating.pacing if user_rating else 0,
        # "energy": user_rating.energy if user_rating else 0,
        # "tone": user_rating.drama if user_rating else 0,
        # "fantasy": user_rating.fantasy if user_rating else 0,
        # "abstraction": user_rating.abstraction if user_rating else 0,
        # "propriety": user_rating.propriety if user_rating else 0,
        "url": f"/series/{series_id}"
    }

    return render_template(f"{template_path}/series_display.html", **variables)


@content.route("/shows/<int:show_id>", methods=["GET", "POST"])
def show(show_id):
    show = Show.query.filter_by(id=show_id).first()
    if not show:
        return redirect(url_for("404"))

    GQL_request = request_show_data(show.anilist_id)
    if show.status not in ("FINISHED", "CANCELLED"):
        update_show_entry(show.anilist_id, GQL_request)
        show = Show.query.filter_by(id=show_id).first()

    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(show_id=show_id, user_id=current_user.id).first()
    else:
        user_rating = None

    x_data = request.args.get("x-coord", "")
    y_data = request.args.get("y-coord", "")
    data = assign_data(show.user_ratings, x_data, y_data)
    if x_data or y_data:
        return data

    new_rating = request.args.get("rate", "")
    list_addition = request.form.get("lists")

    if list_addition:
        selected_list = List.query.filter_by(id=list_addition).first()
        selected_list.shows += [show]
        db.session.commit()
    if new_rating:
        if not user_rating:
            rating = Rating(show_id=show_id, user_id=current_user.id)
            db.session.add(rating)

        user_rating.score = request.args.get("score")
        user_rating.pacing = request.args.get("pacing")
        user_rating.energy = request.args.get("energy")
        user_rating.drama = request.args.get("tone")
        user_rating.fantasy = request.args.get("fantasy")
        user_rating.abstraction = request.args.get("abstraction")
        user_rating.propriety = request.args.get("propriety")

        db.session.commit()

    tags, spoilers = collect_tags(GQL_request["tags"])
    availability = check_stream_locations(GQL_request["externalLinks"])

    variables = {
        "title": collect_title(show),
        "image": show.cover_image,
        "episodes": show.episodes,
        "type": show.type,
        "synopsis": show.description,
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
        "tone": user_rating.drama if user_rating else 0,
        "fantasy": user_rating.fantasy if user_rating else 0,
        "abstraction": user_rating.abstraction if user_rating else 0,
        "propriety": user_rating.propriety if user_rating else 0,
        "url": f"/shows/{show_id}"
    }

    return render_template("content/templates/content/show_display.html", **variables)


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
    dc.getcontext().rounding = dc.ROUND_HALF_UP
    for rating in Show.query.filter_by(id=show_id).first().user_ratings:
        all_ratings.append(rating.score)

    # TODO: Modify get_average() for use here
    if all_ratings:
        avg_user_score = sum(all_ratings) / (len(all_ratings) if all_ratings else 1)
        avg_user_score = int(dc.Decimal(str(avg_user_score)).quantize(dc.Decimal("1")))
    else:
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
            if service[0] == "crunchyroll":
                color = "orange"
            elif service[0] in ("funimation", "hbo"):
                color = "purple"
            elif service[0] in ("hidive", "amazon"):
                color = "dodgerBlue"
            elif service[0] == "vrv":
                color = "gold"
            elif service[0] == "hulu":
                color = "springGreen"
            elif service[0] in ("youtube", "prison", "tubi"):
                color = "red"
            else:
                color = "black"
            colors[service[0]] += [color, "black"]
        else:
            colors[service[0]] += ["gray", "gray"]

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
