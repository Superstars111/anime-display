import json
import string


def insert_alphabetically(show, library):
    title_idx = 0
    comp_idx = 0
    show_idx = 0
    title_checked = False
    if show["englishTitle"]:
        show["defaultTitle"] = show["englishTitle"]
    else:
        show["defaultTitle"] = show["romajiTitle"]

    if library:
        is_inserted = False
        while not is_inserted:

            if show_idx == len(library):
                # If you reach the end of the list, put it there
                library.append(show)
                is_inserted = True
                continue

            if not title_checked:
                if len(library[show_idx]["defaultTitle"]) >= 4:
                    if library[show_idx]["defaultTitle"][0:2] == "A ":
                        comp_idx = comp_idx + 2
                    elif library[show_idx]["defaultTitle"][0:4] == "The ":
                        comp_idx = comp_idx + 4

                if len(show["defaultTitle"]) >= 4:
                    if show["defaultTitle"][0:4] == "The ":
                        title_idx = title_idx + 4
                    elif show["defaultTitle"][0:2] == "A ":
                        title_idx = title_idx + 2
                title_checked = True

            if title_idx == len(show["defaultTitle"]):
                # If you've found a title that encompasses this one, put this title right before that one
                library[show_idx:show_idx] = [show]
                is_inserted = True
            elif comp_idx >= len(library[show_idx]["defaultTitle"]):
                library[show_idx+1:show_idx+1] = [show]
                is_inserted = True

            if show["defaultTitle"][title_idx] in (string.punctuation, " "):
                title_idx += 1
                continue
            if library[show_idx]["defaultTitle"][comp_idx] in (string.punctuation, " "):
                comp_idx += 1
                continue

            if show["defaultTitle"][title_idx].lower() > library[show_idx]["defaultTitle"][comp_idx].lower():
                # If you're still ahead of your alphabetic position, check the next item
                show_idx += 1
                title_idx = 0
                comp_idx = 0
                title_checked = False
            elif show["defaultTitle"][title_idx].lower() == library[show_idx]["defaultTitle"][comp_idx].lower():
                title_idx += 1
                comp_idx += 1
            elif show["defaultTitle"][title_idx].lower() < library[show_idx]["defaultTitle"][comp_idx].lower():
                library[show_idx:show_idx] = [show]
                is_inserted = True
    else:
        library.append(show)

    return library


if __name__ == "__main__":

    with open("anime_data.json", "r") as anime_data:
        unordered_library = json.load(anime_data)

    ordered_library = insert_alphabetically(unordered_library)

    with open("anime_data.json", "w") as anime_data:
        json.dump(ordered_library, anime_data, indent=4)
