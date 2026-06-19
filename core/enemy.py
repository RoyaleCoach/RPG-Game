import random

class Enemy:
    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = hp
        self.attack = attack

    @staticmethod
    def random_enemy():
        enemies = [
            Enemy("Goblin", 30, 8),
            Enemy("Skeleton", 40, 10),
            Enemy("Dark Wolf", 50, 12)
        ]
        return random.choice(enemies)
