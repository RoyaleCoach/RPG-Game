from core.items import weapons, potions


def inventory_check(player):
    while True:
        print("\n=== INVENTORY ===")

        if not player.inventory:
            print("Inventory kosong.")
        else:
            for item, qty in player.inventory.items():
                if item in weapons:
                    print(
                        f"- {item} x{qty} "
                        f"(Damage: {weapons[item]})"
                    )

                elif item in potions:
                    print(
                        f"- {item} x{qty} "
                        f"(Heal: {potions[item]} HP)"
                    )

                else:
                    print(f"- {item} x{qty}")

        print("\n[1] Equip Weapon")
        print("[2] Gunakan Potion")
        print("[0] Keluar")

        choice = input("> ").strip()

        if choice == "0":
            break
        elif choice == "1":

            print("\n=== SENJATA ===")

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
                    f"(Damage: {weapons[item]})"
                )

            weapon_name = input(
                "\nMasukkan nama senjata: "
            ).strip()

            player.equip_weapon(weapon_name)

        elif choice == "2":
            print("\n=== POTION ===")

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
                    f"(Heal: {potions[item]} HP)"
                )
            potion_name = input(
                "\nMasukkan nama potion: "
            ).strip()

            player.equip_potion(potion_name)

        else:
            print("Pilihan tidak valid.")