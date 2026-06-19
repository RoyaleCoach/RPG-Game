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


def flush_stdin():
    if IS_WINDOWS:
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)


def wait_for_single_key():

    if IS_WINDOWS:
        msvcrt.getch()

    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            sys.stdin.read(1)

        finally:
            termios.tcsetattr(
                fd,
                termios.TCSADRAIN,
                old_settings
            )


def press_any(msg="Tekan tombol apa pun untuk melanjutkan"):

    stop_event = threading.Event()

    def animate():

        dots = 0

        while not stop_event.is_set():

            sys.stdout.write(
                "\r" +
                msg +
                "." * dots +
                " " * (3 - dots)
            )

            sys.stdout.flush()

            dots = (dots + 1) % 4

            time.sleep(0.3)

        sys.stdout.write(
            "\r" +
            " " * (len(msg) + 5) +
            "\r"
        )

        sys.stdout.flush()

    animation_thread = threading.Thread(
        target=animate,
        daemon=True
    )

    animation_thread.start()

    try:
        wait_for_single_key()

    finally:

        stop_event.set()

        animation_thread.join(timeout=0.5)

        sys.stdout.write(
            "\r" +
            " " * (len(msg) + 6) +
            "\r"
        )

        sys.stdout.flush()

        flush_stdin()