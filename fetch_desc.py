import asyncio
import json
import re
from wreq import Client, Emulation

def extract_urls_from_file(filename):
    """Membaca file txt dan mengekstrak semua URL YouTube."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        # Mengambil semua link watch?v=
        urls = re.findall(r'(https://www.youtube.com/watch\?v=[\w-]+)', content)
        # Menghapus duplikat dan mempertahankan urutan
        return list(dict.fromkeys(urls))
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan!")
        return []

def parse_recipes(description):
    """Mengekstrak bagian [INDONESIAN] dan [ENGLISH] dari teks deskripsi."""
    # Regex untuk menangkap teks setelah tag hingga batas "===================" atau akhir teks
    id_pattern = r'\[INDONESIAN\]\n(.*?)(?:\n===================|\n\[ENGLISH\]|$)'
    en_pattern = r'\[ENGLISH\]\n(.*?)(?:\n===================|$)'
    
    id_match = re.search(id_pattern, description, re.DOTALL | re.IGNORECASE)
    en_match = re.search(en_pattern, description, re.DOTALL | re.IGNORECASE)
    
    id_recipe = id_match.group(1).strip() if id_match else None
    en_recipe = en_match.group(1).strip() if en_match else None
    
    return id_recipe, en_recipe

async def fetch_and_extract_video(client, semaphore, url, results_id, results_en):
    """Mengambil halaman video dan mengekstrak resep dari deskripsinya."""
    async with semaphore:  # Membatasi jumlah request bersamaan
        print(f"Memproses: {url}")
        try:
            resp = await client.get(url)
            html_content = await resp.text()
            
            # Mencari JSON ytInitialPlayerResponse di dalam HTML
            match = re.search(r'var ytInitialPlayerResponse = (\{.*?\});</script>', html_content)
            if not match:
                print(f"  [!] Gagal menemukan data JSON di {url}")
                return
            
            # Parsing JSON untuk mengambil teks deskripsi utuh
            data = json.loads(match.group(1))
            
            # Mendapatkan judul dan deskripsi video
            title = data.get("videoDetails", {}).get("title", "Judul Tidak Diketahui")
            description = data.get("videoDetails", {}).get("shortDescription", "")
            
            if not description:
                print(f"  [!] Deskripsi kosong untuk {url}")
                return
            
            # Memisahkan resep
            id_recipe, en_recipe = parse_recipes(description)
            
            if id_recipe:
                results_id.append(f"Judul: {title}\nURL: {url}\n\n{id_recipe}\n\n{'-'*50}\n")
            
            if en_recipe:
                results_en.append(f"Title: {title}\nURL: {url}\n\n{en_recipe}\n\n{'-'*50}\n")
                
        except Exception as e:
            print(f"  [Error] Gagal memproses {url}: {e}")

async def main():
    # 1. Ambil URL dari file yang sudah Anda buat sebelumnya
    input_file = "parsed_videos_full.txt"
    urls = extract_urls_from_file(input_file)
    
    if not urls:
        print("Tidak ada URL yang diproses. Keluar...")
        return
        
    print(f"Ditemukan {len(urls)} video. Memulai ekstraksi...\n")

    # 2. Siapkan penyimpanan hasil dan Semaphore (Batas 5 video bersamaan agar tidak kena blokir/Rate Limit)
    results_id = []
    results_en = []
    semaphore = asyncio.Semaphore(5) 
    
    # Inisialisasi wreq client dengan penyamaran browser Safari
    client = Client(emulation=Emulation.Safari26)
    
    # 3. Buat task untuk setiap URL dan jalankan secara asinkron
    tasks = [
        fetch_and_extract_video(client, semaphore, url, results_id, results_en) 
        for url in urls
    ]
    
    await asyncio.gather(*tasks)
    
    # 4. Simpan ke dua dataset terpisah dengan format rapi
    with open("dataset_resep_indonesia.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results_id))
        
    with open("dataset_resep_inggris.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results_en))
        
    print(f"\nSelesai! Berhasil menyimpan:")
    print(f"- {len(results_id)} resep ke dataset_resep_indonesia.txt")
    print(f"- {len(results_en)} resep ke dataset_resep_inggris.txt")

if __name__ == "__main__":
    asyncio.run(main())