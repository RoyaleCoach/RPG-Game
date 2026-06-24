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
                    "Inventory kosong."
                )

            else:

                for item, qty in player.inventory.items():

                    equipped = ""

                    if item == player.weapon:
                        equipped = " [EQUIPPED]"

                    elif item == player.armor:
                        equipped = " [EQUIPPED]"

                    if item in self.weapons:

                        text = (
                            f"- {item} x{qty} "
                            f"(ATK: {self.weapons[item]['attack']})"
                        )

                    elif item in self.potions:

                        text = (
                            f"- {item} x{qty} "
                            f"(Heal: {self.potions[item]['effect']} HP)"
                        )

                    elif item in self.defends:

                        text = (
                            f"- {item} x{qty} "
                            f"(DEF: {self.defends[item]['defense']})"
                        )

                    else:

                        text = (
                            f"- {item} x{qty}"
                        )

                    print(text + equipped)

            print("\n[1] Equip Weapon")
            print("[2] Use Potion")
            print("[3] Equip Armor")
            print("[0] Keluar")

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
                    "Pilihan tidak valid."
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
                "Tidak ada senjata."
            )

            return

        for item in available_weapons:

            print(
                f"- {item} "
                f"(ATK: {self.weapons[item]['attack']})"
            )

        weapon_name = input(
            "\nMasukkan nama senjata: "
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
                "Tidak ada potion."
            )

            return

        for item in available_potions:

            print(
                f"- {item} "
                f"(Heal: {self.potions[item]['effect']} HP)"
            )

        potion_name = input(
            "\nMasukkan nama potion: "
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
                "Tidak ada armor."
            )

            return

        for item in available_armors:

            print(
                f"- {item} "
                f"(DEF: {self.defends[item]['defense']})"
            )

        armor_name = input(
            "\nMasukkan nama armor: "
        ).strip()

        player.equip_defense(
            armor_name
        )