from utils.press_any_key import press_any
from utils.text_effect import typewriter, dialog_choice
from story.good_ending import good_ending
from story.bad_ending import bad_ending
import time
from core.enemy import TheFirstHollow

def main_story(player, story_number, combat):
    if story_number == 0:
        typewriter("Hening", dramatic=True)
        typewriter("Hanya ada gemuruh samar air menetes dari langit-langit batu.",)
        typewriter("Lalu aku mendengar suara itu lagi — lembut, tapi jauh di dalam kepalaku",dramatic=True)
        time.sleep(1)

        typewriter('Seren: "Lyren... bangunlah.”')

        typewriter("""
                   Aku membuka mata. Dunia di sekitarku berdenyut biru pucat.
                   Lantai berkilau seperti kaca, dan di tengah ruangan,
                   berdiri Eiden — tubuhnya dipenuhi luka, tapi matanya masih menatap penuh tekad ke arah Crystal of Origin.
                   """)
        typewriter("Aku", dramatic=True)
        typewriter("""
                   tidak seharusnya ada di sini.
                   Aku mati di dalam dungeon ini bertahun-tahun lalu.
                   Tapi sesuatu — atau seseorang — memanggilku kembali.
                   """)
        
        player.story_progress = 1

    elif story_number == 1:
        level_req = 5
        if player.level >= level_req:
            print("=== Pertemuan Kembali ===")
            typewriter("Aku melangkah maju, jari-jariku menyentuh udara yang terasa berat dan dingin.")
            typewriter("Cahaya kristal memantulkan bayanganku di lantai — tapi bukan hanya aku.")
            typewriter("Ada dua wajah.")
            typewriter("Aku(...) dan Seren", dramatic_mid=True)

            typewriter("\nWajahnya sama sepertiku, tapi matanya memantulkan kedamaian yang asing.")

            typewriter("\nEiden: (terkejut) “Lyren...? Tidak... ini tidak mungkin...”")
            typewriter("Aku tersenyum samar. “Mungkin. Tapi seperti halnya kau yang tak pernah menyerah, jiwaku pun menolak hilang begitu saja.”")

            typewriter("\nSeren: (berbisik) “Kau... adalah aku.”")

            typewriter("\nAku menatapnya lama, dan seketika itu aku mengerti.")
            typewriter("Seren bukan orang asing. Ia adalah bagian jiwaku yang diselamatkan Eiden, ketika tubuhku hancur.")
            typewriter("Aku adalah yang tertinggal — bayangan dari dirinya.")

            player.story_progress = 2
        else: 
            print(f"Level yang dibutuhkan ", {level_req})
            return False
    elif story_number == 2:
        level_req = 10
        if player.level >= level_req:
            print("=== Suara yang Memanggil ===")

            typewriter("Setelah pertemuan itu, Seren terus muncul di dalam mimpiku.")
            typewriter("Setiap malam aku melihat lorong batu yang sama, semakin dalam dan semakin gelap.")
            typewriter("Di ujung lorong itu berdiri sebuah pintu raksasa yang tertutup rantai hitam.")

            typewriter('\nSeren: "Tempat itu ada di bawah dungeon."')
            typewriter('Seren: "Di sanalah semuanya dimulai."')

            typewriter("Aku dan Eiden akhirnya turun menuju lapisan terdalam The Forgotten Dungeon.")
            typewriter("Udara menjadi dingin. Bahkan obor-obor sihir mulai padam satu per satu.")

            typewriter("Lalu suara itu terdengar lagi.")
            typewriter('"Kembalikan apa yang telah dicuri..."', dramatic=True)

            typewriter("\nDi depan pintu raksasa terdapat simbol yang sama dengan kalung retak milikku.")

            typewriter("Ketika kusentuhkan kalung itu, rantai-rantai hitam mulai hancur.")
            typewriter("Pintu perlahan terbuka.")

            typewriter("\nDi baliknya terdapat ruangan luas berisi ribuan kristal yang menyimpan kenangan manusia.")

            typewriter("Dan di tengah ruangan itu...")
            typewriter("Seseorang yang wajahnya sama persis denganku berdiri menunggu.", dramatic=True)

            player.story_progress = 3
        else:
            print(f"Level yang dibutuhkan {level_req}")
            return False
    elif story_number == 3:
        level_req = 15
        if player.level >= level_req:
            print("=== Sang Penjaga Echo ===")

            typewriter("Sosok itu mengenakan jubah putih yang telah usang dimakan waktu.")

            typewriter('\n???: "Akhirnya kau datang, Lyren."')

            typewriter("Eiden langsung menghunus pedangnya.")
            typewriter('Eiden: "Siapa kau?"')

            typewriter('???: "Aku adalah Echo pertama."')
            typewriter('"Sisa jiwa yang tertinggal ketika Gerbang Abadi runtuh."')

            typewriter("Kenangan yang bukan milikku tiba-tiba mengalir deras ke dalam pikiranku.")

            typewriter("Aku melihat kerajaan kuno.")
            typewriter("Aku melihat para penyihir membuka Gerbang Abadi.")
            typewriter("Dan aku melihat diriku sendiri berdiri di antara mereka.")

            typewriter('\nAku berbisik, "Aku... ada di sana?"')

            typewriter('Echo: "Bukan hanya ada."')
            typewriter('"Kaulah yang memulai semuanya."')

            typewriter("Dunia di sekitarku terasa runtuh.")

            player.story_progress = 4
        else:
            print(f"Level yang dibutuhkan {level_req}")
            return False
    elif story_number == 4:
        level_req = 20
        if player.level >= level_req:
            print("=== Dosa yang Terlupakan ===")

            typewriter("Echo pertama menunjukkan kenangan yang selama ini disegel.")

            typewriter("Ratusan tahun lalu, Lyren adalah seorang peneliti yang terobsesi mengalahkan kematian.")
            typewriter("Ia percaya bahwa semua penderitaan manusia berasal dari kefanaan.")

            typewriter("Bersama para penyihir kerajaan, ia menciptakan Gerbang Abadi.")

            typewriter("Namun gerbang itu tidak membuka jalan menuju kehidupan kekal.")
            typewriter("Gerbang itu membuka jalan menuju emosi, penyesalan, dan ketakutan seluruh umat manusia.")

            typewriter("Dari situlah The Hollow lahir.")

            typewriter("\nEiden menatapku tanpa berkata apa-apa.")

            typewriter("Aku mengerti sekarang.")
            typewriter("Monster-monster itu ada karena kesalahanku.")

            typewriter('\nEcho: "Dan sekarang kau harus menentukan nasib dunia."')

            player.story_progress = 5
        else:
            print(f"Level yang dibutuhkan {level_req}")
            return False
    elif story_number == 5:
        level_req = 25
        if player.level >= level_req:
            print("=== Crystal of Origin ===")

            typewriter("Kami akhirnya mencapai ruang terdalam dungeon.")

            typewriter("Crystal of Origin berdiri megah di tengah kehampaan.")
            typewriter("Cahaya biru yang dipancarkannya terasa hidup.")

            typewriter("Seren muncul sekali lagi.")

            typewriter('\nSeren: "Sekarang kau tahu semuanya."')
            typewriter('"Tapi mengetahui kebenaran tidak berarti kau siap menerimanya."')

            typewriter("Untuk pertama kalinya, Seren dan diriku berdiri berdampingan.")

            typewriter("Aku melihat diriku yang seharusnya.")
            typewriter("Bukan bayangan. Bukan pecahan jiwa.")

            typewriter("Utuh.")

            typewriter("Crystal mulai bergetar.")
            typewriter("Gerbang Abadi perlahan terbuka kembali di belakangnya.")

            typewriter("\nDan dari dalam gerbang itu muncul sesuatu yang bahkan The Hollow takuti.")

            typewriter("The First Hollow.", dramatic=True)

            player.story_progress = 6
        else:
            print(f"Level yang dibutuhkan {level_req}")
            return False
    elif story_number == 6:
        level_req = 30
        if player.level >= level_req:
            print("=== The First Hollow ===")

            typewriter("The First Hollow adalah makhluk yang menakutkan.")
            typewriter("Tubuhnya seperti kabut hitam yang berputar, tapi matanya bersinar merah seperti bara.")

            typewriter("Aku dan Eiden bersiap menghadapi makhluk itu.")

            typewriter('\nEiden: "Kita harus menghentikannya."')

            typewriter('Aku mengangguk. "Ini adalah ujian terakhir."')

            typewriter("Pertempuran itu sengit.")
            typewriter("The First Hollow menyerang dengan kekuatan yang belum pernah kami rasakan sebelumnya.")

            typewriter("Namun dengan kerja sama dan tekad, kami berhasil mengalahkannya.")

            typewriter("\nDengan kematian The First Hollow, cahaya dari Crystal of Origin menyebar ke seluruh dungeon.")
            typewriter("The Hollow mulai menghilang, dan dunia perlahan kembali normal.")

            player.story_progress = 7
        else:
            print(f"Level yang dibutuhkan {level_req}")
            return False
    elif story_number == 7:
        level_req = 35
        if player.level >= level_req:
            player.story_progress = 999
            print("=== The Final Choice ===")
            typewriter("Crystal of Origin mulai retak.")
            typewriter("The First Hollow melangkah keluar dari Gerbang Abadi.")
            typewriter("Setiap langkahnya membuat kenangan dan mimpi buruk berputar di udara.")

            typewriter('\nThe First Hollow: "Aku adalah penyesalan yang tidak pernah diterima."')
            typewriter('"Aku adalah dosa yang tidak pernah ditebus."')

            typewriter('\nEiden: "Lyren... hanya ada satu kesempatan."')

            typewriter('\nSeren: "Apa pun pilihanmu, dunia akan mengingatnya."')
            print("\n ## this choice will have consequences ## \n")
            choice = dialog_choice(
                    "The First Hollow berdiri di hadapanmu. Aura gelapnya membuat dungeon bergetar.",
                    {
                        "1": "Aku akan melawannya.",
                        "2": "Aku harus pergi dari sini."
                    }
                )
            if choice == "1":
                typewriter("\nAku menggenggam pedangku erat.")
                typewriter("Untuk pertama kalinya aku tidak lari dari masa laluku.")
                typewriter('"Aku akan mengakhirinya di sini."', dramatic=True)
                
                battle_result = combat.fight(
                    player,
                    TheFirstHollow()
                )

                if battle_result:
                    good_ending(player)
                else:
                    bad_ending(player)
            elif choice == "2":
                typewriter("\nAku melangkah mundur.")

                typewriter('"Tidak..."')
                typewriter('"Aku tidak sanggup."', dramatic=True)

                typewriter("Aku meninggalkan Crystal of Origin.")
                typewriter("Meninggalkan Eiden.")
                typewriter("Meninggalkan Seren.")

                bad_ending(player)
        else:
            print(f"Level yang dibutuhkan {level_req}")
            return False
    else:
        print("Cerita utama telah selesai.")
        return False