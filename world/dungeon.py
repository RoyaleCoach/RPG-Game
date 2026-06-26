import random

from core.enemy import Enemy


class Dungeon:

    def __init__(self, combat=None):
        self.combat = combat
        self.last_event = None
        self.event_cooldowns = {}

    # -------------------------
    # MAIN EVENT ROUTER
    # -------------------------
    def random_event(self, player):
        self._tick_cooldowns()

        event_name = self._choose_event(player)

        if event_name is None:
            return

        self.last_event = event_name
        player.last_event = event_name
        self.event_cooldowns[event_name] = 2

        event = getattr(self, event_name)
        event(player)

    def _tick_cooldowns(self):
        for event_name in list(self.event_cooldowns.keys()):
            self.event_cooldowns[event_name] -= 1
            if self.event_cooldowns[event_name] <= 0:
                self.event_cooldowns.pop(event_name, None)

    def _choose_event(self, player):
        weights = self.build_event_weights(player)
        event_names = [
            name for name in weights if name not in self.event_cooldowns]

        if self.last_event in event_names:
            event_names.remove(self.last_event)

        if not event_names:
            return None

        return random.choices(
            event_names,
            weights=[weights[name] for name in event_names],
            k=1
        )[0]

    def build_event_weights(self, player):
        luck_bonus = max(0, player.luck)

        return {
            "battle": 45 + luck_bonus,
            "treasure_room": 15 + luck_bonus * 2,
            "healing_fountain": 10 + luck_bonus,
            "lost_adventurer": 10 + luck_bonus,
            "ancient_statue": 8 + luck_bonus,
            "secret_passage": 5 + luck_bonus,
            "cursed_shrine": max(1, 4 - luck_bonus),
            "gambler": max(1, 3 - luck_bonus),
        }

    def _scaled_exp(self, player, base):
        return base + player.floor * 2 + max(0, player.luck)

    def _scaled_heal(self, player, base):
        return base + player.floor * 2 + player.luck * 2

    def _scaled_damage(self, player, base):
        return base + player.floor * 2 + max(0, player.luck)

    def _scaled_gold(self, player, base):
        return base + player.floor * 3 + player.luck * 2

    def get_treasure_gold_range(self, player):
        return (
            20 + player.floor * 5,
            100 + player.floor * 10
        )

    def _print_room(self, title, description, atmosphere):
        print(f"\n{title}")
        print(description)

        for line in atmosphere:
            print(line)

    def _grant_bonus(self, player, bonus_name):
        if bonus_name == "Skip next battle":
            player.skip_next_battle = True
        elif bonus_name == "Skip trap":
            player.skip_next_trap = True
        elif bonus_name == "Skip boss preparation":
            player.skip_next_boss_preparation = True
        elif bonus_name == "Jump 2 floors":
            player.floor += 2
        else:
            player.inventory[bonus_name] = player.inventory.get(
                bonus_name, 0) + 1

        print(f"✨ Bonus: {bonus_name}")

    # -------------------------
    # BATTLE
    # -------------------------
    def battle(self, player):
        self._print_room(
            "⚔️ Ambush!",
            "You walk into a dusty chamber...",
            [
                "Dark...",
                "Cold...",
                "You hear footsteps...",
                "..."
            ]
        )

        enemy = Enemy.random_enemy(player.floor)
        print(f"A {enemy.name} lunges from the shadows!")

        if self.combat is not None:
            self.combat.fight(player, enemy)
        else:
            print("The air grows tense as battle begins.")

    # -------------------------
    # TREASURE ROOM
    # -------------------------
    def treasure_room(self, player):
        self._print_room(
            "🎁 Treasure Room",
            "A mysterious chest sits in the center.\nWhat will you do?",
            [
                "Dark...",
                "Cold...",
                "A faint glimmer pulses from the chest...",
                "..."
            ]
        )

        choice = input("[1] Open Chest\n[2] Leave\n> ").strip()

        if choice != "1":
            return

        if random.randint(1, 100) <= 20:
            mimic_hp = 50 + player.floor * 10
            mimic_attack = 15 + max(1, player.floor // 2)
            print("😈 It's a Mimic!")

            if self.combat is not None:
                self.combat.fight(player, Enemy(
                    "Mimic", mimic_hp, mimic_attack))
            else:
                print(f"The mimic lunges with {mimic_attack} force.")

            return

        gold = random.randint(
            20 + player.floor * 5,
            100 + player.floor * 10
        )
        player.gold += gold
        player.gain_exp(self._scaled_exp(player, 15))

        print(f"You found {gold} gold!")

        rarity_roll = random.randint(1, 100)
        if player.floor >= 10 and rarity_roll <= 8 + max(0, player.luck):
            self._grant_bonus(player, "Rare Item")
        elif player.floor >= 20 and rarity_roll <= 3 + max(0, player.luck // 2):
            self._grant_bonus(player, "Legendary Item")
        elif random.randint(1, 100) <= 12 + max(0, player.luck):
            bonus = random.choice([
                "Skip next battle",
                "Skip trap",
                "Skip boss preparation",
                "Jump 2 floors"
            ])
            self._grant_bonus(player, bonus)

    # -------------------------
    # HEALING FOUNTAIN
    # -------------------------
    def healing_fountain(self, player):
        self._print_room(
            "💧 Healing Fountain",
            "A crystal stream pours from the stone.\nThe water shimmers with strange light.",
            [
                "Dark...",
                "Cold...",
                "The water whispers your name...",
                "..."
            ]
        )

        choice = input("[1] Drink\n[2] Leave\n> ").strip()

        if choice != "1":
            return

        outcome = random.randint(1, 100)

        if outcome <= 70:
            heal = self._scaled_heal(player, 20)
            player.hp += heal
            player.gain_exp(self._scaled_exp(player, 8))
            print(f"❤️ +{heal} HP")
        elif outcome <= 90:
            print("The fountain is still. Nothing happens.")
        else:
            damage = self._scaled_damage(player, 15)
            player.hp -= damage
            print(f"☠️ Poisoned! -{damage} HP")

    # -------------------------
    # CURSED SHRINE
    # -------------------------
    def cursed_shrine(self, player):
        self._print_room(
            "☠️ Cursed Shrine",
            "An altar of black stone waits in silence.\nYou feel watched.",
            [
                "Dark...",
                "Cold...",
                "A prayer echoes from nowhere...",
                "..."
            ]
        )

        choice = input("[1] Pray\n[2] Leave\n> ").strip()

        if choice != "1":
            return

        outcome = random.randint(1, 3)

        if outcome == 1:
            player.attack += 5 + max(0, player.luck)
            player.hp -= 20 + player.floor * 2
            player.gain_exp(self._scaled_exp(player, 12))
            print(f"+{5 + max(0, player.luck)} ATK, -{20 + player.floor * 2} HP")
        elif outcome == 2:
            gold_gain = self._scaled_gold(player, 100)
            player.gold += gold_gain
            player.gain_exp(self._scaled_exp(player, 10))
            print(f"+{gold_gain} Gold")
        else:
            player.level += 1
            player.gain_exp(self._scaled_exp(player, 20))
            print("📈 Level Up!")

    # -------------------------
    # ANCIENT STATUE
    # -------------------------
    def ancient_statue(self, player):
        self._print_room(
            "🗿 Ancient Statue",
            "An old guardian watches over a cracked pedestal.\nIts eyes seem to glow.",
            [
                "Dark...",
                "Cold...",
                "You hear a slow, ancient hum...",
                "..."
            ]
        )

        offer_cost = 50 + player.floor * 5
        if player.gold < offer_cost:
            print(f"Need {offer_cost} gold.")
            return

        choice = input(f"[1] Offer {offer_cost} Gold\n[2] Leave\n> ").strip()

        if choice != "1":
            return

        player.gold -= offer_cost

        if random.randint(1, 2) == 1:
            player.attack += 2 + max(0, player.luck // 2)
            player.gain_exp(self._scaled_exp(player, 10))
            print(f"⚔️ ATK +{2 + max(0, player.luck // 2)}")
        else:
            player.defense += 2 + max(0, player.luck // 2)
            player.gain_exp(self._scaled_exp(player, 10))
            print(f"🛡️ DEF +{2 + max(0, player.luck // 2)}")

    # -------------------------
    # GAMBLER
    # -------------------------
    def gambler(self, player):
        self._print_room(
            "🎲 Gambler",
            "A crooked dealer waits near a table of cards.\nThe stakes are high.",
            [
                "Dark...",
                "Cold...",
                "A die rolls in the dark...",
                "..."
            ]
        )

        bet_cost = 50 + player.floor * 2
        if player.gold < bet_cost:
            print(f"Need {bet_cost} gold.")
            return

        choice = input(f"[1] Bet {bet_cost} Gold\n[2] Leave\n> ").strip()

        if choice != "1":
            return

        player.gold -= bet_cost

        if random.randint(1, 100) <= 50 + max(0, player.luck):
            player.gold += bet_cost * 2
            player.gain_exp(self._scaled_exp(player, 8))
            print("🎉 You won!")
        else:
            player.gain_exp(self._scaled_exp(player, 3))
            print("😭 You lost!")

    # -------------------------
    # SECRET PASSAGE
    # -------------------------
    def secret_passage(self, player):
        self._print_room(
            "🚪 Secret Passage",
            "A hidden passage opens beneath the stone.\nIt leads deeper into the dungeon.",
            [
                "Dark...",
                "Cold...",
                "You hear footsteps fading behind you...",
                "..."
            ]
        )

        jump_distance = 2 if random.randint(
            1, 100) <= 15 + max(0, player.luck) else 1
        player.floor += jump_distance
        player.gain_exp(self._scaled_exp(player, 6))

        print(f"📈 Floor {player.floor}")

    # -------------------------
    # LOST ADVENTURER
    # -------------------------
    def lost_adventurer(self, player):
        self._print_room(
            "👤 Lost Adventurer",
            "A weary traveler leans against the wall.\nTheir pack is full of supplies.",
            [
                "Dark...",
                "Cold...",
                "A weak voice calls for help...",
                "..."
            ]
        )

        choice = input("[1] Help\n[2] Rob\n[3] Leave\n> ").strip()

        if choice == "1":
            gold_gain = self._scaled_gold(player, 50)
            player.gold += gold_gain
            player.gain_exp(self._scaled_exp(player, 10))
            print(f"+{gold_gain} Gold")

        elif choice == "2":
            gold_gain = random.randint(50, 150) + player.floor * 5
            player.gold += gold_gain
            player.reputation = max(-100, player.reputation - 1)
            player.gain_exp(self._scaled_exp(player, 5))
            print(f"+{gold_gain} Gold")
            print("⚠️ Your reputation has diminished.")
