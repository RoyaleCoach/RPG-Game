import sys
import time
import os
import threading
import termios
import tty

def press_any(msg="Tekan tombol apa pun untuk melanjutkan"):
    """
    Menampilkan pesan dengan animasi titik yang bergerak.
    Menghapus tulisan setelah tombol ditekan.
    """
    stop_flag = {"stop": False}  # gunakan dict agar bisa diubah lintas-thread

    def animate():
        dots = 0
        while not stop_flag["stop"]:
            sys.stdout.write("\r" + msg + "." * dots + " " * (3 - dots))
            sys.stdout.flush()
            dots = (dots + 1) % 4
            time.sleep(0.3)
        # bersihkan baris saat animasi berhenti
        sys.stdout.write("\r" + " " * (len(msg) + 5) + "\r")
        sys.stdout.flush()

    # jalankan animasi di thread terpisah
    t = threading.Thread(target=animate)
    t.daemon = True
    t.start()

    # tunggu input satu tombol
    try:
        if os.name == "nt":  # Windows
            import msvcrt
            msvcrt.getch()
        else:  # Linux/Mac
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        input()
    finally:
        stop_flag["stop"] = True  # hentikan animasi
        t.join()
        sys.stdout.write("\r" + " " * (len(msg) + 6) + "\r")  # pastikan bersih
        sys.stdout.flush()
