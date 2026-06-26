from utils.press_any_key import press_any
from utils.text_effect import typewriter, dialog_choice
from story.good_ending import good_ending
from story.bad_ending import bad_ending
import time
from core.enemy import TheFirstHollow


def main_story(player, story_number, combat):
    if story_number == 0:
        typewriter("Silence", dramatic=True)
        typewriter("Only the faint drip of water echoed from the stone ceiling.")
        typewriter(
            "Then I heard that voice again — soft, but far inside my head", dramatic=True)
        time.sleep(1)

        typewriter('Seren: "Lyren... wake."')

        typewriter("""
                   I opened my eyes. The world around me pulsed with pale blue light.
                   The floor gleamed like glass, and in the center of the room,
                   stood Eiden — his body scarred, but his eyes fixed on the Crystal of Origin with unwavering resolve.
                   """)
        typewriter("I", dramatic=True)
        typewriter("""
                   I shouldn't be here.
                   I died in this dungeon years ago.
                   Yet something — or someone — called me back.
                   """)

        player.story_progress = 1

    elif story_number == 1:
        level_req = 5
        if player.level >= level_req:
            print("=== Reunion ===")
            typewriter(
                "I stepped forward, my fingers brushing air that felt heavy and cold.")
            typewriter(
                "The crystal's light reflected my shadow on the floor — but I was not alone.")
            typewriter("There were two faces.")
            typewriter("Me(...) and Seren", dramatic_mid=True)

            typewriter(
                "\nHis face mirrored mine, but his eyes reflected a strange calm.")

            typewriter("\nEiden: (startled) 'Lyren...? No... this can't be...'")
            typewriter(
                "I smiled faintly. 'Maybe. But just as you never gave up, my soul refused to fade away.'")

            typewriter("\nSeren: (whisper) 'You... are me.'")

            typewriter(
                "\nI stared at him for a long moment, and then I understood.")
            typewriter(
                "Seren was not a stranger. He was part of my soul saved by Eiden when my body was shattered.")
            typewriter("I was what remained — a shadow of him.")

            player.story_progress = 2
        else:
            print(f"Level required {level_req}")
            return False
    elif story_number == 2:
        level_req = 10
        if player.level >= level_req:
            print("=== The Calling Voice ===")

            typewriter(
                "After that encounter, Seren kept appearing in my dreams.")
            typewriter(
                "Every night I saw the same stone corridor, growing deeper and darker.")
            typewriter(
                "At the corridor's end stood a giant door bound by black chains.")

            typewriter('\nSeren: "That place lies beneath the dungeon."')
            typewriter('Seren: "It is where it all began."')

            typewriter(
                "Eiden and I finally descended into the deepest layers of The Forgotten Dungeon.")
            typewriter(
                "The air grew cold. Even the magical torches dimmed one by one.")

            typewriter("Then the voice came again.")
            typewriter('"Return what was stolen..."', dramatic=True)

            typewriter(
                "\nIn front of the giant door was the same symbol as my cracked necklace.")

            typewriter(
                "When I touched the necklace, the black chains began to crumble.")
            typewriter("The door slowly opened.")

            typewriter(
                "\nBehind it lay a vast chamber filled with thousands of crystals, each holding human memories.")

            typewriter("And in the center of the room...")
            typewriter(
                "Someone with a face identical to mine stood waiting.", dramatic=True)

            player.story_progress = 3
        else:
            print(f"Level required {level_req}")
            return False
    elif story_number == 3:
        level_req = 15
        if player.level >= level_req:
            print("=== The Echo Guardian ===")

            typewriter("The figure wore a white robe, aged and worn by time.")

            typewriter('\n???: "At last you have come, Lyren."')

            typewriter('Eiden drew his sword at once.')
            typewriter('Eiden: "Who are you?"')

            typewriter('???: "I am the First Echo."')
            typewriter(
                '"A remnant soul left behind when the Eternal Gate collapsed."')

            typewriter("Memories not my own suddenly flooded my mind.")

            typewriter("I saw an ancient kingdom.")
            typewriter("I saw mages opening the Eternal Gate.")
            typewriter("And I saw myself standing among them.")

            typewriter('\nI whispered, "Was I... there?"')

            typewriter('Echo: "Not only were you there."')
            typewriter('"You were the one who began it all."')

            typewriter("The world around me felt like it was collapsing.")

            player.story_progress = 4
        else:
            print(f"Level required {level_req}")
            return False
    elif story_number == 4:
        level_req = 20
        if player.level >= level_req:
            print("=== Forgotten Sins ===")

            typewriter(
                "The First Echo revealed memories that had been sealed away.")

            typewriter(
                "Hundreds of years ago, Lyren was a researcher obsessed with conquering death.")
            typewriter(
                "He believed that all human suffering stemmed from mortality.")

            typewriter(
                "Together with the kingdom's mages, he created the Eternal Gate.")

            typewriter("But the gate did not open a path to eternal life.")
            typewriter(
                "It opened a path to the emotions, regrets, and fears of all humanity.")

            typewriter("From there, The Hollow was born.")

            typewriter("\nEiden stared at me without saying a word.")

            typewriter("I understood now.")
            typewriter("Those monsters existed because of my mistakes.")

            typewriter(
                '\nEcho: "And now you must decide the fate of the world."')

            player.story_progress = 5
        else:
            print(f"Level required {level_req}")
            return False
    elif story_number == 5:
        level_req = 25
        if player.level >= level_req:
            print("=== Crystal of Origin ===")

            typewriter("We finally reached the dungeon's deepest chamber.")

            typewriter("The Crystal of Origin stood majestic in the void.")
            typewriter("The blue light it emitted felt alive.")

            typewriter("Seren appeared once more.")

            typewriter('\nSeren: "Now you know everything."')
            typewriter(
                '"But knowing the truth does not mean you are ready to accept it."')

            typewriter("For the first time, Seren and I stood side by side.")

            typewriter("I saw the self I was meant to be.")
            typewriter("Not a shadow. Not a fragment of a soul.")

            typewriter("Whole.")

            typewriter("The Crystal began to tremble.")
            typewriter("The Eternal Gate slowly reopened behind it.")

            typewriter(
                "\nAnd from within the gate emerged something even The Hollow feared.")

            typewriter("The First Hollow.", dramatic=True)

            player.story_progress = 6
        else:
            print(f"Level required {level_req}")
            return False
    elif story_number == 6:
        level_req = 30
        if player.level >= level_req:
            print("=== The First Hollow ===")

            typewriter("The First Hollow is a terrifying creature.")
            typewriter(
                "Its body swirls like black mist, but its eyes glow crimson like embers.")

            typewriter("Eiden and I prepared to face the beast.")

            typewriter('\nEiden: "We must stop it."')

            typewriter('I nodded. "This is the final test."')

            typewriter("The battle was fierce.")
            typewriter(
                "The First Hollow attacked with a power we had never felt before.")

            typewriter("But through teamwork and determination, we prevailed.")

            typewriter(
                "\nWith the First Hollow's death, light from the Crystal of Origin spread through the dungeon.")
            typewriter(
                "The Hollow began to fade, and the world slowly returned to normal.")

            player.story_progress = 7
        else:
            print(f"Level required {level_req}")
            return False
    elif story_number == 7:
        level_req = 35
        if player.level >= level_req:
            player.story_progress = 999
            print("=== The Final Choice ===")
            typewriter("The Crystal of Origin began to crack.")
            typewriter("The First Hollow stepped out of the Eternal Gate.")
            typewriter(
                "Each step stirred memories and nightmares into the air.")

            typewriter('\nThe First Hollow: "I am the regret never accepted."')
            typewriter('"I am the sin never redeemed."')

            typewriter('\nEiden: "Lyren... there is only one chance."')

            typewriter(
                '\nSeren: "Whatever you choose, the world will remember it."')
            print("\n ## this choice will have consequences ## \n")
            choice = dialog_choice(
                "The First Hollow stands before you. Its dark aura makes the dungeon quake.",
                {
                    "1": "I will fight it.",
                    "2": "I must leave this place."
                }
            )
            if choice == "1":
                typewriter("\nI gripped my sword tightly.")
                typewriter("For the first time I would not run from my past.")
                typewriter('"I will end it here."', dramatic=True)

                battle_result = combat.fight(
                    player,
                    TheFirstHollow()
                )

                if battle_result:
                    good_ending(player)
                else:
                    bad_ending(player)
            elif choice == "2":
                typewriter("\nI stepped back.")

                typewriter('"No..."')
                typewriter('"I cannot do this."', dramatic=True)

                typewriter("I left the Crystal of Origin.")
                typewriter("Leaving Eiden behind.")
                typewriter("Leaving Seren behind.")

                bad_ending(player)
        else:
            print(f"Level required {level_req}")
            return False
    else:
        print("The main story is complete.")
        return False
