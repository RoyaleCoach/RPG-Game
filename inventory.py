from items import weapons, potions


def inventory_check(player):
    print("Inventory:")
    for item, qty in player.inventory.items():
        if item in weapons:
            print(f"- {item} x{qty} (Damage: {weapons[item]})")
        elif item in potions:
            print(f"- {item} x{qty} (Heal: {potions[item]} HP)")
        else:
            print(f"- {item} x{qty}")
        print("\n[1] Equip Weapon\n[2] Equip Potion\n[0] Keluar\n")
        inventory_input = input("> ")
        if inventory_input == "1":
            for item, qty in player.inventory.items():
                if item in weapons:
                    print(f"- {item} x{qty} (Damage: {weapons[item]})")
            while True:
                print("\n[0] Keluar\nMasukan nama senjata")
                inventory_input = input("> ")
                if inventory_input == "0": break
                else: player.equip_weapon(player, inventory_input)