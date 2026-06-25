from utils.press_any_key import press_any
from utils.text_effect import typewriter
import time

def bad_ending(player):
    typewriter("I failed.")

    typewriter("The Eternal Gate fully opens.")

    typewriter("The First Hollow swallows the Crystal of Origin.")
    typewriter("Darkness spreads across the world.")

    typewriter("City by city disappears.")
    typewriter("Hope is turned into new Hollows.")

    typewriter("And my name is forgotten for the second time.")

    typewriter("\nBAD ENDING")
    typewriter("The Cycle Repeats", dramatic=True)
    player.story_progress = 0
    press_any()