from project.models import Show, User, Rating, List, Series
from project import db
import pandas as pd
import json
from project.integrated_functions import update_full_series
from project.standalone_functions import request_show_data
import time

# Temporary file used in development. Should eventually get phased out.


def add_lists():
    for user in db.session.query(User).all():
        if not List.query.filter_by(owner_id=user.id).first():
            seen_list = List(owner_id=user.id, name="Seen")
            to_watch_list = List(owner_id=user.id, name="To Watch")
            partially_seen_list = List(owner_id=user.id, name="Partially Seen")

            db.session.add_all([seen_list, to_watch_list, partially_seen_list])
            print(f"Adding lists for {user.username}")
    db.session.commit()


def update_library():
    for show in db.session.query(Show).all():
        print(f"Updating {show.rj_name}")
        GQL_request = request_show_data(show.anilist_id)
        show.update_entry(GQL_request)
        db.session.commit()
        time.sleep(1)

    print("\n\nUpdate complete")
    # full_data = pd.read_json("project/anime_data.json", typ="series", orient="records")
    # library = full_data[2]
    #
    # for entry in library:
    #     show = Show.query.filter_by(anilist_id=entry["id"]).first()
    #     if not show:
    #         new_show = Show(
    #             en_name=entry["englishTitle"],
    #             rj_name=entry["romajiTitle"],
    #             jp_name=entry["nativeTitle"],
    #             anilist_id=entry["id"]
    #         )
    #         db.session.add(new_show)
    #         print(f"Adding {new_show.en_name}, {new_show.rj_name}")
    #
    # db.session.commit()


def migrate_ratings():
    full_data = pd.read_json("project/anime_data.json", typ="series", orient="records")
    library = full_data[2]

    user = User.query.filter_by(id=6).first()
    seen_list = List.query.filter_by(owner_id=user.id, name="Seen").first()

    for entry in library:
        print(entry["id"])
        show = Show.query.filter_by(anilist_id=entry["id"]).first()
        print(show.rj_name)
        for rating in entry["houseScores"]:
            if rating[0] == "Simon":
                if not Rating.query.filter_by(user_id=user.id, show_id=show.id).first():
                    new_rating = Rating(
                        user_id=user.id,
                        show_id=show.id,
                        score=rating[1],
                        pacing=rating[2],
                        tone=rating[3]
                    )
                    db.session.add(new_rating)
                    seen_list.shows += [show]
                    print(f"{show.en_name}, {show.rj_name} added.")
                else:
                    continue

    db.session.commit()


def migrate_drama_to_tone():
    full_data = pd.read_json("project/anime_data.json", typ="series", orient="records")
    library = full_data[2]

    for user in db.session.query(User).all():
        for entry in library:
            show = Show.query.filter_by(anilist_id=entry["id"]).first()
            rating = Rating.query.filter_by(user_id=user.id, show_id=show.id).first()
            if rating:
                for score in entry["houseScores"]:
                    if score[0] == "Jared" and user.id == 1:
                        rating.tone = score[3]
                    elif score[0] == "Kenan" and user.id == 3:
                        rating.tone = score[3]
                    elif score[0] == "Mom" and user.id == 4:
                        rating.tone = score[3]
                    elif score[0] == "Hannah" and user.id == 5:
                        rating.tone = score[3]
                    elif score[0] == "Simon" and user.id == 6:
                        rating.tone = score[3]
                db.session.commit()


def sort_anilist_data():
    data = pd.read_json("gdpr_data.json")

    with open("gdpr_data.json", "w") as target:
        json.dump(data, target, indent=4)

    # Status: 0 = Currently watching
    # Status: 1 = Want to watch
    # Status: 2 = Completed
    # Status: 3 = Dropped
    # Status: 4 = Paused
    # Status: 5 = Repeating


def transfer_shows_to_series():
    for show in db.session.query(Show).all():
        if show.priority == 1 and show.position == 1:
            print(f"---Transfering {show.rj_name} now---")
            update_full_series(show.anilist_id)
            time.sleep(2)
            db.session.commit()


# if __name__ == "__main__":
#     sort_anilist_data()
