from core.items import weapons, potions, defends

class Merchant:
    def __init__(self):
        self.items = {}

        for item_name, item_data in weapons.items():
            if not item_data["limited"] and item_data["price"] is not None:
                self.items[item_name] = item_data["price"]

        for item_name, item_data in potions.items():
            if not item_data["limited"] and item_data["price"] is not None:
                self.items[item_name] = item_data["price"]

        for item_name, item_data in defends.items():
            if not item_data["limited"] and item_data["price"] is not None:
                self.items[item_name] = item_data["price"]

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

                player.inventory[item] = (
                    player.inventory.get(item, 0) + 1
                )

                print(f"Kamu membeli {item}!")
            else:
                print("Uangmu tidak cukup!")

        except (IndexError, ValueError):
            print("Pilihan tidak valid.")