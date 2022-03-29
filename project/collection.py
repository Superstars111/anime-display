import json
import tkinter as tk
from justwatch import JustWatch
import requests as rq

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


if __name__ == "__main__":
    with open("anime_data.json", "r") as anime_data:
        data = json.load(anime_data)

    retry = True
    while retry:
        duplicate = False
        media_id = input("Please input the show's id number. ")
        for show in data:
            if media_id == show["id"]:
                print("We already have that show collected.")
                duplicate = True
        if not duplicate:
            retry = False

    id_var = {"id": media_id}
    request = rq.post(url, json={"query": query, "variables": id_var}).json()['data']["Media"]
    total_episodes, seasons, unaired_seasons, movies, sequel = collect_seasonal_data(media_id, episodes=request["episodes"])

    jared_rating = [0, 0, 0]
    simon_rating = [0, 0, 0]
    kenan_rating = [0, 0, 0]

    print(f"The show is {request['title']['romaji']}, or {request['title']['english']}.")

    jared_rating[0] = int(input("Please input Jared's show rating from 1-100. "))
    jared_rating[1] = int(input("Please input Jared's pacing rating- -50 is slow, 50 is fast. "))
    jared_rating[2] = int(input("Please input Jared's comedy/drama rating. -50 is dramatic, 50 is funny. "))

    if input("Does Simon have available ratings? ").lower() in ("y", "yes"):
        simon_rating[0] = int(input("Please input Simon's show rating from 1-100. "))
        simon_rating[1] = int(input("Please input Simon's pacing rating- -50 is slow, 50 is fast. "))
        simon_rating[2] = int(input("Please input Simon's comedy/drama rating. -50 is dramatic, 50 is funny. "))

    if input("Does Kenan have available ratings? ").lower() in ("y", "yes"):
        kenan_rating[0] = int(input("Please input Kenan's show rating from 1-100. "))
        kenan_rating[1] = int(input("Please input Kenan's pacing rating- -50 is slow, 50 is fast. "))
        kenan_rating[2] = int(input("Please input Kenan's comedy/drama rating. -50 is dramatic, 50 is funny. "))


    entry = {
        "id": media_id,
        "romajiTitle": request["title"]["romaji"],
        "englishTitle": request["title"]["english"],
        "nativeTitle": request["title"]["native"],
        "description": request["description"],
        "episodes": total_episodes,
        "seasons": seasons,
        "unairedSeasons": unaired_seasons,
        "movies": movies,
        "coverLarge": request["coverImage"]["extraLarge"],
        "coverMed": request["coverImage"]["large"],
        "coverSmall": request["coverImage"]["medium"],
        "genres": request["genres"],
        "tags": request["tags"],
        "score": request["averageScore"],
        "jaredScore": jared_rating,
        "simonScore": simon_rating,
        "kenanScore": kenan_rating
    }

    data.append(entry)

    with open("anime_data.json", "w") as anime_data:
        json.dump(data, anime_data, indent=4)
