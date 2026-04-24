import re
import pandas as pd

def normalize_url(url):
    """Menghapus parameter tambahan pada URL YouTube agar konsisten."""
    match = re.search(r'(v=[\w-]+)', url)
    if match:
        return f"https://www.youtube.com/watch?{match.group(1)}"
    return url.strip()

def parse_thumbnails(filename):
    data = {}
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'\d+\.\s+(.*?)\n\s+Link:\s+(.*?)\n\s+Thumb:\s+(.*?)(?=\n\n|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    for title, link, thumb in matches:
        norm_url = normalize_url(link)
        data[norm_url] = {'title': title.strip(), 'thumbnail': thumb.strip()}
    return data

def parse_recipes(filename):
    data = {}
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = content.split('--------------------------------------------------')
    for block in blocks:
        block = block.strip()
        if not block: continue
        url_match = re.search(r'URL:\s+(https://\S+)', block)
        if url_match:
            url = normalize_url(url_match.group(1))
            lines = block.split('\n')
            # Ambil konten setelah baris URL
            idx = next(i for i, line in enumerate(lines) if line.startswith('URL:'))
            data[url] = '\n'.join(lines[idx+1:]).strip()
    return data

# Proses penggabungan
thumbs = parse_thumbnails('parsed_videos_with_thumbnails.txt')
id_recipes = parse_recipes('dataset_resep_indonesia.txt')
en_recipes = parse_recipes('dataset_resep_inggris.txt')

rows = []
for url, info in thumbs.items():
    rows.append({
        'url': url,
        'title': info['title'],
        'thumbnail': info['thumbnail'],
        'recipe_id': id_recipes.get(url, ""),
        'recipe_en': en_recipes.get(url, "")
    })

df = pd.DataFrame(rows)
df.to_csv('combined_recipes.csv', index=False)
print("DataFrame Berhasil Dibuat!")