from flask import Flask, request, render_template, redirect, Blueprint, url_for, session
from flask_login import login_required, current_user, login_user
# from models import db, login, UserModel
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import decimal as dc
from . import db
from .config import settings

if settings.TESTING:
    full_data = pd.read_json("project/anime_data.json", typ="series", orient="records")
else:
    full_data = pd.read_json("/home/Superstars111/mysite/anime_data.json", typ="series", orient="records")

library = full_data[2]
selected_shows = []
testing = True


main = Blueprint("main", __name__)
# app = Flask(__name__)
# app.secret_key = "testing"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///anime-display-users.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db.init_app(app)
# login.init_app(app)
# login.login_view = "login"


# @app.before_first_request
# def create_table():
#     db.create_all()


@main.route("/")
def index():
    return "Homepage"


@main.route("/display_all")
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
    for show in library:
        episodes += show["episodes"]
        seasons += show["seasons"]
        movies += show["movies"]
        unaired += show["unairedSeasons"]
        all_public_scores.append(show["score"])
        house_scores, pacing_scores, drama_scores = sort_ratings(show["houseScores"])
        if sum(house_scores):
            avg_show_scores.append(get_average(house_scores))
            avg_show_pacing.append(get_average(pacing_scores))
            avg_show_drama.append(get_average(drama_scores))
        if house_scores:
            for score in house_scores:
                all_house_scores.append(score)

    avg_public_score = get_average(all_public_scores)
    avg_house_score = get_average(all_house_scores)
    colors = collect_colors(avg_show_scores)
    graph = collect_graph(avg_show_pacing, avg_show_drama, colors)
    # TODO: Make this more universal and not as cobbled together
    if settings.TESTING:
        graph.savefig("project\\static\\full_graph.png")
    else:
        graph.savefig("mysite/static/full_graph.png")

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

    return render_template("lib_display.html", **variables)


@main.route("/display")
def build_webpage():
    show_id = request.args.get("options_list", "")

    if show_id:
        show = find_show(show_id)
    else:
        show = {
            "romajiTitle": "",
            "englishTitle": "Displaying All",
            "nativeTitle": "",
            "coverMed": "",
            "episodes": 0,
            "seasons": 0,
            "movies": 0,
            "unairedSeasons": 0,
            "description": "Once upon a time there was mad anime. It was so cool.",
            "score": 0,
            "houseScores": [],
            "streaming": {}
        }

    scores, pacing_scores, drama_scores = sort_ratings(show["houseScores"])
    colors = collect_colors(scores)
    graph = collect_graph(pacing_scores, drama_scores, colors)
    # TODO: Make this better and more universal. Maybe use url_for()?
    if settings.TESTING:
        graph.savefig("project\\static\\graph.png")
    else:
        graph.savefig("mysite/static/graph.png")
    # genres = collect_genres(show)
    # tags = collect_tags(show)
    # warnings = collect_warnings(show)
    # spoilers = collect_spoilers(show)
    streaming = collect_streaming(show)

    variables = {
        "title": collect_title(show),
        "image": f"{show['coverMed']}",
        "episodes": f"{show['episodes']}",
        "seasons": f"{show['seasons']}",
        "movies": f"{show['movies']}",
        "unaired": f"{show['unairedSeasons']}",
        "synopsis": show['description'],
        "public": f"{show['score']}",
        "graph": graph,
        "private": collect_private_score(show["houseScores"]),
        "chosen": selected_shows,
        "stream_colors": streaming,
    }

    return render_template("home.html", **variables)


@main.route("/options")
def options():
    show_id = request.args.get("selection", "")
    removal_id = request.args.get("chosen", "")
    clear = request.args.get("reset", "")
    if show_id:
        for show in library:
            if show["id"] == show_id and show not in selected_shows:
                selected_shows.append(show)
    if removal_id:
        for show in selected_shows:
            if show["id"] == removal_id:
                selected_shows.remove(show)
    if clear:
        selected_shows.clear()

    return render_template("selection.html", library=library, chosen=selected_shows)


@main.route("/edit")
@login_required
def edit():
    return """This page is a work in progress. <a href="/display">Go back</a>"""


@main.route("/warnings")
@login_required
def warnings():
    return """This page is a work in progress. <a href="/display">Go back</a>"""


@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html", name=current_user.username)


@main.errorhandler(404)
def error404(error):
    return """Sorry, but much like Asta's ability to control his volume, this page does not exist. 
    <a href="/display">Go back</a>"""


def find_show(id):
    for show in library:
        if show["id"] == id:
            return show


def collect_title(show):
    titles = []
    for title in (show["nativeTitle"], show["englishTitle"], show["romajiTitle"]):
        if title and title not in titles:
            titles.append(title)
    return f" \u2022 ".join(titles)


# def collect_image(show):
#     return f"{show['coverMed']}"
#
#
# def collect_episodes(show):
#     return f"{show['episodes']}"
#
#
# def collect_seasons(show):
#     return f"{show['seasons']}"
#
#
# def collect_movies(show):
#     return f"{show['movies']}"
#
#
# def collect_unaired(show):
#     return f"{show['unairedSeasons']}"
#
#
# def collect_synopsis(show):
#     return show['description']
#
#
# def collect_public_score(show):
#     return f"{show['score']}"


def collect_private_score(ratings):
    all_house_scores = []
    for rating in ratings:
        if rating[1]:
            all_house_scores.append(rating[1])

    avg_house_score = get_average(all_house_scores)

    return avg_house_score


def collect_graph(pacing_scores, drama_scores, colors):
    matplotlib.use("Agg")
    fig = plt.Figure(figsize=(5, 4), dpi=100)
    graph = fig.add_subplot(111)
    # scatter_chart = FigureCanvasTkAgg(graph_frame, frm_ratings)
    plot_graph(graph, pacing_scores, drama_scores, colors)
    return fig


def collect_genres(show):
    pass


def collect_tags(show):
    pass


def collect_warnings(show):
    pass


def collect_spoilers(show):
    pass


def collect_streaming(show):
    collections = {
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
    for service in show["streaming"].items():
        # print(service)
        if service[1]["seasons"] + service[1]["movies"] == 0:
            collections[service[0]] = ["gray", "gray"]
        elif service[1]["seasons"] == show["seasons"] and service[1]["movies"] == show["movies"]:
            if service[0] == "crunchyroll":
                color = "orange"
            elif service[0] == ("funimation" or "hbo"):
                color = "purple"
            elif service[0] == ("hidive" or "amazon"):
                color = "dodger blue"
            elif service[0] == "vrv":
                color = "gold"
            elif service[0] == "hulu":
                color = "lime green"
            elif service[0] == ("youtube" or "prison" or "tubi"):
                color = "red"
            else:
                color = "black"
            collections[service[0]] = [color, "black"]
        else:
            collections[service[0]] = ["black", "black"]

    return collections


def build_graph(graph):
    graph.grid()  # Adds a grid to the graph- does not add the graph to the Tkinter grid
    graph.scatter([50, -50], [50, -50], s=[0, 0])
    graph.set_ylabel("< Drama \u2022 Comedy >")
    graph.set_xlabel("< Slow Pacing \u2022 Fast Pacing >")


def plot_graph(graph, pacing_scores, drama_scores, colors):
    graph.cla()
    build_graph(graph)
    graph.scatter(pacing_scores, drama_scores, color=colors, picker=True)
    graph.figure.canvas.draw_idle()


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


def sort_ratings(ratings):
    # Names are not currently used, but hopefully will be in the future
    names = []
    scores = []
    pacing_scores = []
    drama_scores = []

    for rating in ratings:
        names.append(rating[0])
        scores.append(rating[1])
        pacing_scores.append(rating[2])
        drama_scores.append(rating[3])

    return scores, pacing_scores, drama_scores


def get_average(numbers_list):
    average = 0
    if numbers_list:
        dc.getcontext().rounding = dc.ROUND_HALF_UP
        average = sum(numbers_list) / len(numbers_list)
        average = int(dc.Decimal(str(average)).quantize(dc.Decimal("1")))

    return average


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=8080, debug=True)
    pass
