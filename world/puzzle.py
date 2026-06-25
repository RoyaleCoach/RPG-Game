import random

def random_puzzle():
    puzzles = [
        ("Which is heavier, 1 kg of cotton or 1 kg of iron?", "same"),
        ("I have keys but no doors. What am I?", "piano"),
        ("Which number multiplied by 0 remains 0?", "any")
    ]
    question, answer = random.choice(puzzles)
    print("\n❓ A puzzle appears!")
    print(question)
    guess = input("Your answer: ").lower()
    if answer in guess:
        print("✅ Correct! You solved the puzzle.")
        return True
    else:
        print("❌ Wrong! You lose a little HP.")
        return False
