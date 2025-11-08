import random
from player import Player

def random_puzzle():
    puzzles = [
        ("Apa yang lebih berat, 1 kg kapas atau 1 kg besi?", "sama"),
        ("Saya punya kunci tapi tidak punya pintu. Apakah saya?", "piano"),
        ("Angka apa yang jika dikali 0 tetap 0?", "semua")
    ]
    question, answer = random.choice(puzzles)
    print("\n❓ Teka-teki muncul!")
    print(question)
    guess = input("Jawabanmu: ").lower()
    if answer in guess:
        print("✅ Benar! Kamu berhasil memecahkan teka-teki.")
        return True
    else:
        print("❌ Salah! Kamu kehilangan sedikit HP.")
        return False
