function toggleSpoilers() {
          if (spoilerCheckbox.checked === true) {
          spoilerTags.setAttribute("style", "display: inline-block");
          } else {
          spoilerTags.setAttribute("style", "display: none");
          }
        }