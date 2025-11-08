from utils.press_any_key import press_any
from utils.text_effect import typewriter
import time

def good_ending(player):
    typewriter("\n🌅 Cahaya pagi menembus reruntuhan dungeon.", 0.035)
    time.sleep(1)
    typewriter(f"{player.name} berdiri dengan luka, tapi juga dengan kemenangan.", 0.03)
    press_any()
    typewriter("\nKedamaian akhirnya kembali", 0.04, dramatic=True)
    typewriter("Dunia selamat", 0.04)
    time.sleep(1)
    typewriter("\n✨ GOOD ENDING ✨", 0.04)
