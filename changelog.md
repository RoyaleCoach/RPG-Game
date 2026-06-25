# Changelog

## [0.1.0] - 2025-12-20

### Added

* Save/Load System
* Inventory
* Merchant
* Story Introduction
* Text Effects
* Cross-Platform Keyboard Input

---

## [0.1.1] - 2026-06-20

### Fixed

* Folder Structure
* Import Functions
* Save/Load Reliability
* Player Management
* Input Validation

---

## [0.1.2] - 2026-06-24

### Added

* Expanded Enemy Roster
* Enemy Stat Balancing
* New Dungeon Encounters
* Improved Combat Variety

---

## [0.1.3] - 2026-06-24

### Added

* Expanded Item Collection
* Weapon Progression System
* Armor Equipment System
* Potion Variety
* Item Rarity System
* Limited (Quest-Exclusive) Items
* Merchant Inventory Rework

---

## [0.1.4] - 2026-06-24

### Added

* Quest System
* Quest Board
* Quest Progress Tracking
* Quest Completion Rewards
* Quest-Exclusive Item Rewards
* Enemy Kill Tracking
* Puzzle Completion Tracking
* Automatic Quest Completion Check
* Integration Between Quests and Limited Items

---

## [0.1.4.1] - 2026-06-24

### New Features

* Quest Progress Tracking System
* Dynamic Quest Completion Rewards
* Floor Progression System
* Equipment Status Indicator ([EQUIPPED])

### Gameplay Changes

* Defense is now consumed during battle instead of remaining static
* Battle UI now shows current defense value
* Floor increases every 3 enemy victories

### Refactoring

* Quest objectives now use type/target metadata
* Simplified quest progress and completion logic
* Improved maintainability for future quest additions

### Fixes

* Fixed quest progress not being displayed
* Fixed floor progression not being linked to quest requirements

---

## [0.2.0] - 2026-06-24

### Added

* Dungeon Event System
* Treasure Room Event
* Healing Fountain Event
* Cursed Shrine Event
* Ancient Statue Event
* Gambler Event
* Secret Passage Event
* Lost Adventurer Event
* Elite Enemy Encounters
* Mimic Chest Encounters
* Random Event Generation
* Event-Based Rewards and Penalties

### Gameplay Changes

* Dungeon exploration now includes random non-combat encounters
* Players can obtain gold, items, stat bonuses, or penalties through events
* Secret Passages can advance floor progression
* Some events introduce risk-versus-reward decisions

### Improved

* Dungeon variety and replayability
* Exploration progression system
* Reward distribution outside of combat

---

## [0.2.1] - 2026-06-25

### Added

* Boss Enemy System
* Dedicated Boss Class
* Level-Based Boss Scaling
* Boss Reward System (EXP & Gold)
* Boss Data Configuration via Dictionary
* Automatic Boss Encounters

### Gameplay Changes

* Bosses now grant significantly higher rewards than normal enemies
* Boss difficulty now scales with player progression
* Enemy and Boss systems are now separated for easier balancing
* Improved dungeon progression with milestone encounters
* Boss battle is triggered every 3 dungeon expeditions
* Boss encounters act as progression milestones

### Refactoring

* Introduced reusable Boss inheritance from Enemy
* Centralized boss definitions in `enemy.py`
* Improved combat reward handling for different enemy types

---

## [0.3.0] - 2026-06-25

### Added

* JSON-Based Data System
* DataLoader Utility
* `items.json`
* `quests.json`
* `bosses.json`
* `version.json`
* Dynamic Version Loading
* External Game Configuration Support
* Merchant Item Loading From JSON
* Boss Loading From JSON
* Item Database Architecture

### Refactoring

* Migrated Items from Python dictionaries to JSON
* Migrated Quests from Python dictionaries to JSON
* Migrated Bosses from Python dictionaries to JSON
* Refactored Inventory to use item database
* Refactored Merchant to use centralized item data
* Refactored Quest System to use loaded quest data
* Refactored Boss System to use loaded boss data
* Refactored Game Initialization Flow
* Implemented Dependency Injection between systems
* Reduced hardcoded game content

### Improved

* Easier balancing and content editing
* Better separation between code and game data
* Improved maintainability
* Improved scalability for future content updates
* Improved project organization

---

## [0.3.1] - 2026-06-25

### Added

* Save Directory Support
* Automatic Save Folder Creation
* PyInstaller-Friendly Path Handling
* Centralized Version Information Display
* Runtime Data Reload Support

### Fixed

* Save/Load Initialization Issues
* Merchant Constructor Dependency Errors
* Boss Loading Errors
* Item Lookup After JSON Migration
* Data File Path Resolution
* Save File Location Handling
* Version Data Loading
* Multiple Dependency Injection Issues
* Inventory Data Access Errors

### Refactoring

* Improved Save System Architecture
* Improved Data Loading Reliability
* Simplified System Initialization Order
* Standardized Access to Game Data
* Cleaned Up Legacy Hardcoded References

### Technical

* Prepared project for executable distribution
* Improved compatibility with packaged builds
* Centralized game content management
* Established foundation for future modding support

---

## [0.3.2] - 2026-06-25

### Added

* In-Battle Potion Usage
* Combat Heal Action
* Potion Selection During Battle
* Case-Insensitive Equipment Selection
* Case-Insensitive Potion Usage
* Equipment Validation Improvements

### Gameplay Changes

* Players can now consume potions directly during combat
* Healing is now available as a dedicated battle action
* Weapon, Armor, and Potion names are no longer case-sensitive
* Equipment and consumable selection is more user-friendly

### Improved

* Inventory interaction flow
* Combat usability and survivability
* Item lookup reliability
* User input handling for equipment and consumables

### Fixed

* Equipment selection failing due to letter case mismatch
* Potion usage lookup inconsistencies
* Invalid item name recognition issues
* Inventory item validation edge cases

### Refactoring

* Unified item name matching logic across weapons, armor, and potions
* Reduced duplicate item validation code
* Improved separation between combat logic and item data access

---

## [0.4.0] - 2026-06-26

### Added

* Main Story Chapter 1–7
* Story progression system based on player level
* New characters: Lyren, Seren, Eiden, Echo, and The First Hollow
* Crystal of Origin storyline
* Final Choice event
* The First Hollow final boss battle
* Story-based level requirements
* Narrative dialogue and cutscene sequences

### Changed

* Improved story pacing and progression
* Refined dungeon lore and worldbuilding
* Integrated story progression with player save data

### Fixed

* Story progression tracking
* Chapter unlock consistency
* Final battle and ending flow

---

## [0.5.0] - 2026-06-26

### Added

* Multiple Ending System
* Good Ending: Echoes of Redemption
* Bad Ending: The Cycle Repeats
* Final decision event with meaningful consequences
* The First Hollow final confrontation
* Ending paths based on player choices and battle outcome

### Changed

* Reworked final chapter flow
* Improved narrative impact of player decisions
* Enhanced story conclusion and character arcs

### Fixed

* Final boss progression logic
* Ending trigger conditions
* Story completion flow

---

## [0.5.1] - 2026-06-26

### Added

* English localization for in-game text, menus, and story
* Translated story scripts, UI prompts, README, and supporting utilities

### Changed

* Default language set to English across the codebase

### Fixed

* Corrected various untranslated prompts and inconsistent messages

---

## [0.6.0] - 2026-06-26

### Added

* Spell System with Skill Management
* Mana resource system for players (scales with level)
* Player spell learning and tracking (learned_spells)
* Spell casting in combat as a dedicated battle action
* Spell effect system (damage, healing, buff types)
* Mana cost enforcement and validation
* Dynamic spell availability based on learned spells
* Spell-to-effect resolution with type-based handling
* Persistent spell state in save/load system
* Integration with JSON-based spell data from `spells.json`

### Gameplay Changes

* Players now gain mana pool that regenerates on level-up
* Combat offers four actions: attack, defend, heal (potions), and **spell**
* Spells consume mana and produce varied effects (damage enemies, heal self, boost defense)
* Spells are learned progressively throughout gameplay
* Initial player setup now includes a starter spell (Icicle)
* Spell descriptions are displayed dynamically during combat

### Improved

* Combat depth and strategic variety
* Player progression through spell acquisition
* Combat UI now displays current mana pool alongside HP
* Spell selection menu shows mana costs and spell types
* Effect application based on spell metadata

### Technical

* Created `Skill` class for spell management and lookup
* Enhanced `Player` class with mana property and spell tracking
* Rewrote `Combat.fight()` to support spell action handling
* Implemented `apply_spell_effect()` for flexible spell type processing
* Updated `SaveSystem` to persist mana and learned_spells on save/load
* Established foundation for future spell balancing and spell trees

---

