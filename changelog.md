# Changelog

---

## [0.1.0] - 2025-12-20

### Added

- Save/Load System
- Inventory
- Merchant
- Story Introduction
- Text Effects
- Cross-Platform Keyboard Input

---

## [0.1.1] - 2026-06-20

### Fixed

- Folder Structure
- Import Functions
- Save/Load Reliability
- Player Management
- Input Validation

---

## [0.1.2] - 2026-06-24

### Added

- Expanded Enemy Roster
- Enemy Stat Balancing
- New Dungeon Encounters
- Improved Combat Variety

---

## [0.1.3] - 2026-06-24

### Added

- Expanded Item Collection
- Weapon Progression System
- Armor Equipment System
- Potion Variety
- Item Rarity System
- Limited (Quest-Exclusive) Items
- Merchant Inventory Rework

---

## [0.1.4] - 2026-06-24

### Added

- Quest System
- Quest Board
- Quest Progress Tracking
- Quest Completion Rewards
- Quest-Exclusive Item Rewards
- Enemy Kill Tracking
- Puzzle Completion Tracking
- Automatic Quest Completion Check
- Integration Between Quests and Limited Items

---

## [0.1.4.1] - 2026-06-24

### New Features

- Quest Progress Tracking System
- Dynamic Quest Completion Rewards
- Floor Progression System
- Equipment Status Indicator ([EQUIPPED])

### Gameplay Changes

- Defense is now consumed during battle instead of remaining static
- Battle UI now shows current defense value
- Floor increases every 3 enemy victories

### Refactoring

- Quest objectives now use type/target metadata
- Simplified quest progress and completion logic
- Improved maintainability for future quest additions

### Fixes

- Fixed quest progress not being displayed
- Fixed floor progression not being linked to quest requirements

---

## [0.2.0] - 2026-06-24

### Added

- Dungeon Event System
- Treasure Room Event
- Healing Fountain Event
- Cursed Shrine Event
- Ancient Statue Event
- Gambler Event
- Secret Passage Event
- Lost Adventurer Event
- Elite Enemy Encounters
- Mimic Chest Encounters
- Random Event Generation
- Event-Based Rewards and Penalties

### Gameplay Changes

- Dungeon exploration now includes random non-combat encounters
- Players can obtain gold, items, stat bonuses, or penalties through events
- Secret Passages can advance floor progression
- Some events introduce risk-versus-reward decisions

### Improved

- Dungeon variety and replayability
- Exploration progression system
- Reward distribution outside of combat

---

## [0.2.1] - 2026-06-25

### Added

- Boss Enemy System
- Dedicated Boss Class
- Level-Based Boss Scaling
- Boss Reward System (EXP & Gold)
- Boss Data Configuration via Dictionary
- Automatic Boss Encounters

### Gameplay Changes

- Bosses now grant significantly higher rewards than normal enemies
- Boss difficulty now scales with player progression
- Enemy and Boss systems are now separated for easier balancing
- Improved dungeon progression with milestone encounters
- Boss battle is triggered every 3 dungeon expeditions
- Boss encounters act as progression milestones

### Refactoring

- Introduced reusable Boss inheritance from Enemy
- Centralized boss definitions in `enemy.py`
- Improved combat reward handling for different enemy types

---

## [0.3.0] - 2026-06-25

### Added

- JSON-Based Data System
- DataLoader Utility
- `items.json`
- `quests.json`
- `bosses.json`
- `version.json`
- Dynamic Version Loading
- External Game Configuration Support
- Merchant Item Loading From JSON
- Boss Loading From JSON
- Item Database Architecture

### Refactoring

- Migrated Items from Python dictionaries to JSON
- Migrated Quests from Python dictionaries to JSON
- Migrated Bosses from Python dictionaries to JSON
- Refactored Inventory to use item database
- Refactored Merchant to use centralized item data
- Refactored Quest System to use loaded quest data
- Refactored Boss System to use loaded boss data
- Refactored Game Initialization Flow
- Implemented Dependency Injection between systems
- Reduced hardcoded game content

### Improved

- Easier balancing and content editing
- Better separation between code and game data
- Improved maintainability
- Improved scalability for future content updates
- Improved project organization

---

## [0.3.1] - 2026-06-25

### Added

- Save Directory Support
- Automatic Save Folder Creation
- PyInstaller-Friendly Path Handling
- Centralized Version Information Display
- Runtime Data Reload Support

### Fixed

- Save/Load Initialization Issues
- Merchant Constructor Dependency Errors
- Boss Loading Errors
- Item Lookup After JSON Migration
- Data File Path Resolution
- Save File Location Handling
- Version Data Loading
- Multiple Dependency Injection Issues
- Inventory Data Access Errors

### Refactoring

- Improved Save System Architecture
- Improved Data Loading Reliability
- Simplified System Initialization Order
- Standardized Access to Game Data
- Cleaned Up Legacy Hardcoded References

### Technical

- Prepared project for executable distribution
- Improved compatibility with packaged builds
- Centralized game content management
- Established foundation for future modding support

---

## [0.3.2] - 2026-06-25

### Added

- In-Battle Potion Usage
- Combat Heal Action
- Potion Selection During Battle
- Case-Insensitive Equipment Selection
- Case-Insensitive Potion Usage
- Equipment Validation Improvements

### Gameplay Changes

- Players can now consume potions directly during combat
- Healing is now available as a dedicated battle action
- Weapon, Armor, and Potion names are no longer case-sensitive
- Equipment and consumable selection is more user-friendly

### Improved

- Inventory interaction flow
- Combat usability and survivability
- Item lookup reliability
- User input handling for equipment and consumables

### Fixed

- Equipment selection failing due to letter case mismatch
- Potion usage lookup inconsistencies
- Invalid item name recognition issues
- Inventory item validation edge cases

### Refactoring

- Unified item name matching logic across weapons, armor, and potions
- Reduced duplicate item validation code
- Improved separation between combat logic and item data access

---

## [0.4.0] - 2026-06-26

### Added

- Main Story Chapter 1–7
- Story progression system based on player level
- New characters: Lyren, Seren, Eiden, Echo, and The First Hollow
- Crystal of Origin storyline
- Final Choice event
- The First Hollow final boss battle
- Story-based level requirements
- Narrative dialogue and cutscene sequences

### Changed

- Improved story pacing and progression
- Refined dungeon lore and worldbuilding
- Integrated story progression with player save data

### Fixed

- Story progression tracking
- Chapter unlock consistency
- Final battle and ending flow

---

## [0.5.0] - 2026-06-26

### Added

- Multiple Ending System
- Good Ending: Echoes of Redemption
- Bad Ending: The Cycle Repeats
- Final decision event with meaningful consequences
- The First Hollow final confrontation
- Ending paths based on player choices and battle outcome

### Changed

- Reworked final chapter flow
- Improved narrative impact of player decisions
- Enhanced story conclusion and character arcs

### Fixed

- Final boss progression logic
- Ending trigger conditions
- Story completion flow

---

## [0.5.1] - 2026-06-26

### Added

- English localization for in-game text, menus, and story
- Translated story scripts, UI prompts, README, and supporting utilities

### Changed

- Default language set to English across the codebase

### Fixed

- Corrected various untranslated prompts and inconsistent messages

---

## [0.6.0] - 2026-06-26

### Added

- Spell System with Skill Management
- Mana resource system for players (scales with level)
- Player spell learning and tracking (learned_spells)
- Spell casting in combat as a dedicated battle action
- Spell effect system (damage, healing, buff types)
- Mana cost enforcement and validation
- Dynamic spell availability based on learned spells
- Spell-to-effect resolution with type-based handling
- Persistent spell state in save/load system
- Integration with JSON-based spell data from `spells.json`

### Gameplay Changes

- Players now gain mana pool that regenerates on level-up
- Combat offers four actions: attack, defend, heal (potions), and **spell**
- Spells consume mana and produce varied effects (damage enemies, heal self, boost defense)
- Spells are learned progressively throughout gameplay
- Initial player setup now includes a starter spell (Icicle)
- Spell descriptions are displayed dynamically during combat

### Improved

- Combat depth and strategic variety
- Player progression through spell acquisition
- Combat UI now displays current mana pool alongside HP
- Spell selection menu shows mana costs and spell types
- Effect application based on spell metadata

### Technical

- Created `Skill` class for spell management and lookup
- Enhanced `Player` class with mana property and spell tracking
- Rewrote `Combat.fight()` to support spell action handling
- Implemented `apply_spell_effect()` for flexible spell type processing
- Updated `SaveSystem` to persist mana and learned_spells on save/load
- Established foundation for future spell balancing and spell trees

---

## [0.6.1] - 2026-06-26

### Added

- Logging System
- Centralized Game Logger
- Combat Event Logging
- Save/Load Activity Logging
- Error Logging Support
- Log File Output (`logs/game.log`)
- Unit Testing Framework
- Player System Tests
- Combat System Tests
- Inventory System Tests
- Save/Load System Tests

### Improved

- Easier debugging and issue tracking
- Improved reliability of core gameplay systems
- Better visibility into runtime events and errors
- Safer future refactoring through automated tests

### Technical

- Introduced Python `logging` module integration
- Added structured log messages for major game events
- Established automated test suite using `unittest`
- Created foundation for Continuous Integration (CI)
- Improved maintainability and code quality assurance

### Refactoring

- Replaced selected debug `print()` statements with logger calls
- Standardized system event reporting
- Separated runtime diagnostics from gameplay output

---

## [0.7.0] - 2026-06-26

### Added

- Comprehensive Skill Tree System
- SkillNode class for individual skill management
- SkillTree class for skill hierarchy and progression
- SkillTreeMenu class for interactive UI
- Skill Points earned on level-up (1 per level)
- Player skill_points and unlocked_skills tracking
- Skill Tree data architecture (`skill_tree.json`)
- JSON-based skill configuration system
- Two skill types: Active Skills (spells) and Passive Skills (stat bonuses)
- Skill prerequisites and unlock validation
- Passive skill effects (mana bonus, attack bonus, defense bonus)
- Skill Tree Menu with multiple display modes:
  - View All Skills
  - View Unlocked Skills
  - View Available Skills to Unlock
  - View Passive/Active Skills Separately
  - Search Skills by Name
- Dynamic skill availability based on prerequisites
- Skill cost system (variable SP cost per skill)
- Spell integration with skill tree (unlocking skills teaches spells)

### Gameplay Changes

- Players earn 1 Skill Point per level
- New players start with 1 Skill Point and can immediately unlock skills
- Skill Points can be spent to unlock new spells or passive abilities
- Passive skills grant permanent stat bonuses
- Max Mana can be increased through "Mana Mastery" passive skill
- Attack and Defense can be improved through passive skills
- Skill prerequisites prevent skill spam and encourage meaningful progression
- Skill Tree access available from main menu

### Progression Example

```
Magic Apprentice (Base Passive, Cost: 0)
├── Fireball (Cost: 1, Requires: Magic Apprentice)
│   └── Flame Burst (Cost: 2, Requires: Fireball)
│       └── Inferno (Cost: 3, Requires: Flame Burst)
├── Ice Shard (Cost: 1, Requires: Magic Apprentice)
│   └── Frost Lance (Cost: 2, Requires: Ice Shard)
│       └── Absolute Zero (Cost: 3, Requires: Frost Lance)
└── Mana Mastery (Passive, Cost: 2)
```

### Improved

- Character progression depth and replayability
- Strategic choice in skill allocation
- Long-term progression goals beyond level grinding
- Modular skill system for easy content expansion
- Save/Load persistence for skill tree state

### Technical

- Created `core/skill_tree.py` with SkillNode and SkillTree classes
- Created `core/skill_tree_menu.py` for interactive UI
- Updated `Player` class with skill point tracking
- Added `_max_mana_bonus` property for skill effects
- Updated `DataLoader` to load skill tree JSON
- Integrated skill tree into Game initialization
- Enhanced `SaveSystem` to persist skill_points and unlocked_skills
- Updated `gain_exp()` to award skill points on level-up

### Refactoring

- Separated skill tree logic into dedicated modules
- Established foundation for future skill expansions
- Improved Player class for stat bonus management
- Created modular menu system for UI flexibility

### Fixes

- Player status now displays available Skill Points
- Proper save/load of skill progression
- Menu system updated to accommodate new Skill Tree menu option

---

## [0.7.1] - 2026-06-26

### Improved

- Rebalanced dungeon event probabilities.
- Added floor-based scaling for dungeon rewards and encounters.
- Enhanced event descriptions for better immersion.
- Improved risk-versus-reward mechanics across dungeon events.
- Expanded treasure rewards with more varied loot.
- Prevented repetitive dungeon events from occurring consecutively.
- Refined dungeon UI and event presentation.

### Fixed

- Fixed inconsistencies in dungeon event outcomes.
- Improved overall dungeon system stability and gameplay flow.

---

## [0.7.2] - 2026-06-26

### Added

- `game_context.py` to centralize shared game state and systems.
- `game_menu.py` to separate main menu configuration and actions.

### Improved

- Polished `game.py` architecture for better readability and maintainability.
- Simplified game initialization flow.
- Reduced coupling between game systems.
- Improved dependency management through `GameContext`.
- Enhanced menu organization and extensibility.

### Refactoring

- Moved shared game state into `GameContext`.
- Separated menu logic from the main game loop.
- Encapsulated player initialization responsibilities.
- Reduced direct dependencies inside `Game`.
- Improved overall project structure following the Single Responsibility Principle (SRP).

---

## [0.8.0] - 2026-06-27

### Added

- Added **Critical Hit** system with configurable `critical_chance` and `critical_multiplier` stats.
- Added **Accuracy** stat to increase minimum damage while preserving maximum damage.
- Added **Dodge** mechanic that allows entities to completely avoid incoming attacks.
- Added reusable **Status Effect** framework with lifecycle hooks (`on_apply`, `tick`, and `on_expire`).
- Added built-in status effects:
  - Burn
  - Poison
  - Bleed
  - Freeze
  - Stun
  - Regeneration

- Added spell-to-status-effect mapping for automatic effect application.
- Added **MultiphaseBoss** system supporting multiple combat phases.
- Added shared combat helper functions for damage calculation and dodge resolution.

### Changed

- Refactored combat damage calculation to support Critical Hits and Accuracy.
- Improved enemy AI with weighted decision making.
- Enemies can now:
  - Attack
  - Cast spells
  - Defend
  - Dodge

- Bosses now transition between multiple phases with unique stats and abilities.
- Combat now processes active status effects at the beginning of each turn.
- Player and Enemy now share common combat mechanics to reduce duplicated logic.
- Save/Load system now supports the following new player stats:
  - `critical_chance`
  - `critical_multiplier`
  - `accuracy`
  - `dodge`

### Fixed

- Improved combat consistency by reducing extreme low-damage rolls through the Accuracy system.
- Prevented enemies from repeatedly using Dodge by introducing a cooldown.
- Ensured older save files remain compatible by automatically applying default values for newly added stats.

### Technical

- Introduced a modular status effect architecture that allows new effects to be added without modifying the combat engine.
- Improved extensibility for future spells, bosses, and enemy behaviors.
- Simplified combat logic through reusable helper methods and reduced code duplication.

---

## [0.8.1] - 2026-06-28

### Changed

- Reworked the **Defend** mechanic into a secondary health layer.
- Defense points are now consumed before HP when taking damage.
- Removed the **Defend** action from the player's turn.
- Updated combat flow so defensive durability is handled automatically during damage calculation.
- Improved combat balance by making defensive stats more meaningful throughout battles.

### Fixed

- Fixed an issue where only enemies could successfully use the Dodge mechanic.
- Players can now correctly dodge incoming attacks based on their `dodge` stat.
- Fixed damage handling to properly deplete Defense before reducing HP.
- Improved combat consistency between Player and Enemy damage resolution.

### Technical

- Refactored the damage pipeline to prioritize Defense before Health.
- Unified dodge resolution for both Player and Enemy using the shared combat logic.
- Simplified combat calculations by removing the legacy player Defend action while preserving defensive gameplay.

---

## [0.8.2] - 2026-06-28

### Added

- Added **SQLite** backend support for the Save/Load system.
- Added automatic database initialization and schema creation on first launch.
- Added structured database storage for player progress and game data.

### Changed

- Replaced the JSON-based Save/Load system with **SQLite** for improved reliability and scalability.
- Refactored the SaveSystem into a modular architecture with separated responsibilities.
- Improved data persistence by storing game state in normalized database tables instead of a single JSON file.
- Updated save handling to use reusable repository components for different game systems.

### Fixed

- Improved save consistency by using database transactions during save operations.
- Reduced the risk of save corruption caused by interrupted writes.
- Improved compatibility for future game features through a more extensible storage architecture.

### Technical

- Introduced a dedicated database layer for SQLite connection and query management.
- Separated database schema initialization from save/load logic.
- Reduced code duplication by centralizing common database operations.
- Improved maintainability through repository-based data access and modular SaveSystem components.

---

## [0.8.3] - 2026-06-29

### Fixed

- Fixed `execute_non_query` not correctly distinguishing between single-tuple params (`conn.execute`) and list-of-tuples params (`conn.executemany`), which caused `ProgrammingError` on batch inserts.
- Fixed `save_active_quests` and `save_completed_quests` sending individual tuples instead of batch lists, resulting in incomplete quest saves.
- Fixed stale `__pycache__` bytecode causing the game to run old debug-heavy code even after source files were cleaned.

### Changed

- Removed all debug `print()` statements from the entire `core/savesystem/` module (`database.py`, `inventory_repository.py`, `quest_repository.py`, `schema.py`).
- Retained error-level `print()` to `stderr` for SQLite failures and unexpected exceptions.
- Streamlined `execute_non_query` parameter handling with strict type checking for `list` vs `tuple` vs empty.

### Technical

- `execute_non_query` now uses `isinstance(params, list)` to route to `executemany` and `isinstance(params, tuple)` to route to `execute`, eliminating ambiguous parameter binding errors.
- Empty list params are now silently skipped instead of logging a debug message.
- All `__pycache__` directories were purged to force Python to recompile from the updated `.py` source files.

---

## [0.9.0] - 2026-06-29

### Added

- **Loot Table System** — Every enemy now has its own data-driven loot table with guaranteed drops (e.g. gold) and randomized item drops with configurable drop chance and quantity range.
- **Rare Drops** — Independent rare drop roll (per-mille chance) for each enemy, supporting unique equipment, crafting materials, and collectibles. Displays a special "RARE DROP!" message when triggered.
- **Equipment Rarity** — Five rarity tiers: Common, Uncommon, Rare, Epic, Legendary. Each rarity provides a stat multiplier and sell value multiplier. Rarity is displayed in inventory and equip menus.
- **Item Encyclopedia** — Automatically records every discovered item. Unknown items remain hidden until obtained. Supports filtering by rarity and type (equipment, consumable, materials). Shows per-category and overall completion percentage.
- Added `Item Encyclopedia` as main menu option `[6]` (Save Game moved to `[7]`).
- Added `data/loot_tables.json` with loot tables for all enemies including bosses.

### Changed

- Combat victory rewards now roll loot table drops in addition to base gold/EXP rewards.
- Inventory display now shows rarity label (e.g. `[Rare]`) and formatted stats for each item.
- New `LootEngine` class handles all loot logic, decoupled from combat code.
- New `ItemEncyclopedia` class tracks discovered items, auto-synced with player inventory after combat and on game load/new game.

### Technical

- New modules:
  - `core/rarity.py` — rarity data definitions and helper functions.
  - `core/loot.py` — LootTable, RareDrops, and LootEngine classes.
  - `core/encyclopedia.py` — ItemEncyclopedia class with filtering and display.
- `core/combat.py` — Added `set_loot_engine()` and `set_encyclopedia()` methods. `_award_victory()` now rolls loot and syncs encyclopedia.
- `core/game_context.py` — Creates LootEngine and ItemEncyclopedia, wires them into Combat. Loads `loot_tables.json` via DataLoader.
- `core/data_loader.py` — Added `load_loot_tables()` method.
- `core/game.py` — Added menu entry for encyclopedia, syncs encyclopedia on player create/load.
- `core/inventory.py` — Updated display to show rarity labels and formatted item stats.
- All items in `data/items.json` already had `rarity` fields — no changes needed to existing item data.

---
