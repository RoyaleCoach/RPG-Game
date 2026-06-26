from utils.press_any_key import press_any
from utils.text_effect import typewriter, dialog_choice
import time


def intro_story(player):
    typewriter(f"\nWelcome, {player.name}\n", 0.04, dramatic=True)
    time.sleep(1)
    typewriter(
        "Hundreds of years ago, the world 'Eidral' was shattered by a ritual that failed to open the 'Eternal Gate'.")
    typewriter("Since then, humanity has lived under the shadow of 'The Hollow', creatures born from leftover emotions and past sins.")
    typewriter("All records of that event were erased, but echoes of that time still linger underground — in The Forgotten Dungeon.", dramatic=True)
    press_any()

    typewriter(
        f"\n{player.name}, a young man with no memory, woke in the ruins of an ancient city. He carried only:")
    typewriter(
        "A broken sword engraved with an ancient phrase: 'Forgive the past, or repeat it.'")
    typewriter(
        "A cracked circular necklace that grows warm whenever he nears something 'that shouldn't be.'")
    press_any()

    typewriter(
        "He did not know who he was, only that a voice in his head whispered:")
    typewriter(
        "'Find the meaning of the Echo. Trust not the light, fear not the dark.'", dramatic=True)

    typewriter("\nYour adventure has only just begun...")
    press_any()
