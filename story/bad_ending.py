from utils.press_any_key import press_any
from utils.text_effect import typewriter
import time

def bad_ending(player):
    typewriter("Aku gagal.")

    typewriter("Gerbang Abadi terbuka sepenuhnya.")

    typewriter("The First Hollow menelan Crystal of Origin.")
    typewriter("Kegelapan menyebar ke seluruh dunia.")

    typewriter("Kota demi kota menghilang.")
    typewriter("Harapan berubah menjadi Hollow baru.")

    typewriter("Dan namaku terlupakan untuk kedua kalinya.")

    typewriter("\nBAD ENDING")
    typewriter("The Cycle Repeats", dramatic=True)
    player.story_progress = 0
    press_any()