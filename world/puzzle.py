import random


PUZZLES = [
    # Logic
    {
        "question": "Which is heavier, 1 kg of cotton or 1 kg of iron?",
        "answers": ["same", "equal", "both"],
    },
    {
        "question": "I have keys but no doors. What am I?",
        "answers": ["piano"],
    },
    {
        "question": "The more you take, the more you leave behind. What am I?",
        "answers": ["footsteps", "footstep"],
    },

    # Math
    {
        "question": "What comes next? 2, 4, 8, 16, ?",
        "answers": ["32"],
    },
    {
        "question": "What is 15 + 27?",
        "answers": ["42"],
    },
    {
        "question": "How many sides does a hexagon have?",
        "answers": ["6", "six"],
    },

    # Dungeon
    {
        "question": "A torch burns brighter when...\nA) It is wet\nB) It has fuel\nC) It is buried",
        "answers": ["b"],
    },
    {
        "question": "Which direction does the sun rise?",
        "answers": ["east"],
    },
    {
        "question": "A locked door has no keyhole. What should you look for?",
        "answers": ["lever", "switch", "button"],
    },

    # RPG
    {
        "question": "A healer's greatest weapon is...",
        "answers": ["healing", "kindness", "magic"],
    },
    {
        "question": "What defeats greed?\nA) Gold\nB) Wisdom\nC) Hunger",
        "answers": ["b", "wisdom"],
    },
]


def random_puzzle():
    puzzle = random.choice(PUZZLES)

    print("\n🧩 Ancient Puzzle")
    print("-" * 30)
    print(puzzle["question"])

    answer = input("\nYour answer: ").strip().lower()

    if answer in puzzle["answers"]:
        print("\n✅ Correct! The ancient mechanism activates.")
        return True

    print("\n❌ Incorrect! A hidden trap is triggered.")
    return False
