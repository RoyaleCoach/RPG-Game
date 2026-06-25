import random


class Skill:

    def __init__(self, spells=None):
        self.spells = spells or {}

    def get_spell(self, spell_name):
        return self.spells.get(spell_name)

    def get_spells_by_obtain(self, obtain_source):
        return {
            name: data
            for name, data in self.spells.items()
            if data.get("obtain") == obtain_source
        }

    def get_available_spells(self, player):
        return {
            name: self.spells[name]
            for name in player.learned_spells
            if name in self.spells
        }

    def learn_spell(self, player, spell_name):
        if spell_name in player.learned_spells:
            return False

        if spell_name not in self.spells:
            print(f"⚠️ Spell not found: {spell_name}")
            return False

        player.learned_spells.append(spell_name)

        print(
            f"✨ You learned a new spell: {spell_name}!"
        )
        return True

    def learn_random_spell(self, player, obtain_source):
        available = [
            name
            for name, data in self.spells.items()
            if (
                data.get("obtain") == obtain_source
                and name not in player.learned_spells
            )
        ]

        if not available:
            return None

        spell_name = random.choice(available)
        self.learn_spell(player, spell_name)
        return spell_name
