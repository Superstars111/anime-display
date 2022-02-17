from flask import Flask
from flask import request
import pandas as pd

# NAMED BOB!!

download_data = pd.read_json("http://superstars111.pythonanywhere.com/library", typ="series", orient="records")
# mild_warnings = download_data[0]
# extreme_warnings = download_data[1]
# library = download_data[2]

library = [{
            "id": "20755",
            "romajiTitle": "Ansatsu Kyoushitsu",
            "englishTitle": "Assassination Classroom",
            "nativeTitle": "\u6697\u6bba\u6559\u5ba4",
            "defaultTitle": "Assassination Classroom",
            "format": "TV",
            "description": "The students of class 3-E have a mission: kill their teacher before graduation. He has already destroyed the moon, and has promised to destroy the Earth if he can not be killed within a year. But how can this class of misfits kill a tentacled monster, capable of reaching Mach 20 speed, who may be the best teacher any of them have ever had?",
            "episodes": 47,
            "seasons": 2,
            "unairedSeasons": 0,
            "movies": 0,
            "coverLarge": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20755-q0b3Ok1cAbPd.jpg",
            "coverMed": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx20755-q0b3Ok1cAbPd.jpg",
            "coverSmall": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/small/bx20755-q0b3Ok1cAbPd.jpg",
            "genres": [
                "Action",
                "Comedy",
                "Drama",
                "Supernatural"
            ],
            "tags": [
                {
                    "name": "Assassins",
                    "rank": 95,
                    "isMediaSpoiler": False
                },
                {
                    "name": "School",
                    "rank": 93,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Teacher",
                    "rank": 88,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Cultivation",
                    "rank": 86,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Shounen",
                    "rank": 79,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Ensemble Cast",
                    "rank": 75,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Super Power",
                    "rank": 67,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Anti-Hero",
                    "rank": 64,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Crime",
                    "rank": 61,
                    "isMediaSpoiler": True
                },
                {
                    "name": "Bullying",
                    "rank": 61,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Male Protagonist",
                    "rank": 56,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Guns",
                    "rank": 56,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Primarily Teen Cast",
                    "rank": 50,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Artificial Intelligence",
                    "rank": 48,
                    "isMediaSpoiler": True
                },
                {
                    "name": "Episodic",
                    "rank": 43,
                    "isMediaSpoiler": False
                },
                {
                    "name": "Crossdressing",
                    "rank": 41,
                    "isMediaSpoiler": True
                },
                {
                    "name": "Yandere",
                    "rank": 26,
                    "isMediaSpoiler": True
                }
            ],
            "score": 80,
            "streaming": {
                "crunchyroll": {
                    "seasons": 0,
                    "movies": 0
                },
                "funimation": {
                    "seasons": 2,
                    "movies": 0
                },
                "prison": {
                    "seasons": 2,
                    "movies": 0
                },
                "amazon": {
                    "seasons": 0,
                    "movies": 0
                },
                "vrv": {
                    "seasons": 0,
                    "movies": 0
                },
                "hulu": {
                    "seasons": 2,
                    "movies": 0
                },
                "youtube": {
                    "seasons": 1,
                    "movies": 0
                },
                "tubi": {
                    "seasons": 0,
                    "movies": 0
                },
                "hbo": {
                    "seasons": 0,
                    "movies": 0
                },
                "hidive": {
                    "seasons": 0,
                    "movies": 0
                }
            },
            "houseScores": [
                [
                    "Jared",
                    93,
                    25,
                    20
                ],
                [
                    "Simon",
                    95,
                    15,
                    25
                ],
                [
                    "Kenan",
                    70,
                    -10,
                    25
                ]
            ]
        }]

app = Flask(__name__)


@app.route("/")
def build_webpage():
    id = request.args.get("options_list", "")
    if id:
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
    else:
        title = "Assassination Classroom"

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
                    <aside id="options">
                        <form action=""><select name="options_list" onchange="this.form.submit()" size="38" style="width: 20em; margin: .75em">
                            <option value="20755">Assassination Classroom</option>
                            <option value="107663">ASTRA LOST IN SPACE</option>
                            <option value="Bob Ross">Bob Ross</option>
                            <option value="">Calculation</option>
                        </select></form>
                    </aside>"""
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
