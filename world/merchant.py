import random

class Merchant:
    def __init__(self):
        self.items = {
            "Potion": 10,
            "Sword": 30,
            "Shield": 25,
            "Axe": 50,
            "Armour": 70,
            "Magic Staff": 100
        }

    def show_items(self):
        print("\n🪙 Merchant: Selamat datang, petualang!")
        for i, (item, price) in enumerate(self.items.items(), start=1):
            print(f"[{i}] {item} - {price} gold")
        print("[0] Keluar")

    def trade(self, player):
        self.show_items()
        choice = input("Pilih barang: ")
        if choice == "0":
            print("Merchant: Semoga perjalananmu aman!")
            return
        try:
            item, price = list(self.items.items())[int(choice) - 1]
            if player.gold >= price:
                player.gold -= price
                player.inventory[item] = 1
                print(f"Kamu membeli {item}!")
            else:
                print("Uangmu tidak cukup!")
        except (IndexError, ValueError):
            print("Pilihan tidak valid.")
