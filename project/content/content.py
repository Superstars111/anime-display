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
from project.functions import assign_data, collect_seasonal_data, sort_seasonal_data, check_stream_locations

# if settings.TESTING:
#     full_data = pd.read_json("project/anime_data.json", typ="series", orient="records")
# else:
#     full_data = pd.read_json("/home/Superstars111/mysite/anime_data.json", typ="series", orient="records")
#
# library = full_data[2]

url = "https://graphql.anilist.co/"
query = """query($id: Int){
  Media(id: $id, type: ANIME){
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
    # if current_user.is_authenticated:
    #     user_rating = Rating.query.filter_by(show_id=show_id, user_id=current_user.id).first()
    # else:
    #     user_rating = None

    id_var = {"id": entry.anilist_id}
    GQL_request = rq.post(url, json={"query": query, "variables": id_var}).json()['data']["Media"]
    series_data = {
        "sequel": [],
        "total_episodes": GQL_request["episodes"],
        "seasons": 1 if GQL_request["format"] in ("TV", "TV_SHORT") else 0,
        "movies": 1 if GQL_request["format"] == "MOVIE" else 0,
        "unaired_seasons": 0,
        "streaming": {
            "crunchyroll": {"seasons": 0,
                            "movies": 0
                            },
            "funimation": {"seasons": 0,
                           "movies": 0
                           },
            "prison": {"seasons": 0,
                       "movies": 0
                       },
            "amazon": {"seasons": 0,
                       "movies": 0
                       },
            "vrv": {"seasons": 0,
                    "movies": 0
                    },
            "hulu": {"seasons": 0,
                     "movies": 0
                     },
            "youtube": {"seasons": 0,
                        "movies": 0
                        },
            "tubi": {"seasons": 0,
                     "movies": 0
                     },
            "hbo": {"seasons": 0,
                    "movies": 0
                    },
            "hidive": {"seasons": 0,
                       "movies": 0
                       }
        }
    }
    seasonal_data = collect_seasonal_data(entry.anilist_id, series_data)
    tags, spoilers = collect_tags(GQL_request["tags"])

    variables = {
        "title": collect_title(series),
        "image": entry.cover_image,
        "episodes": sum([show.episodes for show in series.shows]),
        "seasons": seasonal_data["seasons"],
        "movies": seasonal_data["movies"],
        "unaired": seasonal_data["unaired_seasons"],
        "synopsis": entry.description,
        "genres": collect_genres(GQL_request["genres"]),
        "tags": tags,
        "spoilers": spoilers,
        "public": GQL_request["averageScore"],
        "stream_colors": collect_streaming_colors(seasonal_data),
        "streaming": seasonal_data["streaming"],
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

    return render_template("content/templates/content/series_display.html", **variables)


@content.route("/shows/<int:show_id>", methods=["GET", "POST"])
def show(show_id):
    show = Show.query.filter_by(id=show_id).first()
    if not show:
        return redirect(url_for("404"))
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

    id_var = {"id": show.anilist_id}
    GQL_request = rq.post(url, json={"query": query, "variables": id_var}).json()['data']["Media"]

    streaming = {
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

    # seasonal_data = collect_seasonal_data(show.anilist_id, series_data)
    tags, spoilers = collect_tags(GQL_request["tags"])
    availability = check_stream_locations(GQL_request["externalLinks"])
    # scores, pacing_scores, drama_scores = sort_ratings(user_rating)
    # colors = collect_colors(scores)
    # graph = collect_graph(pacing_scores, drama_scores, colors)

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


# def find_show(id):
#     for show in library:
#         if show["id"] == id:
#             return show


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
        if service[1] is True:
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


def get_average(numbers_list):
    average = 0
    if numbers_list:
        dc.getcontext().rounding = dc.ROUND_HALF_UP
        average = sum(numbers_list) / len(numbers_list)
        average = int(dc.Decimal(str(average)).quantize(dc.Decimal("1")))

    return average


def collect_genres(genres_list):
    genres = ", ".join(genres_list)
    return genres


def collect_tags(tags_list):
    tags = []
    spoilers = []
    for tag in tags_list:
        s = f"{tag['name']} ({tag['rank']}%)"
        if tag['isMediaSpoiler']:
            spoilers.append(s)
        else:
            tags.append(s)

    tags = ", ".join(tags)
    spoilers = ", ".join(spoilers)
    return tags, spoilers


# def collect_graph(pacing_scores, drama_scores, colors):
#     matplotlib.use("Agg")
#     fig = plt.Figure(figsize=(5, 4), dpi=100)
#     graph = fig.add_subplot(111)
#     # scatter_chart = FigureCanvasTkAgg(graph_frame, frm_ratings)
#     plot_graph(graph, pacing_scores, drama_scores, colors)
#     return fig
#
#
# def plot_graph(graph, pacing_scores, drama_scores, colors):
#     graph.cla()
#     build_graph(graph)
#     graph.scatter(pacing_scores, drama_scores, color=colors, picker=True)
#     graph.figure.canvas.draw_idle()
#
#
# def build_graph(graph):
#     graph.grid()  # Adds a grid to the graph- does not add the graph to the Tkinter grid
#     graph.scatter([50, -50], [50, -50], s=[0, 0])
#     graph.set_ylabel("< Drama \u2022 Comedy >")
#     graph.set_xlabel("< Slow Pacing \u2022 Fast Pacing >")



