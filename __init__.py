# A plugin which given a deck and field in config.json, tags each note according to the
# grade level of the kanji, as defined in the official government list
# https://en.wikipedia.org/wiki/List_of_j%C5%8Dy%C5%8D_kanji

# Also adds a hook to apply tags to a note when they are added automatically

# Comments will be detailed because Anki does not provide good plugin documentation,
# and reading others' code is the only way to understand many things.
# I hope my plugin helps you make yours.

from anki.lang import _
from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from anki.collection import *
# from aqt.qt import debug
from anki.decks import *
from anki.cards import *
from . import jouyou_grades  # To import files in the same directory
from anki.hooks_gen import note_will_be_added

user_config = mw.addonManager.getConfig(__name__)  # creates a dictionary from the directory's config.json


# =================================
# === TOOLBOX APPLY TAGS OPTION ===
# =================================
def add_tags() -> None:
    deck_id = mw.col.decks.id_for_name(
        user_config['deck'])  # camelCase is deprecated, but still used in official examples
    cids = mw.col.decks.cids(did=deck_id)  # Card IDs

    num_applied_tags = 0
    num_notes = 0
    for c in cids:
        note = mw.col.get_card(c).note()
        kanji_field = (note.__getitem__(user_config['field']))
        for character in kanji_field:
            grade_level = jouyou_grades.grades.get(character)
            if grade_level is None:  # kana, non-jouyou, romaji etc
                continue

            num_applied_tags += 1
            note.add_tag("Jouyou_{}".format(grade_level))

        num_notes += 1
        note.flush()  # You must flush each note you affect for changes to stick.

    showInfo(f"Deck now has {num_applied_tags} tags applied to {num_notes} notes in \"{user_config['deck']}\".")


# These lines are basically the same as those in https://addon-docs.ankiweb.net/a-basic-addon.html
action = QAction("Apply Jouyou Grade Tags", mw)
qconnect(action.triggered, add_tags)  # set it to call add_tags when it's clicked
mw.form.menuTools.addAction(action)  # adds it to the tools menu


# ===================================
# === TAG-AT-INSERT FUNCTIONALITY ===
# ===================================

# Required arguments appear as args=[...] in the hook definition
# In this case note_will_be_added within anki/pylib/tools/genhooks.py
def apply_tags_to_new_note(col, note, deck_id):
    kanji_field = note.__getitem__(user_config['field'])
    for character in kanji_field:
        grade_level = jouyou_grades.grades.get(character)
        if grade_level is None:  # kana, non-jouyou, romaji etc
            continue

        note.add_tag("Jouyou_{}".format(grade_level))
    #note.flush()  # No flush necesary, as the note doesn't exist yet


anki.hooks_gen.note_will_be_added.append(apply_tags_to_new_note)

