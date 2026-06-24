from core.player import Player
from core.inventory import inventory_check

# World
from world.map import explore
from world.merchant import Merchant

# Story
from story.intro_story import intro_story
from story.main_story import main_story

# Utils
from utils.press_any_key import press_any
from utils.text_effect import typewriter

from core.version import version, game_name, author

def main():
    print(f"=== {game_name.upper()} ===")
    print(f"Version: {version}")
    print(f"Author: {author}\n")

    choice = None
    while choice not in ["n", "l"]:
        print("Mulai baru (n) atau lanjutkan (l)?")
        choice = input("> ").lower()

    player = Player.load() if choice == "l" else Player(input("Masukkan nama pemain: "))

    if choice == "n":
        intro_story(player)

    def show_main_menu():
        print("\n=== MENU ===")
        print("[1] Main Story")
        print("[2] Jelajahi Dungeon")
        print("[3] Merchant")
        print("[4] Inventory")
        print("[5] Simpan Game")
        print("[0] Keluar")

        return input("> ").strip().lower()

    x=0
    while True:
        if x >= 1:
            press_any()
        x=1

        player.show_status()
        action = show_main_menu()

        if action == "1":
            story_number = player.story_progress
            main_story(player, story_number)  
        elif action == "2":
            explore(player)
            if player.hp <= 0:
                print("\nGame Over.")
                break
        elif action == "3":
            merchant = Merchant()
            merchant.trade(player)
        elif action == "4":
            inventory_check(player)
        elif action == "5":
            player.save()
            print("💾 Game disimpan ke save.json")
        elif action == "0":
            print("Simpan Permainan? (y/n)")
            save_choice = input("> ").lower().strip()
            if save_choice == "y" or save_choice == "yes":
                player.save()
                typewriter("Keluar dari permainan", dramatic=True)
                break
            elif save_choice == "n" or save_choice == "no":
                typewriter("Keluar dari permainan", dramatic=True)
                break
            else:
                print("Pilihan tidak valid")
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()
