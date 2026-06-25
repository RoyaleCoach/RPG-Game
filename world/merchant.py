class Merchant:

    def __init__(self, items):

        self.items_data = items

        weapons = items.get(
            "weapons",
            {}
        )

        potions = items.get(
            "potions",
            {}
        )

        armors = items.get(
            "defends",
            {}
        )

        self.items = {}

        # Weapons
        for item_name, item_data in weapons.items():

            if (
                not item_data.get(
                    "limited",
                    False
                )
                and item_data.get(
                    "price"
                ) is not None
            ):
                self.items[item_name] = (
                    item_data["price"]
                )

        # Potions
        for item_name, item_data in potions.items():

            if (
                not item_data.get(
                    "limited",
                    False
                )
                and item_data.get(
                    "price"
                ) is not None
            ):
                self.items[item_name] = (
                    item_data["price"]
                )

        # Armors
        for item_name, item_data in armors.items():

            if (
                not item_data.get(
                    "limited",
                    False
                )
                and item_data.get(
                    "price"
                ) is not None
            ):
                self.items[item_name] = (
                    item_data["price"]
                )

    # -------------------------
    # SHOW SHOP
    # -------------------------
    def show_items(self):

        print(
            "\n🪙 Merchant: Welcome, traveler!"
        )

        for i, (item, price) in enumerate(
            self.items.items(),
            start=1
        ):
            print(
                f"[{i}] {item} - {price} gold"
            )

        print("[0] Exit")

    # -------------------------
    # BUY ITEM
    # -------------------------
    def trade(self, player):

        while True:

            self.show_items()

            choice = input(
                "\nChoose item: "
            ).strip()

            if choice == "0":

                print(
                    "Merchant: Safe travels!"
                )

                break

            try:

                item, price = list(
                    self.items.items()
                )[int(choice) - 1]

            except (
                IndexError,
                ValueError
            ):

                print(
                    "❌ Invalid choice."
                )

                continue

            if player.gold < price:

                print(
                    "❌ You don't have enough gold!"
                )

                continue

            player.gold -= price

            player.inventory[item] = (
                player.inventory.get(
                    item,
                    0
                ) + 1
            )

            print(
                f"✅ You bought {item}!"
            )