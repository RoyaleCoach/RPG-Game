from utils.press_any_key import press_any
from utils.text_effect import typewriter, dialog_choice
import time

def intro_story(player):
    typewriter(f"\nSelamat datang, {player.name}\n", 0.04, dramatic=True)
    time.sleep(1)
    typewriter("Ratusan tahun lalu, dunia “Eidral” hancur akibat ritual yang gagal membuka “Gerbang Abadi”.")
    typewriter("Semenjak itu, manusia hidup di bawah bayangan “The Hollow”, makhluk yang lahir dari sisa emosi dan dosa masa lalu.")
    typewriter("Semua sejarah tentang kejadian itu telah dihapus, namun gema (echoes) dari masa itu masih terdengar di bawah tanah — di The Forgotten Dungeon.", dramatic=True)
    press_any()

    typewriter(f"\n{player.name}, seorang pemuda tanpa masa lalu yang terbangun di reruntuhan kota tua. Ia hanya membawa:")
    typewriter("\tPedang patah dengan tulisan kuno: “Forgive the past, or repeat it.”")
    typewriter("\tKalung berbentuk lingkaran retak, terasa hangat setiap kali ia mendekati sesuatu yang “tidak seharusnya ada”.")
    press_any()

    typewriter("Ia tidak tahu siapa dirinya, hanya bahwa suara di kepalanya berbisik:")
    typewriter("“Temukan makna dari Echo. Jangan percaya cahaya, jangan takut kegelapan.”", dramatic=True)

    typewriter("\nPetualanganmu baru saja dimulai...")
    press_any()
