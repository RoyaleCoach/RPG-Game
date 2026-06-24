import random

class Enemy:
    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = hp
        self.attack = attack

    @staticmethod
    def random_enemy(floor):
        if floor <= 3:
            enemies = [
                Enemy("Goblin", 30, 8),
                Enemy("Skeleton", 40, 10),
                Enemy("Dark Wolf", 50, 12),
                Enemy("Bomber", 20, 20)
            ]

        elif floor <= 6:
            enemies = [
                Enemy("Venom Spider", 45, 14),
                Enemy("Ghoul", 60, 15),
                Enemy("Bone Archer", 55, 16),
                Enemy("Dark Shaman", 70, 18)
            ]

        elif floor <= 10:
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