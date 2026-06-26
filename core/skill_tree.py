class SkillNode:
    """Represents a single node in the skill tree."""

    def __init__(self, node_data):

        self.id = node_data.get("id", "unknown")
        self.name = node_data.get("name", "Unknown Skill")
        self.skill_type = node_data.get("type", "active")
        self.cost = node_data.get("cost", 0)
        self.description = node_data.get("description", "")
        self.prerequisites = node_data.get("prerequisites", [])
        self.effects = node_data.get("effects", {})
        self.spell = node_data.get("spell", None)
        self.is_unlocked = False

    def can_unlock(self, player):
        """Check if player can unlock this skill."""

        if self.is_unlocked:
            return False

        if player.skill_points < self.cost:
            return False

        # Check prerequisites
        for prereq in self.prerequisites:
            if prereq not in player.unlocked_skills:
                return False

        return True

    def to_dict(self):
        """Serialize node state."""
        return {
            "id": self.id,
            "is_unlocked": self.is_unlocked
        }

    def __repr__(self):
        status = "✓" if self.is_unlocked else "✗"
        return f"[{status}] {self.name} (Cost: {self.cost})"


class SkillTree:
    """Manages the skill tree system."""

    def __init__(self, skill_tree_data=None):

        self.nodes = {}
        self.skill_tree_data = skill_tree_data or {}

        self._build_tree()

    def _build_tree(self):
        """Build skill tree from data."""

        for node_id, node_data in self.skill_tree_data.get(
            "skill_nodes",
            {}
        ).items():

            self.nodes[node_id] = SkillNode(node_data)

    def get_node(self, node_id):
        """Get a skill node by ID."""
        return self.nodes.get(node_id)

    def get_all_nodes(self):
        """Get all skill nodes."""
        return self.nodes.values()

    def get_active_skills(self):
        """Get all active skill nodes."""
        return [
            node
            for node in self.nodes.values()
            if node.skill_type == "active"
        ]

    def get_passive_skills(self):
        """Get all passive skill nodes."""
        return [
            node
            for node in self.nodes.values()
            if node.skill_type == "passive"
        ]

    def get_available_skills(self, player):
        """Get skills player can unlock."""
        return [
            node
            for node in self.nodes.values()
            if node.can_unlock(player)
        ]

    def get_unlocked_skills(self, player):
        """Get skills player has unlocked."""
        return [
            self.nodes[skill_id]
            for skill_id in player.unlocked_skills
            if skill_id in self.nodes
        ]

    def unlock_skill(self, player, skill_id):
        """Unlock a skill for the player."""

        node = self.get_node(skill_id)

        if node is None:
            print("[WARNING] Skill not found: " + skill_id)
            return False

        if not node.can_unlock(player):
            print("[WARNING] Cannot unlock " + node.name)
            return False

        # Deduct skill points
        player.skill_points -= node.cost

        # Mark as unlocked
        node.is_unlocked = True
        player.unlocked_skills.append(skill_id)

        # Apply passive effects
        if node.skill_type == "passive":
            self._apply_passive_effects(player, node)

        # Learn associated spell
        if node.spell is not None:
            player.learned_spells.append(node.spell)

        print("[UNLOCKED] " + node.name + "!")

        return True

    def _apply_passive_effects(self, player, node):
        """Apply passive skill effects to player."""

        for effect_key, effect_value in node.effects.items():

            if effect_key == "max_mana":
                player._max_mana_bonus = (
                    player._max_mana_bonus + effect_value
                )

            elif effect_key == "attack":
                player._base_attack += effect_value

            elif effect_key == "defense":
                player._base_defense += effect_value

    def get_skill_prerequisites(self, skill_id):
        """Get prerequisites for a skill."""

        node = self.get_node(skill_id)

        if node is None:
            return []

        return node.prerequisites

    def to_dict(self):
        """Serialize all unlocked skills."""
        return {
            node_id: node.to_dict()
            for node_id, node in self.nodes.items()
        }
