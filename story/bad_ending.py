from utils.press_any_key import press_any
from utils.text_effect import typewriter
import time

def bad_ending(player):
    typewriter("""
🌑 Kau menatap kegelapan, lalu tersenyum.
Kau memilih untuk tetap menjadi penjaga baru dungeon ini.
Akhirmu adalah keabadian.
""")
    press_any()