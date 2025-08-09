import pygame
import random

pygame.init()

# Ukuran layar
lebar, tinggi = 500, 500
layar = pygame.display.set_mode((lebar, tinggi))
pygame.display.set_caption('Game Mobil')

# Warna
warna = {
    'abu': (100, 100, 100),
    'hijau': (76, 208, 56),
    'merah': (200, 0, 0),
    'putih': (255, 255, 255),
    'kuning': (255, 232, 0)
}

# Jalan
lebar_jalan = 300
lebar_markah, tinggi_markah = 10, 50
jalur = [150, 250, 350]
pemain_x, pemain_y = 250, 400
jalan = (100, 0, lebar_jalan, tinggi)
marka_tepi = [(95, 0, lebar_markah, tinggi), (395, 0, lebar_markah, tinggi)]

# Suara
pygame.mixer.init()
suara_tabrakan = pygame.mixer.Sound('sounds/tabrakan.mp3')
suara_mobil = pygame.mixer.Sound('sounds/laju.mp3')
suara_mobil.set_volume(0.3)
suara_mobil.play(-1)

# Timer
jam = pygame.time.Clock()
fps = 120
kecepatan = 2
skor = 0
berakhir = False
gerak_markah_y = 0

# Font
font = pygame.font.Font(pygame.font.get_default_font(), 16)

# Tombol klik
tombol_kiri = pygame.Rect(20, 440, 40, 40)
tombol_kanan = pygame.Rect(440, 440, 40, 40)

# Kelas kendaraan
class Kendaraan(pygame.sprite.Sprite):
    def __init__(self, gambar, x, y):
        super().__init__()
        skala = 45 / gambar.get_rect().width
        ukuran_baru = (int(gambar.get_rect().width * skala), int(gambar.get_rect().height * skala))
        self.image = pygame.transform.scale(gambar, ukuran_baru)
        self.rect = self.image.get_rect(center=(x, y))

class MobilPemain(Kendaraan):
    def __init__(self, x, y):
        gambar = pygame.image.load('images/car.png')
        super().__init__(gambar, x, y)

# Grup
grup_pemain = pygame.sprite.Group()
grup_kendaraan = pygame.sprite.Group()
pemain = MobilPemain(pemain_x, pemain_y)
grup_pemain.add(pemain)

# Gambar musuh
gambar_kendaraan = [pygame.image.load(f'images/{nama}') for nama in ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']]
gambar_tabrakan = pygame.image.load('images/crash.png')
rect_tabrakan = gambar_tabrakan.get_rect()

# Fungsi gambar markah
def gambar_markah_jalur():
    global gerak_markah_y
    gerak_markah_y = (gerak_markah_y + kecepatan * 2) % (tinggi_markah * 2)
    for y in range(-tinggi_markah * 2, tinggi, tinggi_markah * 2):
        for posisi_x in [jalur[0] + 45, jalur[1] + 45]:
            pygame.draw.rect(layar, warna['putih'], (posisi_x, y + gerak_markah_y, lebar_markah, tinggi_markah))

def tampilkan_skor():
    teks = font.render(f'Skor: {skor}', True, warna['putih'])
    layar.blit(teks, teks.get_rect(center=(50, 400)))

def reset_game():
    global kecepatan, skor, berakhir
    kecepatan, skor, berakhir = 2, 0, False
    grup_kendaraan.empty()
    pemain.rect.center = (pemain_x, pemain_y)
    suara_mobil.play(-1)  # <- Tambahkan agar suara nyala lagi

def tambah_kendaraan():
    if len(grup_kendaraan) < 2:
        if all(k.rect.top >= k.rect.height * 1.5 for k in grup_kendaraan):
            posisi_jalur = random.choice(jalur)
            gambar = random.choice(gambar_kendaraan)
            kendaraan = Kendaraan(gambar, posisi_jalur, -tinggi // 2)
            grup_kendaraan.add(kendaraan)

def deteksi_tabrakan():
    global berakhir
    if pygame.sprite.spritecollide(pemain, grup_kendaraan, True):
        suara_mobil.stop()         # ← Hentikan suara laju saat tabrakan
        suara_tabrakan.play()
        berakhir = True
        rect_tabrakan.center = (pemain.rect.centerx, pemain.rect.top)

def pindah_kiri():
    if pemain.rect.centerx > jalur[0]:
        pemain.rect.x -= 100

def pindah_kanan():
    if pemain.rect.centerx < jalur[2]:
        pemain.rect.x += 100

# ===== Loop Utama =====
berjalan = True
while berjalan:
    jam.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            berjalan = False

        if not berakhir:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pindah_kiri()
                elif event.key == pygame.K_RIGHT:
                    pindah_kanan()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tombol_kiri.collidepoint(event.pos):
                    pindah_kiri()
                elif tombol_kanan.collidepoint(event.pos):
                    pindah_kanan()

    # Gambar latar
    layar.fill(warna['hijau'])
    pygame.draw.rect(layar, warna['abu'], jalan)
    for sisi in marka_tepi:
        pygame.draw.rect(layar, warna['kuning'], sisi)
    gambar_markah_jalur()
    grup_pemain.draw(layar)

    # Mobil musuh
    tambah_kendaraan()
    for k in grup_kendaraan:
        k.rect.y += kecepatan
        if k.rect.top >= tinggi:
            k.kill()
            skor += 1
            if skor % 5 == 0:
                kecepatan += 1

    grup_kendaraan.draw(layar)
    tampilkan_skor()
    deteksi_tabrakan()

    # Game over
    if berakhir:
        layar.blit(gambar_tabrakan, rect_tabrakan)
        pygame.draw.rect(layar, warna['merah'], (0, 50, lebar, 100))
        pesan = font.render('Game over. Main lagi? (Y/N)', True, warna['putih'])
        layar.blit(pesan, pesan.get_rect(center=(lebar // 2, 100)))

    # Tombol kontrol visual
    pygame.draw.rect(layar, warna['kuning'], tombol_kiri)
    pygame.draw.polygon(layar, warna['merah'], [(30, 460), (50, 445), (50, 475)])
    pygame.draw.rect(layar, warna['kuning'], tombol_kanan)
    pygame.draw.polygon(layar, warna['merah'], [(470, 460), (450, 445), (450, 475)])

    pygame.display.update()

    while berakhir:
        jam.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                berakhir = False
                berjalan = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    reset_game()
                elif event.key == pygame.K_n:
                    berakhir = False
                    berjalan = False

# Keluar dari game
suara_mobil.stop()
pygame.quit()
