import unittest

from core.player import Player
from world.dungeon import Dungeon


class TestDungeon(unittest.TestCase):
    def setUp(self):
        self.player = Player(
            name="TestPlayer",
            hp=100,
            attack=10,
            defense=5,
            gold=50,
            level=1,
            floor=3,
            luck=2,
        )
        self.dungeon = Dungeon()

    def test_event_weights_use_luck(self):
        weights = self.dungeon.build_event_weights(self.player)

        self.assertGreater(weights["battle"], 45)
        self.assertLess(weights["cursed_shrine"], 4)

    def test_treasure_gold_scales_with_floor(self):
        gold_range = self.dungeon.get_treasure_gold_range(self.player)

        self.assertEqual(gold_range, (35, 130))


if __name__ == "__main__":
    unittest.main()
