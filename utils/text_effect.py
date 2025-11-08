import sys
import time
import threading
import termios
import tty
import select

def typewriter(text, speed=0.03, skip_enabled=True, dramatic=False, dramatic_mid=False, sound=True):
    """
    Efek mengetik huruf satu per satu.
    Tekan tombol apa pun untuk skip.
    dramatic=True -> titik tiga di akhir (pada baris yang sama).
    sound=True   -> bunyi ketik tiap huruf (terminal bell).
    """
    import sys, time, threading, termios, tty, select

    skip_event = threading.Event()

    def listen_for_keypress():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            while not skip_event.is_set():
                dr, _, _ = select.select([sys.stdin], [], [], 0.05)
                if dr:
                    sys.stdin.read(1)
                    skip_event.set()
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def flush_stdin():
        """Membersihkan buffer input agar tidak sisa karakter."""
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

    listener = None
    if skip_enabled:
        listener = threading.Thread(target=listen_for_keypress, daemon=True)
        listener.start()

    # Efek mengetik huruf
    for i, char in enumerate(text):
        if skip_event.is_set():
            sys.stdout.write(text[i:])
            sys.stdout.flush()
            break
        sys.stdout.write(char)
        if sound:
            sys.stdout.write('\a')  # bunyi bell
        sys.stdout.flush()
        time.sleep(speed)

    if dramatic_mid and text[i:i+5] == "(...)":
            # hapus tanda dari layar
            sys.stdout.write('\b' * 5 + ' ' * 5 + '\b' * 5)
            sys.stdout.flush()

            # tulis titik tiga pelan-pelan
            for _ in range(3):
                sys.stdout.write(".")
                if sound:
                    sys.stdout.write('\a')
                sys.stdout.flush()
                time.sleep(0.4)

            # lompatkan indeks agar tidak menulis "(...)" literal
            for _ in range(4):
                next(text, None)

    # Efek dramatis (titik-tiga di sebelah teks)
    if dramatic and not skip_event.is_set():
        for _ in range(3):
            sys.stdout.write(".")
            if sound:
                sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(0.4)
    print()  # baris baru setelah selesai

    # Reset input terminal
    if listener:
        skip_event.set()
        listener.join(timeout=0.1)
        flush_stdin()


def flush_stdin():
    """Buang semua input yang tertinggal di buffer stdin (Ubuntu-safe)."""
    termios.tcflush(sys.stdin, termios.TCIFLUSH)


def dialog_choice(question, choices):
    """
    Menampilkan pertanyaan + daftar pilihan.
    Bisa menerima:
      - list -> ["Ya", "Tidak"]
      - dict -> {"1": "Ya", "2": "Tidak"}
    Mengembalikan key pilihan (string).
    """
    typewriter(f"\n{question}")

    # Jika dict → gunakan key dan value
    if isinstance(choices, dict):
        for key, text in choices.items():
            print(f"[{key}] {text}")
    # Jika list → buat nomor otomatis
    elif isinstance(choices, list):
        for i, text in enumerate(choices, 1):
            print(f"[{i}] {text}")
    else:
        raise TypeError("choices harus berupa list atau dict")

    # Validasi input
    while True:
        answer = input("> ").strip()
        if isinstance(choices, dict):
            if answer in choices:
                return answer
        else:
            if answer.isdigit() and 1 <= int(answer) <= len(choices):
                return str(answer)
        typewriter("Pilihan tidak valid. Coba lagi.")
