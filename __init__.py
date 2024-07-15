# A plugin which given a deck and field in config.json, tags each note according to the
# grade level of the kanji, as defined in the official government list
# https://en.wikipedia.org/wiki/List_of_j%C5%8Dy%C5%8D_kanji

# Also adds a hook to apply tags to a note when they are added automatically

# Comments will be detailed because Anki does not provide good plugin documentation,
# and reading others' code is the only way to understand many things.
# I hope my plugin helps you make yours.

from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from anki.cards import *
from . import jouyou_grades  # To import files in the same directory
from anki.hooks_gen import note_will_be_added

user_config = mw.addonManager.getConfig(__name__)  # creates a dictionary from the directory's config.json
possible_tags = ["jouyou_1", "jouyou_2", "jouyou_3", "jouyou_4", "jouyou_5", "jouyou_6", "jouyou_S"]


# ========================
# === HELPER FUNCTIONS ===
# ========================
def apply_tags_to_note(note: anki.notes.Note, needs_flush: bool):
    num_tags = 0
    kanji_field = (note.__getitem__(user_config['field']))
    for character in kanji_field:
        grade_level = jouyou_grades.grades.get(character)
        if grade_level is None:  # kana, non-jouyou, romaji etc
            continue

        num_tags += 1
        note.add_tag("Jouyou_{}".format(grade_level))

    if needs_flush:
        note.flush()  # You must flush each note you affect for changes to stick.
    return num_tags


# Remove all jouyou tags from a note
def remove_jouyou_tags(note: anki.notes.Note):
    for tag in possible_tags:
        note.remove_tag(tag)


# ===================================
# === APPLY TAGS IN DROPDOWN MENU ===
# ===================================
def add_tags_to_all() -> None:
    deck_id = mw.col.decks.id_for_name(
        user_config['deck'])  # camelCase functions are deprecated, but still used in official examples
    cids = mw.col.decks.cids(did=deck_id)  # Card IDs

    num_applied_tags = 0
    num_notes = 0
    for c in cids:
        note = mw.col.get_card(c).note()
        remove_jouyou_tags(note)
        num_applied_tags += apply_tags_to_note(note, needs_flush=True)
        num_notes += 1

    showInfo(f"Deck now has {num_applied_tags} tags applied to {num_notes} notes in \"{user_config['deck']}\".")


# These lines are basically the same as those in https://addon-docs.ankiweb.net/a-basic-addon.html
action = QAction("Apply Jouyou Grade Tags", mw)
qconnect(action.triggered, add_tags_to_all)  # set it to call add_tags when it's clicked
mw.form.menuTools.addAction(action)  # adds it to the tools menu


# ===================================
# === TAG-AT-INSERT FUNCTIONALITY ===
# ===================================

# Required arguments appear as args=[...] in the hook definition
# In this case note_will_be_added within anki/pylib/tools/genhooks.py
def apply_tags_to_new_note(col, note, deck_id):
    apply_tags_to_note(note, needs_flush=False)  # new notes do not exist in the DB so flushing is meaningless.


anki.hooks_gen.note_will_be_added.append(apply_tags_to_new_note)

# EXPERIMENTAL
# =============================
# === CHANGE TAGS ON MODIFY ===
# =============================
# def update_tags_on_modified_note(note: anki.notes.Note):
# print("invoked")
# remove_jouyou_tags(note)  # if a grade S kanji is removed for instance, then the tag will be removed as well.
# apply_tags_to_note(note, needs_flush=True)


# anki.hooks_gen.note_will_flush.append(update_tags_on_modified_note)
