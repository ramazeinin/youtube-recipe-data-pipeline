import streamlit as st
import pandas as pd

st.set_page_config(page_title="Devina Hermawan Recipe Finder", layout="wide")

# Load data yang sudah kita buat
@st.cache_data
def load_data():
    return pd.read_csv('combined_recipes.csv')

df = load_data()

# Sidebar untuk Pengaturan Bahasa
st.sidebar.title("Settings / Pengaturan")
lang = st.sidebar.radio("Pilih Bahasa / Select Language:", ("Bahasa Indonesia", "English"))

# Konfigurasi kolom berdasarkan bahasa
if lang == "Bahasa Indonesia":
    recipe_col = 'recipe_id'
    search_label = "Masukkan bahan (pisahkan dengan koma):"
    placeholder = "contoh: udang, bawang putih, telur"
    no_res_msg = "Resep tidak ditemukan."
    btn_text = "Lihat Video di YouTube"
else:
    recipe_col = 'recipe_en'
    search_label = "Enter ingredients (separate with comma):"
    placeholder = "e.g.: shrimp, garlic, egg"
    no_res_msg = "No recipes found."
    btn_text = "Watch Video on YouTube"

st.title("🍳 Recipe Search Assistant")

# Input Pencarian
query = st.text_input(search_label, placeholder=placeholder)

if query:
    # Logic pencarian: Semua bahan harus ada dalam teks resep
    ingredients = [i.strip().lower() for i in query.split(",") if i.strip()]
    
    # Filter data yang memiliki resep (tidak kosong) dan mengandung semua bahan
    mask = df[recipe_col].str.lower().fillna('').apply(lambda x: all(ing in x for ing in ingredients))
    results = df[mask]

    if not results.empty:
        st.write(f"Showing {len(results)} results:")
        for _, row in results.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(row['thumbnail'], use_container_width=True)
                with col2:
                    st.subheader(row['title'])
                    # Tampilkan cuplikan resep
                    st.text_area("Preview:", row[recipe_col][:300] + "...", height=150)
                    st.link_button(btn_text, row['url'])
                st.divider()
    else:
        st.warning(no_res_msg)
else:
    st.info("Silakan masukkan bahan masakan Anda untuk memulai.")