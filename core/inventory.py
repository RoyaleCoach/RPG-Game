from core.rarity import get_rarity_label


class Inventory:

    def __init__(self, items):

        self.weapons = items.get(
            "weapons",
            {}
        )

        self.potions = items.get(
            "potions",
            {}
        )

        self.defends = items.get(
            "defends",
            {}
        )

    # -------------------------
    # MAIN INVENTORY MENU
    # -------------------------
    def open(self, player):

        while True:

            print("\n=== INVENTORY ===")

            if not player.inventory:
                print(
                    "Inventory is empty."
                )

            else:

                for item, qty in player.inventory.items():

                    equipped = ""

                    if item == player.weapon:
                        equipped = " [EQUIPPED]"

                    elif item == player.armor:
                        equipped = " [EQUIPPED]"

                    rarity = ""
                    if item in self.weapons:
                        r = self.weapons[item].get("rarity", "Common")
                        rarity = f" {get_rarity_label(r)}"
                        text = (
                            f"- {item}{rarity}\n"
                            f"    ATK +{self.weapons[item]['attack']}"
                        )

                    elif item in self.potions:
                        r = self.potions[item].get("rarity", "Common")
                        rarity = f" {get_rarity_label(r)}"
                        text = (
                            f"- {item}{rarity}\n"
                            f"    Heal: {self.potions[item]['effect']} HP"
                        )

                    elif item in self.defends:
                        r = self.defends[item].get("rarity", "Common")
                        rarity = f" {get_rarity_label(r)}"
                        text = (
                            f"- {item}{rarity}\n"
                            f"    DEF +{self.defends[item]['defense']}"
                        )

                    else:
                        text = (
                            f"- {item} x{qty}"
                        )

                    print(text + equipped)

            print("\n[1] Equip Weapon")
            print("[2] Use Potion")
            print("[3] Equip Armor")
            print("[0] Exit")

            choice = input("> ").strip()

            if choice == "0":
                break

            elif choice == "1":

                self.equip_weapon_menu(
                    player
                )

            elif choice == "2":

                self.use_potion_menu(
                    player
                )

            elif choice == "3":

                self.equip_armor_menu(
                    player
                )

            else:

                print(
                    "Invalid choice."
                )

    # -------------------------
    # EQUIP WEAPON
    # -------------------------
    def equip_weapon_menu(self, player):

        print("\n=== WEAPONS ===")

        available_weapons = [
            item
            for item in player.inventory
            if item in self.weapons
        ]

        if not available_weapons:

            print(
                "No weapons available."
            )

            return

        for item in available_weapons:

            r = self.weapons[item].get("rarity", "Common")
            rarity_label = get_rarity_label(r)
            print(
                f"{rarity_label} {item}\n"
                f"    ATK +{self.weapons[item]['attack']}"
            )

        weapon_name = input(
            "\nEnter weapon name: "
        ).strip()

        player.equip_weapon(
            weapon_name
        )

    # -------------------------
    # USE POTION
    # -------------------------
    def use_potion_menu(self, player):

        print("\n=== POTIONS ===")

        available_potions = [
            item
            for item in player.inventory
            if item in self.potions
        ]

        if not available_potions:

            print(
                "No potions available."
            )

            return

        for item in available_potions:

            r = self.potions[item].get("rarity", "Common")
            rarity_label = get_rarity_label(r)
            print(
                f"{rarity_label} {item}\n"
                f"    Heal: {self.potions[item]['effect']} HP"
            )

        potion_name = input(
            "\nEnter potion name: "
        ).strip()

        player.equip_potion(
            potion_name
        )

    # -------------------------
    # EQUIP ARMOR
    # -------------------------
    def equip_armor_menu(self, player):

        print("\n=== ARMOR ===")

        available_armors = [
            item
            for item in player.inventory
            if item in self.defends
        ]

        if not available_armors:

            print(
                "No armor available."
            )

            return

        for item in available_armors:

            r = self.defends[item].get("rarity", "Common")
            rarity_label = get_rarity_label(r)
            print(
                f"{rarity_label} {item}\n"
                f"    DEF +{self.defends[item]['defense']}"
            )

        armor_name = input(
            "\nEnter armor name: "
        ).strip()

        player.equip_defense(
            armor_name
        )
