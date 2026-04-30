# Proyek Analisis Data: Brazilian E-Commerce 

## Deskripsi Proyek
Proyek ini melakukan analisis data pada dataset Brazilian E-Commerce publik dari Olist. Analisis mencakup tren revenue, segmentasi pelanggan (RFM Analysis), analisis kategori produk, review pelanggan, waktu pengiriman, dan distribusi geografis pelanggan.

## Pertanyaan Bisnis
1. Bagaimana tren total revenue bulanan Olist selama periode 2016–2018, 
   dan pada bulan apa revenue tertinggi terjadi?
2. Bagaimana segmentasi pelanggan Olist berdasarkan metode RFM 
   (Recency, Frequency, Monetary) dan kategori pelanggan mana 
   yang paling dominan selama periode 2016–2018?

## Setup Environment - Anaconda

```bash
conda create --name proyek-analisis python=3.10.20
conda activate proyek-analisis
pip install -r requirements.txt
```
## Setup Environment - Shell/Terminal

```bash
mkdir submission
cd submission
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App

```bash
streamlit run dashboard/dashboard.py
```