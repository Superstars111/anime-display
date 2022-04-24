from flask import Blueprint, request, session, render_template, url_for, redirect
import pandas as pd
import decimal as dc
import matplotlib
import matplotlib.pyplot as plt
from project.config import settings
from project.models import Show
import requests as rq

if settings.TESTING:
    full_data = pd.read_json("project/anime_data.json", typ="series", orient="records")
else:
    full_data = pd.read_json("/home/Superstars111/mysite/anime_data.json", typ="series", orient="records")

library = full_data[2]

url = "https://graphql.anilist.co/"
query = """query($id: Int){
  Media(id: $id, type: ANIME){
    title {
      romaji
      english
      native
    },
    format,
    description,
    episodes,
    relations{
      edges{
        relationType,
        node{
          id,
          episodes,
          format,
          status,
          externalLinks {
            site
          }
        }
      }
    },
    coverImage {
      extraLarge
      large
      medium
    },
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

    return render_template("content/templates/content/lib_display.html", **variables)


@content.route("/display")
def build_webpage():
    show_id = request.args.get("options_list", "")
    if "selected_shows" not in session:
        session["selected_shows"] = []

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
    streaming = collect_streaming_colors(show)

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
        "chosen": session["selected_shows"],
        "stream_colors": streaming,
    }

    return render_template("content/templates/content/display.html", **variables)


@content.route("/options")
def options():
    show_id = request.args.get("selection", "")
    removal_id = request.args.get("chosen", "")
    clear = request.args.get("reset", "")
    if "selected_shows" not in session:
        session["selected_shows"] = []
    if show_id:
        for show in library:
            if show["id"] == show_id and show not in session["selected_shows"]:
                session["selected_shows"].append({"id": show["id"], "defaultTitle": show["defaultTitle"]})
                session.modified = True
    if removal_id:
        for show in session["selected_shows"]:
            if show["id"] == removal_id:
                session["selected_shows"].remove(show)
                session.modified = True
    if clear:
        session["selected_shows"].clear()
        session.modified = True

    return render_template("content/templates/content/selection.html", library=library, chosen=session["selected_shows"])


@content.route("/shows/<int:show_id>")
def show(show_id):
    show = Show.query.filter_by(id=show_id).first()
    id_var = {"id": show.anilist_id}
    request = rq.post(url, json={"query": query, "variables": id_var}).json()['data']["Media"]
    series_data = {
        "sequel": [],
        "total_episodes": request["episodes"],
        "seasons": 1 if request["format"] in ("TV", "TV_SHORT") else 0,
        "movies": 1 if request["format"] == "MOVIE" else 0,
        "unaired_seasons": 0,
        "streaming": {
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
    }
    seasonal_data = collect_seasonal_data(show.anilist_id, series_data)
    scores, pacing_scores, drama_scores = sort_ratings(show.user_ratings)
    colors = collect_colors(scores)
    graph = collect_graph(pacing_scores, drama_scores, colors)

    variables = {
        "title": collect_title(show),
        "image": request["coverImage"]["large"],
        "episodes": seasonal_data["total_episodes"],
        "seasons": seasonal_data["seasons"],
        "movies": seasonal_data["movies"],
        "unaired": seasonal_data["unaired_seasons"],
        "synopsis": request["description"],
        "public": request["averageScore"],
        "graph": graph,
        "private": collect_private_score(show.user_ratings),
        "chosen": session["selected_shows"],
        "stream_colors": collect_streaming_colors(seasonal_data),
        "streaming": seasonal_data["streaming"]
    }

    if not show:
        return redirect(url_for("404"))
    return render_template("content/templates/content/display.html", **variables)


def find_show(id):
    for show in library:
        if show["id"] == id:
            return show


def collect_title(show):
    titles = []
    for title in (show.jp_name, show.en_name, show.rj_name):
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


def collect_private_score(ratings):
    all_house_scores = []
    for rating in ratings:
        if rating[1]:
            all_house_scores.append(rating[1])

    avg_house_score = get_average(all_house_scores)

    return avg_house_score


def collect_streaming_colors(show):
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
        if service[1]["seasons"] + service[1]["movies"] == 0:
            collections[service[0]] = ["gray", "gray"]
        elif service[1]["seasons"] == show["seasons"] and service[1]["movies"] == show["movies"]:
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
            collections[service[0]] = [color, "black"]
        else:
            collections[service[0]] = ["black", "black"]

    return collections


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


def collect_graph(pacing_scores, drama_scores, colors):
    matplotlib.use("Agg")
    fig = plt.Figure(figsize=(5, 4), dpi=100)
    graph = fig.add_subplot(111)
    # scatter_chart = FigureCanvasTkAgg(graph_frame, frm_ratings)
    plot_graph(graph, pacing_scores, drama_scores, colors)
    return fig


def plot_graph(graph, pacing_scores, drama_scores, colors):
    graph.cla()
    build_graph(graph)
    graph.scatter(pacing_scores, drama_scores, color=colors, picker=True)
    graph.figure.canvas.draw_idle()


def build_graph(graph):
    graph.grid()  # Adds a grid to the graph- does not add the graph to the Tkinter grid
    graph.scatter([50, -50], [50, -50], s=[0, 0])
    graph.set_ylabel("< Drama \u2022 Comedy >")
    graph.set_xlabel("< Slow Pacing \u2022 Fast Pacing >")


def collect_seasonal_data(show_id, seasonal_data):
    id_var = {"id": show_id}
    season_query = """query($id: Int){
                 Media(id: $id, type:ANIME){
                   format,
                   relations{
                     edges{
                       relationType,
                       node{
                         id,
                         episodes,
                         format,
                         status,
                         },
                       }
                     }
                   externalLinks {
                     site
                   },
                 }
               }"""
    show_data = rq.post(url, json={"query": season_query, "variables": id_var}).json()["data"]["Media"]

    seasonal_data = sort_seasonal_data(show_data, seasonal_data)

    for id in seasonal_data["sequel"]:
        seasonal_data = collect_seasonal_data(id, seasonal_data)
    return seasonal_data


def sort_seasonal_data(data_tree, seasonal_data):
    check_stream_locations(data_tree, seasonal_data["streaming"])
    seasonal_data["sequel"] = []
    for series in data_tree["relations"]["edges"]:
        if series["relationType"] == "SEQUEL":
            if series["node"]["format"] in ("TV", "TV_SHORT"):
                if series["node"]["status"] == "FINISHED":
                    seasonal_data["total_episodes"] += series["node"]["episodes"]
                    seasonal_data["seasons"] += 1
                else:
                    seasonal_data["unaired_seasons"] += 1
            elif series["node"]["format"] == "MOVIE":
                seasonal_data["movies"] += 1
            seasonal_data["sequel"].append(series["node"]["id"])

    return seasonal_data


def check_stream_locations(data_tree, stream_list):
    checked = []
    for value in data_tree["externalLinks"]:
        if value["site"] == "Crunchyroll" and "crunchyroll" not in checked:
            checked.append("crunchyroll")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["crunchyroll"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["crunchyroll"]["movies"] += 1
        elif value["site"] == "Funimation" and "funimation" not in checked:
            checked.append("funimation")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["funimation"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["funimation"]["movies"] += 1
        elif value["site"] == "Netflix" and "prison" not in checked:
            checked.append("prison")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["prison"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["prison"]["movies"] += 1
        elif value["site"] == "Amazon" and "amazon" not in checked:
            checked.append("amazon")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["amazon"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["amazon"]["movies"] += 1
        elif value["site"] == "VRV" and "vrv" not in checked:
            checked.append("vrv")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["vrv"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["vrv"]["movies"] += 1
        elif value["site"] == "Hulu" and "hulu" not in checked:
            checked.append("hulu")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["hulu"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["hulu"]["movies"] += 1
        elif value["site"] == "Youtube" and "youtube" not in checked:
            checked.append("youtube")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["youtube"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["youtube"]["movies"] += 1
        elif value["site"] == "Tubi TV" and "tubi" not in checked:
            checked.append("tubi")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["tubi"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["tubi"]["movies"] += 1
        elif value["site"] == "HBO Max" and "hbo" not in checked:
            checked.append("hbo")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["hbo"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["hbo"]["movies"] += 1
        elif value["site"] == "Hidive" and "hidive" not in checked:
            checked.append("hidive")
            if data_tree["format"] in ("TV", "TV_SHORT"):
                stream_list["hidive"]["seasons"] += 1
            elif data_tree["format"] == "MOVIE":
                stream_list["hidive"]["movies"] += 1
