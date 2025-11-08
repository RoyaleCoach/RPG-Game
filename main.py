from player import Player
from map import explore, move
from merchant import Merchant
from story.intro_story import intro_story
from story.main_story import main_story
from utils.press_any_key import press_any
from inventory import inventory_check
from utils.text_effect import typewriter

def main():
    print("=== ECHOES OF THE FORGOTTEN DUNGEON ===")

    choice = input("Mulai baru (n) atau lanjutkan (l)? ").lower()
    player = Player.load() if choice == "l" else Player(input("Masukkan nama pemain: "))

    if choice == "n":
        intro_story(player)
    x=0
    while True:
        if x >= 1:
            press_any()
        x=1
        print(x)
        player.show_status()
        action = input("\n[1] Main Story\n[2] Jelajahi dungeon\n[3] Merchant\n[4] Inventory\n[5] Simpan Game\n[0] Keluar\n> ")

        if action == "1":
            story_number = player.story_progress
            main_story(player, story_number)  
        elif action == "2":
            explore(player)
            if player.hp <= 0:
                print("\nGame Over.")
                break
        elif action == "3":
            move()
        elif action == "4":
            merchant = Merchant()
            merchant.trade(player)
        elif action == "5":
            inventory_check(player)
        elif action == "6":
            player.save()
            print("💾 Game disimpan ke save.json")
        elif action == "0":
            print("Simpan Permainan? (y/n)")
            save_choice = input("> ")
            if save_choice == "y" or save_choice == "yes":
                player.save()
            elif save_choice == "n" or save_choice == "no":
                typewriter("Keluar dari permainan", dramatic=True)
                break
            else:
                print("Pilihan tidak valid")
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()
