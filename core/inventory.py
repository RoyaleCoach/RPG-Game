from core.items import weapons, potions, defends


def inventory_check(player):
    while True:
        print("\n=== INVENTORY ===")

        if not player.inventory:
            print("Inventory kosong.")

        else:
            for item, qty in player.inventory.items():

                equipped = ""

                if item == player.weapon:
                    equipped = " [EQUIPPED]"

                elif item == player.armor:
                    equipped = " [EQUIPPED]"

                if item in weapons:
                    text = (
                        f"- {item} x{qty} "
                        f"(ATK: {weapons[item]['attack']})"
                    )

                elif item in potions:
                    text = (
                        f"- {item} x{qty} "
                        f"(Heal: {potions[item]['effect']} HP)"
                    )

                elif item in defends:
                    text = (
                        f"- {item} x{qty} "
                        f"(DEF: {defends[item]['defense']})"
                    )

                else:
                    text = f"- {item} x{qty}"

                print(text + equipped)

        print("\n[1] Equip Weapon")
        print("[2] Use Potion")
        print("[3] Equip Armor")
        print("[0] Keluar")

        choice = input("> ").strip()

        if choice == "0":
            break

        elif choice == "1":

            print("\n=== WEAPONS ===")

            available_weapons = [
                item
                for item in player.inventory
                if item in weapons
            ]

            if not available_weapons:
                print("Tidak ada senjata.")
                continue

            for item in available_weapons:
                print(
                    f"- {item} "
                    f"(ATK: {weapons[item]['attack']})"
                )

            weapon_name = input(
                "\nMasukkan nama senjata: "
            ).strip()

            player.equip_weapon(weapon_name)

        elif choice == "2":

            print("\n=== POTIONS ===")

            available_potions = [
                item
                for item in player.inventory
                if item in potions
            ]

            if not available_potions:
                print("Tidak ada potion.")
                continue

            for item in available_potions:
                print(
                    f"- {item} "
                    f"(Heal: {potions[item]['effect']} HP)"
                )

            potion_name = input(
                "\nMasukkan nama potion: "
            ).strip()

            player.equip_potion(potion_name)

        elif choice == "3":

            print("\n=== ARMOR ===")

            available_armors = [
                item
                for item in player.inventory
                if item in defends
            ]

            if not available_armors:
                print("Tidak ada armor.")
                continue

            for item in available_armors:
                print(
                    f"- {item} "
                    f"(DEF: {defends[item]['defense']})"
                )

            armor_name = input(
                "\nMasukkan nama armor: "
            ).strip()

            player.equip_defense(armor_name)

        else:
            print("Pilihan tidak valid.")