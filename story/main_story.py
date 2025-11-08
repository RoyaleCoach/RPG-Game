from utils.press_any_key import press_any
from utils.text_effect import typewriter, dialog_choice
from story.good_ending import good_ending
from story.bad_ending import bad_ending
import time

def main_story(player, story_number):
    level_req = 0
    if story_number == 0:
        typewriter("\tHening", dramatic=True)
        typewriter("\tHanya ada gemuruh samar air menetes dari langit-langit batu.",)
        typewriter("\tLalu aku mendengar suara itu lagi — lembut, tapi jauh di dalam kepalaku",dramatic=True)
        time.sleep(1)

        typewriter('Seren: "Lyren... bangunlah.”')

        typewriter("""
                   Aku membuka mata. Dunia di sekitarku berdenyut biru pucat.
                   Lantai berkilau seperti kaca, dan di tengah ruangan,
                   berdiri Eiden — tubuhnya dipenuhi luka, tapi matanya masih menatap penuh tekad ke arah Crystal of Origin.
                   """)
        typewriter("Aku", dramatic=True)
        typewriter("""
                   tidak seharusnya ada di sini.
                   Aku mati di dalam dungeon ini bertahun-tahun lalu.
                   Tapi sesuatu — atau seseorang — memanggilku kembali.
                   """)

        choice = dialog_choice("Suara itu: 'Sekarang... apakah kau ingin keluar dari kegelapan ini?", {
            "1": "Ya, aku ingin bebas.",
            "2": "Tidak, tempat ini sudah menjadi rumahku."
        })
        if choice == "1":
            good_ending(player)
        elif choice == "2":
            bad_ending(player)
    elif story_number == 1:
        level_req = 5
        if player.level == level_req:
            print("=== Pertemuan Kembali ===")
            typewriter("Aku melangkah maju, jari-jariku menyentuh udara yang terasa berat dan dingin.")
            typewriter("Cahaya kristal memantulkan bayanganku di lantai — tapi bukan hanya aku.")
            typewriter("Ada dua wajah.")
            typewriter("Aku(...) dan Seren", dramatic_mid=True)

            typewriter("\nWajahnya sama sepertiku, tapi matanya memantulkan kedamaian yang asing.")

            typewriter("\nEiden: (terkejut) “Lyren...? Tidak... ini tidak mungkin...”")
            typewriter("Aku tersenyum samar. “Mungkin. Tapi seperti halnya kau yang tak pernah menyerah, jiwaku pun menolak hilang begitu saja.”")

            typewriter("\nSeren: (berbisik) “Kau... adalah aku.”")

            typewriter("\nAku menatapnya lama, dan seketika itu aku mengerti.")
            typewriter("Seren bukan orang asing. Ia adalah bagian jiwaku yang diselamatkan Eiden, ketika tubuhku hancur.")
            typewriter("Aku adalah yang tertinggal — bayangan dari dirinya.")
        else: 
            print(f"Level yang dibutuhkan ", {level_req})
            return False
    elif story_number == 2:
        level_req == 10
        if player.level == level_req:
            print("=== Suara yang Memanggil ===")
        else: 
            print(f"Level yang dibutuhkan ", {level_req})
            return False