import random


class Enemy:

    bosses = {}

    @classmethod
    def load_bosses(cls, bosses_data):
        cls.bosses = bosses_data

    def __init__(self, name, hp, attack):

        self.name = name
        self.hp = hp
        self.attack = attack

    # -------------------------
    # RANDOM ENEMY
    # -------------------------
    @staticmethod
    def random_enemy(floor):

        if floor <= 5:

            enemies = [
                Enemy("Goblin", 30, 8),
                Enemy("Skeleton", 40, 10),
                Enemy("Dark Wolf", 50, 12),
                Enemy("Bomber", 20, 20)
            ]

        elif floor <= 15:

            enemies = [
                Enemy("Venom Spider", 45, 14),
                Enemy("Ghoul", 60, 15),
                Enemy("Bone Archer", 55, 16),
                Enemy("Dark Shaman", 70, 18)
            ]

        elif floor <= 25:

            enemies = [
                Enemy("Stone Golem", 120, 18),
                Enemy("Ogre", 140, 20),
                Enemy("Necromancer", 90, 22),
                Enemy("Giant", 100, 15)
            ]

        else:

            enemies = [
                Enemy("Doom Knight", 160, 25),
                Enemy("Abyss Walker", 180, 28)
            ]

        return random.choice(enemies)

    # -------------------------
    # RANDOM BOSS
    # -------------------------
    @classmethod
    def random_boss(cls, player_level):

        if not cls.bosses:
            raise ValueError(
                "Boss data belum dimuat."
            )

        selected = None

        for level_req, boss_data in sorted(
            cls.bosses.items(),
            key=lambda x: int(x[0])
        ):

            if player_level >= int(level_req):
                selected = boss_data

        if selected is None:
            selected = next(
                iter(cls.bosses.values())
            )

        return Boss(
            selected["name"],
            selected["hp"],
            selected["attack"],
            selected["exp_reward"],
            selected["gold_reward"]
        )


class Boss(Enemy):

    def __init__(
        self,
        name,
        hp,
        attack,
        exp_reward,
        gold_reward
    ):

        super().__init__(
            name,
            hp,
            attack
        )

        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

class TheFirstHollow(Enemy):
    def __init__(self):
        super().__init__("The First Hollow", 500, 50)
        self.exp_reward = 1000
        self.gold_reward = 500