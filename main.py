import time
import sys
import requests
from datetime import datetime
from colorama import Fore, init as colorama_init

# Inisialisasi warna terminal
colorama_init(autoreset=True)

class GigaHashBotMandiri:
    # Base URL utama hasil buruan Inspect Element kamu
    BASE_URL = "https://gigahash-production.up.railway.app/miniapp/"
    
    def __init__(self):
        # Header disesuaikan dengan isi screenshot permintaan agar server tidak curiga
        self.headers = {
            "Content-Type": "application/json",
            "Origin": "https://gigahash-production.up.railway.app",
            "Referer": "https://gigahash-production.up.railway.app/",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        }

    def log(self, pesan, warna=Fore.WHITE):
        waktu = datetime.now().strftime("%H:%M:%S")
        print(f"{Fore.LIGHTBLACK_EX}[{waktu}] {warna}{pesan}")

    def load_queries(self, nama_file="query.txt"):
        try:
            with open(nama_file, "r") as f:
                queries = [line.strip() for line in f if line.strip()]
            if not queries:
                self.log("⚠️ File query.txt kosong! Masukkan query_id terlebih dahulu.", Fore.YELLOW)
            return queries
        except FileNotFoundError:
            self.log(f"❌ File {nama_file} tidak ditemukan! Silakan buat file tersebut.", Fore.RED)
            return []

    # =========================================================================
    # FUNGSI 1: AUTH / LOGIN & INTIP SALDO (Data Menyatu sesuai Analisis Kamu)
    # =========================================================================
    def login_dan_cek_saldo(self, init_data):
        url_auth = f"{self.BASE_URL}auth"
        payload = {"initData": init_data}
        
        try:
            self.log("📡 Mengirim data otentikasi ke server...", Fore.LIGHTBLACK_EX)
            response = requests.post(url_auth, headers=self.headers, json=payload, timeout=15)
            
            # --- FITUR DEBUGGING: JIKA SERVER ERROR (Bukan 200 OK) ---
            if response.status_code != 200:
                self.log(f"⚠️ Server merespons dengan Status Code: {response.status_code}", Fore.YELLOW)
                self.log(f"📄 Detail Isu Server: {response.text[:200]}", Fore.LIGHTBLACK_EX)
                return False
                
            data_json = response.json()
            
            # --- MASUK KE PROSES PEMBACAAN JSON ---
            if data_json.get("ok") is True:
                user_data = data_json.get("user", {})
                
                # Ekstraksi variabel sesuai dengan isi struktur tab Respons kamu
                username = user_data.get("first_name", "Unknown")
                telegram_id = user_data.get("telegram_id", "N/A")
                power = user_data.get("power", 0)
                hashes = user_data.get("hashes", 0)
                balance = user_data.get("balance", 0)
                
                self.log(f"👤 Akun: {username} ({telegram_id})", Fore.CYAN)
                self.log(f"🔋 Power Mining: {power} GHS | 🪙 Saldo Koin: {balance}", Fore.LIGHTCYAN_EX)
                self.log(f"💎 Hashes Saat Ini: {hashes}", Fore.LIGHTBLUE_EX)
                return True
            else:
                self.log(f"❌ Gagal Masuk: Respons 'ok' bernilai False.", Fore.RED)
                self.log(f"🐞 Raw JSON Respons: {data_json}", Fore.LIGHTBLACK_EX)
                return False
                
        except requests.exceptions.Timeout:
            self.log("❌ Koneksi Gagal: Timeout (Server down atau internet lambat).", Fore.RED)
            return False
        except ValueError:
            # --- FITUR DEBUGGING: JIKA FORMAT BUKAN JSON ---
            self.log("❌ Gagal parsing data: Respons dari server bukan format JSON (Kemungkinan Cloudflare/Maintenance).", Fore.RED)
            return False
        except Exception as e:
            self.log(f"❌ Terjadi bug tidak diketahui saat login: {e}", Fore.RED)
            return False

    # =========================================================================
    # FUNGSI 2: POST CLAIM (Eksekusi Klaim Hasil Giga Hash)
    # =========================================================================
    def eksekusi_klaim(self, init_data):
        url_claim = f"{self.BASE_URL}claim"
        payload = {"initData": init_data}
        
        try:
            self.log("⚡ Memulai proses klaim hasil mining...", Fore.LIGHTBLUE_EX)
            response = requests.post(url_claim, headers=self.headers, json=payload, timeout=15)
            
            if response.status_code != 200:
                self.log(f"❌ Gagal klaim, Server merespons status: {response.status_code}", Fore.RED)
                return
                
            res_json = response.json()
            
            # Membaca respons sukses berdasarkan pembacaan JSON klaim
            if res_json.get("ok") is True or "success" in res_json.get("message", "").lower():
                self.log("✅ Klaim Berhasil! Hasil mining telah dipindahkan ke saldo.", Fore.GREEN)
            else:
                self.log(f"⚠️ Server menolak klaim: {res_json.get('message', 'Tanpa alasan/pesan')}", Fore.YELLOW)
                self.log(f"🐞 Raw JSON Respons: {res_json}", Fore.LIGHTBLACK_EX)
                
        except Exception as e:
            self.log(f"❌ Gagal eksekusi fungsi klaim karena Bug: {e}", Fore.RED)

# =========================================================================
# ORKESTRASI UTAMA (Siklus Akun & Sistem Jeda 1 Menit)
# =========================================================================
def main():
    bot = GigaHashBotMandiri()
    
    print(f"{Fore.GREEN}==================================================")
    print(f"{Fore.GREEN}🚀 PROYEK BOT GIGA HASH - BUATAN MANDIRI")
    print(f"{Fore.GREEN}==================================================")
    
    queries = bot.load_queries("query.txt")
    if not queries:
        bot.log("Program dihentikan karena tidak ada akun yang dimuat.", Fore.RED)
        return
        
    bot.log(f"📂 Total antrean akun: {len(queries)} akun berhasil ditemukan.\n", Fore.LIGHTGREEN_EX)

    for indeks, data_query in enumerate(queries):
        nomor_akun = indeks + 1
        bot.log(f"⏳ [Akun {nomor_akun}/{len(queries)}] Sedang diproses...", Fore.MAGENTA)
        
        # 1. Jalankan Login & Intip Data
        login_sukses = bot.login_dan_cek_saldo(data_query)
        
        # 2. Jika login berhasil, otomatis langsung tembak fungsi klaim
        if login_sukses:
            bot.eksekusi_klaim(data_query)
        else:
            bot.log(f"⏭️ Melewati Akun ke-{nomor_akun} karena terjadi kendala login.", Fore.YELLOW)
            
        # 3. Sistem Delay Pasca Eksekusi (Kecuali Akun Terakhir)
        if nomor_akun < len(queries):
            print("") # Baris kosong agar log di terminal rapi per akun
            bot.log("🕒 Memulai jeda pengaman sesuai instruksi (1 Menit / 60 detik)...", Fore.LIGHTBLACK_EX)
            
            # Hitung mundur interaktif agar kamu tahu bot-nya tidak nge-hang/macet
            for sisa_waktu in range(60, 0, -1):
                sys.stdout.write(f"\r⏱️ Berpindah akun dalam {sisa_waktu} detik... ")
                sys.stdout.flush()
                time.sleep(1)
            print("\n") # Reset baris setelah hitung mundur selesai

    print(f"{Fore.GREEN}==================================================")
    print(f"{Fore.GREEN}🎉 SEMUA ANTRENAN AKUN TELAH SELESAI DIEKSEKUSI!")
    print(f"{Fore.GREEN}==================================================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Program dihentikan secara paksa oleh pengguna (CTRL+C).")
    except Exception as bug_utama:
        print(f"\n{Fore.RED}❌ Program utama mengalami Crash: {bug_utama}")
