import json
import requests as rq
import collection
import tkinter as tk
import tkinter.font as fnt
import urllib.request
from PIL import Image, ImageTk
import io
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.text import Annotation
import decimal as dc
import alphabetize
import time

# app = Flask(__name__)

with open("templates/home.html", "r") as data:
    webpage = data


download_data = pd.read_json("anime_data.json", typ="series", orient="records")

options = []
option_titles = []
library_titles = []
cover_image = []
mild_warnings = download_data[0]
extreme_warnings = download_data[1]
library = download_data[2]
content_warnings = [0, 0, 0]

for show in library:
    library_titles.append(show["defaultTitle"])


class Root:
    def __init__(self, parent):
        self.parent = parent
        parent.title("Anime Data Displayinator 9001 (Beta)")
        self.show = {}
        self.spoiler_state = tk.IntVar()

        # Build main window
        self.lbox_options = tk.Listbox(self.parent, height=35)
        self.lbox_options.bind("<<ListboxSelect>>", self.update_page_display)
        btn_options = tk.Button(self.parent, text="Add Options", command=self.add_options)
        btn_display_all = tk.Button(self.parent, text="Display All", command=self.display_all)
        self.frm_anime_display = tk.Frame(self.parent)
        self.lbl_title = tk.Label(self.frm_anime_display, text="Anime Data Program", font=("Arial", 20), wraplength=900)

        # Build ratings frame
        self.frm_ratings = tk.Frame(self.frm_anime_display)
        self.lbl_avg_rating = tk.Label(self.frm_ratings, text="Public score: 0/100")
        self.lbl_house_rating = tk.Label(self.frm_ratings, text="House score: 0/100")
        self.lbl_public_star = tk.Label(self.frm_ratings, text="\u2605")
        self.lbl_house_star = tk.Label(self.frm_ratings, text="\u2605")
        self.graph_frame = plt.Figure(figsize=(5, 4), dpi=100)
        self.graph = self.graph_frame.add_subplot(111)
        self.scatter_chart = FigureCanvasTkAgg(self.graph_frame, self.frm_ratings)
        self.build_graph()
        self.labels = []
        self.graph_frame.canvas.mpl_connect('pick_event', self.onpick)

        # Build data frame
        self.frm_series_info = tk.Frame(self.frm_anime_display)
        self.lbl_cover_image = tk.Label(self.frm_series_info)
        self.lbl_episodes = tk.Label(self.frm_series_info, text="Episodes: 0")
        self.lbl_seasons = tk.Label(self.frm_series_info, text="Seasons: 0")
        self.lbl_unaired_seasons = tk.Label(self.frm_series_info, text="Unfinished Seasons: 0", width=22)
        self.lbl_movies = tk.Label(self.frm_series_info, text="Movies: 0")

        # Build tags frame
        self.frm_tags = tk.Frame(self.frm_anime_display)
        lbl_genres = tk.Label(self.frm_tags, text="Genres:")
        self.lbl_genres_list = tk.Label(self.frm_tags, text="", wraplength=490)
        lbl_tags = tk.Label(self.frm_tags, text="Tags:")
        self.lbl_tags_list = tk.Label(self.frm_tags, text="", wraplength=490)
        lbl_warnings = tk.Label(self.frm_tags, text="Content Warnings:")
        self.lbl_warnings_list = tk.Label(self.frm_tags, text="", wraplength=490)
        self.cbox_spoiler_tags = tk.Checkbutton(self.frm_tags, text="\u25B6 Spoiler Tags: (0, 0, 0)",
                                                command=self.toggle_spoilers, variable=self.spoiler_state)
        self.lbl_spoiler_tags = tk.Label(self.frm_tags, text="SPOILERS! Hide this before selecting a series.",
                                         wraplength=490)

        # Build synopsis frame
        self.frm_description = tk.Frame(self.frm_anime_display, width=300, height=150, borderwidth=2, relief="solid")
        self.txt_description = tk.Text(self.frm_description, height=9, width=55, state="disabled",
                                       wrap="word", bg="gray92")
        # TODO: txt_description font=default_font if going back to TKinter
        self.sbar = tk.Scrollbar(self.frm_description, orient=tk.VERTICAL, command=self.txt_description.yview)
        lbl_streaming = tk.Label(self.frm_description, text="Streaming Locations:")
        self.frm_stream_locations = tk.Frame(self.frm_description)
        lbl_crunchy_name = tk.Label(self.frm_stream_locations, text="Crunchyroll")
        lbl_crunchy_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_crunchy_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")
        lbl_funi_name = tk.Label(self.frm_stream_locations, text="Funimation")
        lbl_funi_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_funi_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")
        lbl_hidive_name = tk.Label(self.frm_stream_locations, text="Hidive")
        lbl_hidive_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_hidive_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")
        lbl_vrv_name = tk.Label(self.frm_stream_locations, text="VRV")
        lbl_vrv_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_vrv_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")
        lbl_hulu_name = tk.Label(self.frm_stream_locations, text="Hulu")
        lbl_hulu_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_hulu_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")
        lbl_amazon_name = tk.Label(self.frm_stream_locations, text="Amazon Prime")
        lbl_amazon_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_amazon_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")
        lbl_youtube_name = tk.Label(self.frm_stream_locations, text="YouTube")
        lbl_youtube_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_youtube_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")
        lbl_prison_name = tk.Label(self.frm_stream_locations, text="Netflix Prison")
        lbl_prison_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_prison_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")
        lbl_hbo_name = tk.Label(self.frm_stream_locations, text="HBO Max")
        lbl_hbo_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_hbo_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")
        lbl_tubi_name = tk.Label(self.frm_stream_locations, text="Tubi TV")
        lbl_tubi_seasons = tk.Label(self.frm_stream_locations, text="Seasons: 0")
        lbl_tubi_movies = tk.Label(self.frm_stream_locations, text="Movies: 0")



        # Grid main window
        self.lbox_options.grid(row=0, column=1, columnspan=2, sticky="ns", padx=10, pady=5)
        btn_options.grid(row=1, column=2, pady=7, padx=3, sticky="s")
        self.frm_anime_display.grid(row=0, column=0, rowspan=2)
        self.frm_anime_display.rowconfigure(0, minsize=120)
        self.lbl_title.grid(row=0, column=0, columnspan=2, pady=8)
        btn_display_all.grid(row=1, column=1, pady=7, padx=3, sticky="s")

        # Grid ratings frame
        self.frm_ratings.grid(row=1, column=0, padx=15)
        self.lbl_avg_rating.grid(row=0, column=0, sticky="e")
        self.lbl_public_star.grid(row=0, column=1, sticky="w")
        self.lbl_house_rating.grid(row=0, column=2, sticky="e")
        self.lbl_house_star.grid(row=0, column=3, sticky="w")
        self.scatter_chart.get_tk_widget().grid(row=1, column=0, columnspan=4)

        # Grid data frame
        self.lbl_cover_image.grid(row=0, column=0, rowspan=4, sticky="w", padx=15)
        self.lbl_episodes.grid(row=0, column=1)
        self.lbl_seasons.grid(row=1, column=1)
        self.lbl_movies.grid(row=2, column=1)
        self.lbl_unaired_seasons.grid(row=3, column=1)
        self.frm_series_info.grid(row=1, column=1)
        self.frm_series_info.rowconfigure((0, 1, 2, 3), minsize=90)
        self.frm_series_info.columnconfigure(0, minsize=270)

        # Grid tags frame
        self.frm_tags.grid(row=2, column=0, sticky="n")
        lbl_genres.grid(row=0, column=0, sticky="n")
        self.frm_tags.rowconfigure(1, minsize=50)
        self.lbl_genres_list.grid(row=1, column=0)
        lbl_tags.grid(row=2, column=0, sticky="n")
        self.frm_tags.rowconfigure(3, minsize=115)
        self.lbl_tags_list.grid(row=3, column=0)
        lbl_warnings.grid(row=4, column=0)
        self.frm_tags.rowconfigure(5, minsize=50)
        self.lbl_warnings_list.grid(row=5, column=0)
        self.cbox_spoiler_tags.grid(row=6, column=0)
        self.frm_tags.rowconfigure(7, minsize=70)

        # Grid synopsis frame
        self.frm_description.grid(row=2, column=1, padx=10, pady=15, sticky="n")
        self.frm_description.columnconfigure(0)
        self.frm_description.rowconfigure(0, minsize=150)
        self.txt_description.grid(row=0, column=0)
        self.sbar.grid(row=0, column=1, sticky="ns")
        lbl_streaming.grid(row=1, column=0)

        self.frm_stream_locations.columnconfigure((0, 1, 2, 3, 4), minsize=100)
        self.frm_stream_locations.rowconfigure(2, minsize=45)
        self.frm_stream_locations.rowconfigure(5, minsize=45)
        self.frm_stream_locations.grid(row=2, column=0, columnspan=2)
        lbl_crunchy_name.grid(row=0, column=0)
        lbl_crunchy_seasons.grid(row=1, column=0)
        lbl_crunchy_movies.grid(row=2, column=0, sticky="n")
        lbl_funi_name.grid(row=0, column=1)
        lbl_funi_seasons.grid(row=1, column=1)
        lbl_funi_movies.grid(row=2, column=1, sticky="n")
        lbl_hidive_name.grid(row=0, column=2)
        lbl_hidive_seasons.grid(row=1, column=2)
        lbl_hidive_movies.grid(row=2, column=2, sticky="n")
        lbl_vrv_name.grid(row=0, column=3)
        lbl_vrv_seasons.grid(row=1, column=3)
        lbl_vrv_movies.grid(row=2, column=3, sticky="n")
        lbl_hulu_name.grid(row=0, column=4)
        lbl_hulu_seasons.grid(row=1, column=4)
        lbl_hulu_movies.grid(row=2, column=4, sticky="n")
        lbl_amazon_name.grid(row=3, column=0)
        lbl_amazon_seasons.grid(row=4, column=0)
        lbl_amazon_movies.grid(row=5, column=0, sticky="n")
        lbl_youtube_name.grid(row=3, column=1)
        lbl_youtube_seasons.grid(row=4, column=1)
        lbl_youtube_movies.grid(row=5, column=1, sticky="n")
        lbl_prison_name.grid(row=3, column=2)
        lbl_prison_seasons.grid(row=4, column=2)
        lbl_prison_movies.grid(row=5, column=2, sticky="n")
        lbl_hbo_name.grid(row=3, column=3)
        lbl_hbo_seasons.grid(row=4, column=3)
        lbl_hbo_movies.grid(row=5, column=3, sticky="n")
        lbl_tubi_name.grid(row=3, column=4)
        lbl_tubi_seasons.grid(row=4, column=4)
        lbl_tubi_movies.grid(row=5, column=4, sticky="n")

    def update_page_display(self, *ignore):
        self.show = options[self.lbox_options.curselection()[0]]
        self.check_streaming()
        names, scores, pacing_scores, drama_scores = sort_ratings(self.show["houseScores"])
        self.labels = []
        for idx, name in enumerate(names):
            self.labels.append(f"{name} - {scores[idx]}")
        colors = collect_colors(scores)
        total_house_score = sum(scores)
        content_warnings[0] = 0
        content_warnings[1] = 0
        content_warnings[2] = 0
        normal_tags, warning_tags, spoiler_tags = self.sort_tags()
        self.plot_graph(pacing_scores, drama_scores, colors)

        # Get average household score
        if total_house_score > 0:
            avg_house_score = total_house_score / len(scores)
            dc.getcontext().rounding = dc.ROUND_HALF_UP
            avg_house_score = int(dc.Decimal(str(avg_house_score)).quantize(dc.Decimal("1")))
        else:
            avg_house_score = 0

        self.color_stars(self.show["score"], avg_house_score)

        # Toggle display
        if self.show["unairedSeasons"] == 0:
            self.lbl_unaired_seasons["text"] = ""
        else:
            self.lbl_unaired_seasons["text"] = f"Unfinished Seasons: {self.show['unairedSeasons']}"

        self.set_spoiler_label()

        # Update display values
        self.lbl_title["text"] = f"{self.show['romajiTitle']} \u2022 {self.show['englishTitle']} \u2022 {self.show['nativeTitle']}"
        self.lbl_avg_rating["text"] = f"Public score: {self.show['score']}/100"
        self.lbl_house_rating["text"] = f"House score: {avg_house_score}/100"
        self.lbl_cover_image["image"] = convert_image(self.show["coverMed"])
        self.lbl_episodes["text"] = f"Total episodes: {self.show['episodes']}"
        self.lbl_seasons["text"] = f"Seasons: {self.show['seasons']}"
        self.lbl_movies["text"] = f"Movies: {self.show['movies']}"
        self.txt_description["state"] = "normal"
        self.txt_description.delete("1.0", tk.END)
        self.txt_description.insert("1.0", self.show["description"])
        self.txt_description["state"] = "disabled"
        self.lbl_genres_list["text"] = f"{', '.join(self.show['genres'])}"
        self.lbl_tags_list["text"] = f"{', '.join(normal_tags)}"
        self.lbl_warnings_list["text"] = f"{', '.join(warning_tags)}"
        self.lbl_spoiler_tags["text"] = f"{', '.join(spoiler_tags)}"

    def add_options(self):

        dlg_selection = SelectionWindow(self.parent)
        dlg_selection.title("Option Selector")
        dlg_selection.transient(self.parent)
        dlg_selection.grab_set()
        dlg_selection.wait_window()

    def display_all(self):
        house_scores = []
        public_scores = []
        titles = []
        pacing_scores = []
        drama_scores = []
        self.labels = []
        tags = []
        genres = []
        tag_content_labels = []
        tag_frequency_labels = []
        genre_frequency_labels = []
        episodes = 0
        seasons = 0
        movies = 0
        unfinished_seasons = 0
        content_warnings[0:3] = [0, 0, 0]
        dc.getcontext().rounding = dc.ROUND_HALF_UP
        for show in library:
            ratings = [rating for rating in show["houseScores"]]
            names, scores, pacing, drama = sort_ratings(ratings)
            total_house_score = sum(scores)
            total_pacing_score = sum(pacing)
            total_drama_score = sum(drama)
            if total_house_score > 0:
                avg_house_score = total_house_score / len(scores)
                avg_house_score = int(dc.Decimal(str(avg_house_score)).quantize(dc.Decimal("1")))
                avg_pacing_score = total_pacing_score / len(scores)
                avg_pacing_score = int(dc.Decimal(str(avg_pacing_score)).quantize(dc.Decimal("1")))
                avg_drama_score = total_drama_score / len(scores)
                avg_drama_score = int(dc.Decimal(str(avg_drama_score)).quantize(dc.Decimal("1")))
                titles.append(show["defaultTitle"])
                house_scores.append(avg_house_score)
                public_scores.append(show["score"])
                pacing_scores.append(avg_pacing_score)
                drama_scores.append(avg_drama_score)
                self.labels.append(f"{show['defaultTitle']}\n"
                                   f"Public:{show['score']}, House:{avg_house_score}")

                calc_tags = []
                calc_genres = []
                for genre in genres:
                    calc_genres.append(genre["name"])

                for tag in tags:
                    calc_tags.append(tag["name"])

                for tag in show["tags"]:
                    if tag["name"] not in calc_tags:
                        tags.append(tag.copy())

                for genre in show["genres"]:
                    if genre not in calc_genres:
                        genres.append({"name": genre,
                                       "shows": 0})

            episodes += show["episodes"]
            seasons += show["seasons"]
            movies += show["movies"]
            unfinished_seasons += show["unairedSeasons"]

        colors = collect_colors(house_scores)

        for tag in tags:
            tag["rank"] = 0
            tag["shows"] = 0
            for show in library:
                if show["houseScores"] and show["houseScores"][0][1]:
                    for item in show["tags"]:
                        if item["name"] == tag["name"]:
                            tag["shows"] += 1

        for genre in genres:
            for show in library:
                if show["houseScores"] and show["houseScores"][0][1]:
                    for item in show["genres"]:
                        if item == genre["name"]:
                            genre["shows"] += 1

        warning_frequency = []
        tag_frequency = []
        genre_frequency = []
        for i in range(len(titles), 0, -1):
            for tag in tags:
                if tag["shows"] == i:
                    if tag["name"] in mild_warnings or tag["name"] in extreme_warnings:
                        warning_frequency.append(tag)
                    else:
                        tag_frequency.append(tag)
            for genre in genres:
                if genre["shows"] == i:
                    genre_frequency.append(genre)
        for idx, tag in enumerate(tag_frequency):
            if idx <= 20:
                tag_frequency_labels.append(f"{tag['name']}: {tag['shows']}")
        for idx, tag in enumerate(warning_frequency):
            if idx <= 8:
                tag_content_labels.append(f"{tag['name']}: {tag['shows']}")
        for idx, genre in enumerate(genre_frequency):
            if idx <= 9:
                genre_frequency_labels.append(f"{genre['name']}: {genre['shows']}")

        total_score = sum(public_scores)
        avg_public_score = total_score / len(public_scores)
        avg_public_score = int(dc.Decimal(str(avg_public_score)).quantize(dc.Decimal("1")))

        total_house_score = sum(house_scores)
        avg_house_score = total_house_score / len(house_scores)
        avg_house_score = int(dc.Decimal(str(avg_house_score)).quantize(dc.Decimal("1")))

        self.plot_graph(pacing_scores, drama_scores, colors)
        self.color_stars(avg_public_score, avg_house_score)

        self.set_spoiler_label()

        # Update display values
        self.lbl_title["text"] = "Displaying Entire Library"
        self.lbl_avg_rating["text"] = f"Public score: {avg_public_score}/100"
        self.lbl_house_rating["text"] = f"House score: {avg_house_score}/100"
        self.lbl_cover_image["image"] = ""
        self.lbl_episodes["text"] = f"Total episodes: {episodes}"
        self.lbl_seasons["text"] = f"Seasons: {seasons}"
        self.lbl_movies["text"] = f"Movies: {movies}"
        self.lbl_unaired_seasons["text"] = f"Unfinished Seasons: {unfinished_seasons}"
        self.txt_description["state"] = "normal"
        self.txt_description.delete("1.0", tk.END)
        self.txt_description["state"] = "disabled"
        self.lbl_genres_list["text"] = f"{', '.join(genre_frequency_labels)}"
        self.lbl_tags_list["text"] = f"{', '.join(tag_frequency_labels)}"
        self.lbl_warnings_list["text"] = f"{', '.join(tag_content_labels)}"
        self.lbl_spoiler_tags["text"] = f""

    def set_spoiler_label(self):
        if self.spoiler_state.get() == 1:
            self.cbox_spoiler_tags[
                "text"] = f"\u25BC Spoiler Tags: ({content_warnings[0]}, {content_warnings[1]}, {content_warnings[2]})"
        else:
            self.cbox_spoiler_tags[
                "text"] = f"\u25B6 Spoiler Tags: ({content_warnings[0]}, {content_warnings[1]}, {content_warnings[2]})"

    def color_stars(self, score1, score2):
        # TODO: Rename to "get_rating_color" or similar. Only check one score at a time, and rather than setting the
        #   color here, return the color to have it be set back there.
        if score1 >= 85:
            self.lbl_public_star.config(fg="purple")
        elif score1 >= 70:
            self.lbl_public_star.config(fg="blue")
        elif score1 >= 55:
            self.lbl_public_star.config(fg="orange")
        elif score1 >= 1:
            self.lbl_public_star.config(fg="red")
        else:
            self.lbl_public_star.config(fg="black")

        if score2 >= 85:
            self.lbl_house_star.config(fg="purple")
        elif score2 >= 70:
            self.lbl_house_star.config(fg="blue")
        elif score2 >= 55:
            self.lbl_house_star.config(fg="orange")
        elif score2 >= 1:
            self.lbl_house_star.config(fg="red")
        else:
            self.lbl_house_star.config(fg="black")

    def build_graph(self):
        self.graph.grid()  # Adds a grid to the graph- does not add the graph to the Tkinter grid
        self.graph.scatter([50, -50], [50, -50], s=[0, 0])
        self.graph.set_ylabel("< Drama \u2022 Comedy >")
        self.graph.set_xlabel("< Slow Pacing \u2022 Fast Pacing >")

    def plot_graph(self, pacing_scores, drama_scores, colors):
        self.graph.cla()
        self.build_graph()
        self.graph.scatter(pacing_scores, drama_scores, color=colors, picker=True)
        self.graph.figure.canvas.draw_idle()

    def onpick(self, event):
        ind = event.ind
        label_pos_x = event.mouseevent.xdata
        label_pos_y = event.mouseevent.ydata
        offset = 1

        for i in ind:
            label = self.labels[i]
            annotate(
                self.graph,
                label,
                label_pos_x + offset,
                label_pos_y + offset
            )

            self.graph.figure.canvas.draw_idle()

            offset += 3.5

    def toggle_spoilers(self):
        if self.spoiler_state.get() == 1:
            self.lbl_spoiler_tags.grid(row=7, column=0)
            self.cbox_spoiler_tags[
                "text"] = f"\u25BC Spoiler Tags: ({content_warnings[0]}, {content_warnings[1]}, {content_warnings[2]})"
        else:
            self.lbl_spoiler_tags.grid_remove()
            self.cbox_spoiler_tags[
                "text"] = f"\u25B6 Spoiler Tags: ({content_warnings[0]}, {content_warnings[1]}, {content_warnings[2]})"

    def sort_tags(self):
        normal_tags = []
        warning_tags = []
        spoiler_tags = []
        for tag in self.show["tags"]:
            if tag["isMediaSpoiler"]:
                spoiler_tags.append(f"{tag['name']} ({tag['rank']}%)")
                if tag["name"] in extreme_warnings:
                    content_warnings[2] += 1
                elif tag["name"] in mild_warnings:
                    content_warnings[1] += 1
                else:
                    content_warnings[0] += 1
            elif tag["name"] in mild_warnings or tag["name"] in extreme_warnings:
                warning_tags.append(f"{tag['name']} ({tag['rank']}%)")
            else:
                normal_tags.append(f"{tag['name']} ({tag['rank']}%)")

        return normal_tags, warning_tags, spoiler_tags

    def check_streaming(self):
        indices = []
        color = "black"
        for service in self.show["streaming"].items():
            if service[0] == "crunchyroll":
                indices = [27, 28, 29]
                color = "dark orange"
            elif service[0] == "funimation":
                indices = [24, 25, 26]
                color = "purple"
            elif service[0] == "hidive":
                indices = [21, 22, 23]
                color = "dodger blue"
            elif service[0] == "vrv":
                indices = [18, 19, 20]
                color = "gold"
            elif service[0] == "hulu":
                indices = [15, 16, 17]
                color = "lime green"
            elif service[0] == "amazon":
                indices = [12, 13, 14]
                color = "dodger blue"
            elif service[0] == "youtube":
                indices = [9, 10, 11]
                color = "red"
            elif service[0] == "prison":
                indices = [6, 7, 8]
                color = "red"
            elif service[0] == "hbo":
                indices = [3, 4, 5]
                color = "purple"
            elif service[0] == "tubi":
                indices = [0, 1, 2]
                color = "red"

            self.frm_stream_locations.grid_slaves()[indices[1]]["text"] = f"Seasons: {service[1]['seasons']}"
            self.frm_stream_locations.grid_slaves()[indices[0]]["text"] = f"Movies: {service[1]['movies']}"
            if service[1]["seasons"] + service[1]["movies"] == 0:
                for idx in indices:
                    self.frm_stream_locations.grid_slaves()[idx]["fg"] = "gray"
            elif service[1]["seasons"] >= self.show["seasons"] and service[1]["movies"] >= self.show["movies"]:
                self.frm_stream_locations.grid_slaves()[indices[2]]["fg"] = color
                self.frm_stream_locations.grid_slaves()[indices[1]]["fg"] = "black"
                self.frm_stream_locations.grid_slaves()[indices[0]]["fg"] = "black"
            else:
                for idx in indices:
                    self.frm_stream_locations.grid_slaves()[idx]["fg"] = "black"


class SelectionWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.library_var = tk.StringVar(value=library_titles)
        self.options_var = tk.StringVar(value=option_titles)

        # Build main frame
        self.selection_frame = tk.Frame(self)
        btn_confirm = tk.Button(self.selection_frame, text="Confirm choices", command=lambda: self.dismiss_window())
        self.lbox_library = tk.Listbox(self.selection_frame, listvariable=self.library_var)
        self.lbox_selected = tk.Listbox(self.selection_frame, listvariable=self.options_var)
        self.btn_add_option = tk.Button(self.selection_frame, text="Add", command=self.add_to_list)
        self.lbox_library.bind("<Double-1>", lambda x: self.add_to_list())
        self.btn_remove_option = tk.Button(self.selection_frame, text="Remove",
                                           command=lambda: self.remove_from_list(options))
        self.lbox_selected.bind("<Double-1>", lambda x: self.remove_from_list(options))
        self.btn_edit_library = tk.Button(self.selection_frame, text="Edit Entry", command=self.add_to_library)

        # Grid main frame
        self.lbox_library.grid(row=1, column=0, rowspan=4)
        self.lbox_selected.grid(row=1, column=2, rowspan=4)
        self.btn_add_option.grid(row=2, column=1, padx=7, pady=3, sticky="ew")
        self.btn_remove_option.grid(row=3, column=1, padx=7, pady=3, sticky="ew")
        btn_confirm.grid(row=5, column=1, padx=3, pady=3)
        self.btn_edit_library.grid(row=5, column=0, padx=3, pady=3)
        self.selection_frame.grid()

    def add_to_library(self):
        dlg_addition = EditWindow(self.parent)
        dlg_addition.title("Library Editor")
        dlg_addition.transient(self.parent)
        dlg_addition.grab_set()
        dlg_addition.wait_window()

    def add_to_list(self):
        selected = self.lbox_library.curselection()[0]

        if library_titles[selected] not in option_titles:
            options.append(library[selected])
            option_titles.append(library_titles[selected])

        options_var = tk.StringVar(value=option_titles)
        self.lbox_selected["listvariable"] = options_var

    def remove_from_list(self, options_list):
        options_list.pop(self.lbox_selected.curselection()[0])
        option_titles.pop(self.lbox_selected.curselection()[0])

        options_list_var = tk.StringVar(value=option_titles)
        self.lbox_selected["listvariable"] = options_list_var

    def dismiss_window(self):
        self.grab_release()
        self.destroy()
        options_var = tk.StringVar(value=option_titles)
        # TODO: Reinstate if going back to TKinter
        # window.lbox_options["listvariable"] = options_var


class EditWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_show = {}
        self.bind("<Return>", self.update_series)

        # Build main frame
        self.edit_frame = tk.Frame(self)
        self.lbl_id_no = tk.Label(self.edit_frame, text="ID no.")
        self.ent_id_no = tk.Entry(self.edit_frame, width=15)
        btn_confirm_id = tk.Button(self.edit_frame, text="Confirm", command=self.update_series)
        self.lbl_show_name = tk.Label(self.edit_frame)
        btn_confirm_scores = tk.Button(self.edit_frame, text="Confirm", command=self.enter_ratings)
        btn_add_user = tk.Button(self.edit_frame, text="Add User", command=self.add_user)
        btn_update_all = tk.Button(self.edit_frame, text="Update All", command=self.update_all)

        # Build ratings frame
        self.frm_user_ratings = tk.Frame(self.edit_frame)
        lbl_name = tk.Label(self.frm_user_ratings, text="Name")
        lbl_score = tk.Label(self.frm_user_ratings, text="Score")
        lbl_energy = tk.Label(self.frm_user_ratings, text="Energy")
        lbl_drama = tk.Label(self.frm_user_ratings, text="Tone")
        self.adjust_rows()

        # Grid main frame
        self.edit_frame.grid()
        self.lbl_id_no.grid(row=0, column=0)
        self.ent_id_no.grid(row=0, column=1, columnspan=1)
        btn_confirm_id.grid(row=0, column=2, padx=3, pady=3)
        self.edit_frame.rowconfigure(1, minsize=15)
        self.lbl_show_name.grid(row=1, column=0, columnspan=3)
        btn_confirm_scores.grid(row=3, column=1, padx=3, pady=3)
        btn_add_user.grid(row=3, column=0, padx=3, pady=3)
        btn_update_all.grid(row=3, column=2, padx=3, pady=3)

        # Grid ratings frame
        self.frm_user_ratings.grid(row=2, column=0, columnspan=3)
        lbl_name.grid(row=0, column=0)
        lbl_score.grid(row=0, column=1)
        lbl_energy.grid(row=0, column=2)
        lbl_drama.grid(row=0, column=3)

    def update_series(self, *ignore):
        media_id = self.ent_id_no.get()
        self.get_series(media_id)
        if self.current_show["englishTitle"]:
            self.lbl_show_name["text"] = self.current_show["englishTitle"]
        else:
            self.lbl_show_name["text"] = self.current_show["romajiTitle"]
        user_reviews = [rating for rating in self.current_show["houseScores"]]

        self.adjust_rows()

        for row, user in enumerate(user_reviews):
            for col in range(4):
                for widget in self.frm_user_ratings.grid_slaves(row=row+1, column=col):
                    widget["state"] = "normal"
                    widget.delete(0, tk.END)
                    widget.insert(0, user[col])

    def get_series(self, media_id):
        id_var = {"id": media_id}
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
        request = rq.post(collection.url, json={"query": collection.query, "variables": id_var}).json()['data']["Media"]
        if request["format"] == "MOVIE":
            seasonal_data = {
                "total_episodes": 0,
                "seasons": 0,
                "unaired_seasons": 0,
                "movies": 1,
                "sequel": [],
                "streaming": stream_info
            }
        else:
            seasonal_data = {
                "total_episodes": request["episodes"],
                "seasons": 1,
                "unaired_seasons": 0,
                "movies": 0,
                "sequel": [],
                "streaming": stream_info
            }
        seasonal_data = collection.sort_seasonal_data(request, seasonal_data)

        for id in seasonal_data["sequel"]:
            seasonal_data = collection.collect_seasonal_data(id, seasonal_data)

        if request["title"]["english"]:
            title = request["title"]["english"]
        else:
            title = request["title"]["romaji"]

        entry = {
            "id": media_id,
            "romajiTitle": request["title"]["romaji"],
            "englishTitle": request["title"]["english"],
            "nativeTitle": request["title"]["native"],
            "defaultTitle": title,
            "format": request["format"],
            "description": request["description"],
            "episodes": seasonal_data["total_episodes"],
            "seasons": seasonal_data["seasons"],
            "unairedSeasons": seasonal_data["unaired_seasons"],
            "movies": seasonal_data["movies"],
            "coverLarge": request["coverImage"]["extraLarge"],
            "coverMed": request["coverImage"]["large"],
            "coverSmall": request["coverImage"]["medium"],
            "genres": request["genres"],
            "tags": request["tags"],
            "score": request["averageScore"],
            "streaming": seasonal_data["streaming"],
            "houseScores": [["", 0, 0, 0]]
        }

        for show in library:
            if media_id == show["id"]:
                entry["houseScores"] = show["houseScores"]

        self.current_show = entry

    def enter_ratings(self):
        rows = count_rows(self.frm_user_ratings.grid_slaves())

        for row in range(rows):
            for col in range(4):
                for widget in self.frm_user_ratings.grid_slaves(row=row, column=col):
                    if row != 0:
                        if row-1 == len(self.current_show["houseScores"]):
                            self.current_show["houseScores"].append(["", 0, 0, 0])
                        if col == 0:
                            self.current_show["houseScores"][row-1][col] = widget.get()
                            widget["state"] = "disabled"
                        else:
                            self.current_show["houseScores"][row-1][col] = int(widget.get())
                            widget["state"] = "disabled"

        match_found = False
        lib_clone = library.copy()
        for idx, show in enumerate(lib_clone):
            if self.current_show["id"] == show["id"]:
                library[idx] = self.current_show
                match_found = True

        if not match_found:
            alphabetize.insert_alphabetically(self.current_show, library)
            library_titles[0:len(library_titles)] = []
            for show in library:
                library_titles.append(show["defaultTitle"])

        self.lbl_show_name["text"] = "Data Confirmed!"

    def add_user(self):
        rows = count_rows(self.frm_user_ratings.grid_slaves())

        ent_user = tk.Entry(self.frm_user_ratings)
        ent_user.grid(row=rows, column=0, padx=3)
        for col in range(3):
            ent_score = tk.Entry(self.frm_user_ratings, width=5)
            ent_score.grid(row=rows, column=col+1, padx=3)

    def adjust_rows(self):
        for idx, widget in enumerate(self.frm_user_ratings.grid_slaves()):
            if idx < (len(self.frm_user_ratings.grid_slaves()) - 4):
                widget.destroy()
        if self.current_show:
            users = self.current_show["houseScores"]
        else:
            users = []
        for row, user in enumerate(users):

            ent_user = tk.Entry(self.frm_user_ratings)
            ent_user.grid(row=row + 1, column=0, padx=3)
            for col in range(3):
                ent_score = tk.Entry(self.frm_user_ratings, width=5)
                ent_score.grid(row=row + 1, column=col + 1, padx=3)

    def update_all(self):
        lib_clone = library.copy()
        for series in library:
            self.get_series(series["id"])
            for idx, show in enumerate(lib_clone):
                if self.current_show["id"] == show["id"]:
                    library[idx] = self.current_show
                    break
            if len(library) > 90:
                time.sleep(2)
            elif len(library) > 60:
                time.sleep(1.5)
            elif len(library) > 45:
                time.sleep(1)
            print(f"{series['defaultTitle']} updated")


def convert_image(url):
    raw_url = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"})
    raw_image = urllib.request.urlopen(raw_url).read()
    image_data = Image.open(io.BytesIO(raw_image))
    image = ImageTk.PhotoImage(image_data)
    if image not in cover_image:
        cover_image.append(image)

    return image


def count_rows(item):
    rows = 0
    for idx in range(len(item)):
        if idx % 4 == 0:
            rows += 1

    return rows


def annotate(axis, text, x, y):
    text_annotation = Annotation(text, xy=(x, y), xycoords='data')
    axis.add_artist(text_annotation)


def collect_colors(scores):
    colors = []
    for idx, score in enumerate(scores):
        if score > 0:
            if score >= 85:
                colors.append("purple")
            elif score >= 70:
                colors.append("blue")
            elif score >= 55:
                colors.append("orange")
            else:
                colors.append("red")
    return colors


def sort_ratings(ratings):
    scores = []
    names = []
    pacing_scores = []
    drama_scores = []
    for rating in ratings:
        if rating[1] > 0:
            names.append(rating[0])
            scores.append(rating[1])
            pacing_scores.append(rating[2])
            drama_scores.append(rating[3])

    return names, scores, pacing_scores, drama_scores


if __name__ == "__main__":
    application = tk.Tk()
    default_font = fnt.nametofont("TkDefaultFont")
    default_font.configure(size=12)
    window = Root(application)

    application.mainloop()

    upload_data = [mild_warnings, extreme_warnings, library]
    with open("anime_data.json", "w") as anime_data:
        json.dump(upload_data, anime_data, indent=4)
