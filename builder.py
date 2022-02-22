from flask import Flask
from flask import request
from flask import render_template
import json
import pandas as pd

try:
    full_data = pd.read_json("anime_data.json", typ="series", orient="records")
except ValueError:
    full_data = pd.read_json("/home/Superstars111/mysite/anime_data.json", typ="series", orient="records")

library = full_data[2]

app = Flask(__name__)


@app.route("/")
def build_webpage():
    id = request.args.get("options_list", "")
    if id:
        show = find_show(id)
        title = collect_title(show)
        image = collect_image(show)
        episodes = collect_episodes(show)
        seasons = collect_seasons(show)
        movies = collect_movies(show)
        unaired = collect_unaired(show)
        synopsis = collect_synopsis(show)
        public_score = collect_public_score(show)
        # private_score = collect_private_score(show)
        # graph = collect_graph(show)
        # genres = collect_genres(show)
        # tags = collect_tags(show)
        # warnings = collect_warnings(show)
        # spoilers = collect_spoilers(show)
        # streaming = collect_streaming(show)
    else:
        title = "Title"
        image = "Image"
        episodes = "Episodes"
        seasons = "Seasons"
        movies = "Movies"
        unaired = "Unaired"
        synopsis = "Synopsis"
        public_score = "Public"
        # private_score = collect_private_score(show)
        # graph = collect_graph(show)
        # genres = collect_genres(show)
        # tags = collect_tags(show)
        # warnings = collect_warnings(show)
        # spoilers = collect_spoilers(show)
        # streaming = collect_streaming(show)

    variables = {
        "title": title,
        "image": image,
        "episodes": episodes,
        "seasons": seasons,
        "movies": movies,
        "unaired": unaired,
        "synopsis": synopsis,
        "public": public_score,
    }

    return render_template("home.html", **variables)


def find_show(id):
    for show in library:
        if show["id"] == id:
            return show


def collect_title(show):
    return f"{show['nativeTitle']} \u2022 {show['englishTitle']} \u2022 {show['romajiTitle']}"


def collect_image(show):
    return f"{show['coverMed']}"


def collect_episodes(show):
    return f"{show['episodes']}"


def collect_seasons(show):
    return f"{show['seasons']}"


def collect_movies(show):
    return f"{show['movies']}"


def collect_unaired(show):
    return f"{show['unairedSeasons']}"


def collect_synopsis(show):
    return show['description']


def collect_public_score(show):
    return f"{show['score']}"


def collect_private_score(show):
    pass


def collect_graph(show):
    pass


def collect_genres(show):
    pass


def collect_tags(show):
    pass


def collect_warnings(show):
    pass


def collect_spoilers(show):
    pass


def collect_streaming(show):
    pass


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
