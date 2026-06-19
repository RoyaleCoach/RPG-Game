import os
import sys
import time
import threading

IS_WINDOWS = os.name == "nt"

if IS_WINDOWS:
    import msvcrt
else:
    import termios
    import tty
    import select


def flush_stdin():
    if IS_WINDOWS:
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)


def typewriter(
    text,
    speed=0.03,
    skip_enabled=True,
    dramatic=False,
    dramatic_mid=False,
    sound=False
):
    skip_event = threading.Event()

    def listen_for_keypress():

        if IS_WINDOWS:

            while not skip_event.is_set():

                if msvcrt.kbhit():
                    msvcrt.getch()
                    skip_event.set()
                    break

                time.sleep(0.05)

        else:

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setcbreak(fd)

                while not skip_event.is_set():

                    dr, _, _ = select.select(
                        [sys.stdin],
                        [],
                        [],
                        0.05
                    )

                    if dr:
                        sys.stdin.read(1)
                        skip_event.set()
                        break

            finally:
                termios.tcsetattr(
                    fd,
                    termios.TCSADRAIN,
                    old_settings
                )

    listener = None

    if skip_enabled:
        listener = threading.Thread(
            target=listen_for_keypress,
            daemon=True
        )
        listener.start()

    i = 0

    while i < len(text):

        if skip_event.is_set():
            sys.stdout.write(text[i:])
            sys.stdout.flush()
            break

        if dramatic_mid and text[i:i + 5] == "(...)":

            for _ in range(3):
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(0.4)

            i += 5
            continue

        sys.stdout.write(text[i])
        sys.stdout.flush()

        time.sleep(speed)

        i += 1

    if dramatic and not skip_event.is_set():

        for _ in range(3):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(0.4)

    print()

    if listener:
        skip_event.set()
        listener.join(timeout=0.1)

    flush_stdin()

def dialog_choice(question, choices):
    """
    Menampilkan pertanyaan + daftar pilihan.

    Bisa menerima:
        ["Ya", "Tidak"]

    atau

        {
            "1": "Ya",
            "2": "Tidak"
        }

    Return:
        key pilihan dalam bentuk string.
    """

    typewriter(f"\n{question}")

    if isinstance(choices, dict):

        for key, text in choices.items():
            print(f"[{key}] {text}")

    elif isinstance(choices, list):

        for i, text in enumerate(choices, start=1):
            print(f"[{i}] {text}")

    else:
        raise TypeError(
            "choices harus berupa list atau dict"
        )

    while True:

        answer = input("> ").strip()

        if isinstance(choices, dict):

            if answer in choices:
                return answer

        else:

            if (
                answer.isdigit()
                and
                1 <= int(answer) <= len(choices)
            ):
                return str(answer)

        typewriter(
            "Pilihan tidak valid. Coba lagi.",
            skip_enabled=False
        )