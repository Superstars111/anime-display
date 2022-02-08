from flask import Flask
from flask import request
import pandas as pd

download_data = pd.read_json("anime_data.json", typ="series", orient="records")
mild_warnings = download_data[0]
extreme_warnings = download_data[1]
library = download_data[2]

app = Flask(__name__)


@app.route("/")
def build_webpage():
    id = request.args.get("options_list", "")
    show = find_show(id)
    title = collect_title(show)
    # image = collect_image(show)
    # episodes = collect_episodes(show)
    # seasons = collect_seasons(show)
    # movies = collect_movies(show)
    # unaired = collect_unaired(show)
    # synopsis = collect_synopsis(show)
    # public_score = collect_public_score(show)
    # private_score = collect_private_score(show)
    # graph = collect_graph(show)
    # genres = collect_genres(show)
    # tags = collect_tags(show)
    # warnings = collect_warnings(show)
    # spoilers = collect_spoilers(show)
    # streaming = collect_streaming(show)

    return (
        """<!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/html">
        <head>
            <meta charset="UTF-8">
            <link rel="stylesheet" href="main.css">
            <title>Anime Displayinator 9001 Beta</title>
        </head>
        <body>
            <div id="wrapper">
                <h1>Anime Data Program</h1>
                <nav>
                    <ul>
                        <li>Display Page</li>
                        <li>Select Options</li>
                        <li>Display All</li>
                        <li>Edit Show Data</li>
                        <li>Edit Warnings</li>
                    </ul>
                </nav>
                <main>
                    <aside id="options"><select name="options_list" size="38" style="width: 20em; margin: .75em">
                        <option value="20755">Assassination Classroom</option>
                        <option value="107663">ASTRA LOST IN SPACE</option>
                        <option value="Bob Ross">Bob Ross</option>
                        <option value="">Calculation</option>
                    </select></aside>"""
        + title)


def find_show(id):
    for show in library:
        if show["id"] == id:
            return show


def collect_title(show):
    return f"<h2>{show['nativeTitle']} \u2022 {show['englishTitle']} \u2022 {show['romajiTitle']}</h2>"


def collect_image(show):
    pass


def collect_episodes(show):
    pass


def collect_seasons(show):
    pass


def collect_movies(show):
    pass


def collect_unaired(show):
    pass


def collect_synopsis(show):
    pass


def collect_public_score(show):
    pass


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
