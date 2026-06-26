class SkillTreeMenu:
    """Menu system for viewing and unlocking skills."""

    def __init__(self, skill_tree):
        self.skill_tree = skill_tree

    def show_skill_tree(self, player):
        """Display the skill tree menu."""

        while True:

            print("\n" + "=" * 50)
            print("SKILL TREE")
            print("=" * 50)

            print(
                "\nSkill Points Available: " + str(player.skill_points)
            )

            print("\n[1] View All Skills")
            print("[2] View Unlocked Skills")
            print("[3] View Available Skills")
            print("[4] View Passive Skills")
            print("[5] View Active Skills")
            print("[6] Search Skill")
            print("[0] Back")

            choice = input("\n> ").strip()

            if choice == "1":
                self._display_all_skills(player)

            elif choice == "2":
                self._display_unlocked_skills(player)

            elif choice == "3":
                self._display_available_skills(player)

            elif choice == "4":
                self._display_passive_skills(player)

            elif choice == "5":
                self._display_active_skills(player)

            elif choice == "6":
                self._search_skill(player)

            elif choice == "0":
                break

            else:
                print("Invalid choice.")

    def _display_all_skills(self, player):
        """Display all skills."""

        print("\n=== ALL SKILLS ===\n")

        for idx, node in enumerate(self.skill_tree.get_all_nodes(), 1):

            status = (
                "[UNLOCKED]"
                if node.is_unlocked
                else "[LOCKED]"
            )

            print(
                str(idx) + ". " + node.name +
                " (" + status + ") - Cost: " + str(node.cost)
            )
            print("   " + node.description)
            print()

    def _display_unlocked_skills(self, player):
        """Display unlocked skills."""

        unlocked = self.skill_tree.get_unlocked_skills(player)

        if not unlocked:
            print("\n[WARNING] No skills unlocked yet.")
            return

        print("\n=== UNLOCKED SKILLS ===\n")

        for idx, node in enumerate(unlocked, 1):

            print(str(idx) + ". " + node.name +
                  " (" + node.skill_type.upper() + ")")
            print("   " + node.description)

            if node.spell:
                print("   Spell: " + node.spell)

            print()

    def _display_available_skills(self, player):
        """Display available skills to unlock."""

        available = self.skill_tree.get_available_skills(player)

        if not available:
            print("\n[WARNING] No available skills to unlock.")
            print("Earn more skill points or unlock prerequisites.")
            return

        print("\n=== AVAILABLE SKILLS ===\n")

        for idx, node in enumerate(available, 1):

            print(
                str(idx) + ". " + node.name + " - Cost: " + str(node.cost) +
                " (You have: " + str(player.skill_points) + ")"
            )
            print("   " + node.description)

            if node.prerequisites:
                print(
                    "   Prerequisites: " + ", ".join(node.prerequisites)
                )

            print()

        choice = input("Choose skill to unlock (0 to skip): ").strip()

        if choice.isdigit() and 0 < int(choice) <= len(available):

            selected_skill = available[int(choice) - 1]

            self.skill_tree.unlock_skill(
                player,
                selected_skill.id
            )

    def _display_passive_skills(self, player):
        """Display passive skills."""

        passives = self.skill_tree.get_passive_skills()

        if not passives:
            print("\n[WARNING] No passive skills available.")
            return

        print("\n=== PASSIVE SKILLS ===\n")

        for idx, node in enumerate(passives, 1):

            status = (
                "[OK]"
                if node.is_unlocked
                else "[X]"
            )

            print(
                str(idx) + ". [" + status + "] " +
                node.name + " - Cost: " + str(node.cost)
            )
            print("   " + node.description)

            if node.effects:
                print("   Effects: " + str(node.effects))

            print()

    def _display_active_skills(self, player):
        """Display active skills."""

        actives = self.skill_tree.get_active_skills()

        if not actives:
            print("\n[WARNING] No active skills available.")
            return

        print("\n=== ACTIVE SKILLS ===\n")

        for idx, node in enumerate(actives, 1):

            status = (
                "[OK]"
                if node.is_unlocked
                else "[X]"
            )

            print(
                str(idx) + ". [" + status + "] " +
                node.name + " - Cost: " + str(node.cost)
            )
            print("   " + node.description)

            if node.spell:
                print("   Spell: " + node.spell)

            print()

    def _search_skill(self, player):
        """Search for a skill."""

        query = input("\nSearch skill by name: ").strip().lower()

        results = [
            node
            for node in self.skill_tree.get_all_nodes()
            if query in node.name.lower()
        ]

        if not results:
            print("\n[WARNING] No skills found matching '" + query + "'")
            return

        print("\n=== SEARCH RESULTS ===\n")

        for node in results:

            status = (
                "[UNLOCKED]"
                if node.is_unlocked
                else "[LOCKED]"
            )

            print(node.name + " (" + status + ") - Cost: " + str(node.cost))
            print(node.description)

            if node.prerequisites:
                print(
                    "Prerequisites: " + ", ".join(node.prerequisites)
                )

            print()
