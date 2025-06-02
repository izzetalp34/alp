# 🧾 ALP - Ambalaj Dükkanı ERP Uygulaması

**ALP**, ambalaj dükkanları için geliştirilmiş sade ve kullanıcı dostu bir masaüstü ERP uygulamasıdır. PyQt5 ile geliştirilmiştir ve PostgreSQL veritabanı kullanır.

## 🚀 Özellikler

- 📦 **Stok Yönetimi:**
  - Ürün listeleme, filtreleme, arama
  - Dinamik maliyet hesaplama (alış fiyatı + %20)
  - Ürün detayına çift tıklayarak alış ekranına geçiş

- 🧾 **Alış Modülü:**
  - Tedarikçiye göre ürün alımı
  - Var olan ürünlere stok ekleme
  - `alislar`, `alis_detaylari`, `stok_hareketleri` entegrasyonu

- 💸 **Satış Modülü:**
  - Müşteri seçimi + iskonto desteği
  - Ürün arama, filtreleme, tabloya ekleme
  - Otomatik iskonto + ekstra iskonto ile toplam hesaplama
  - `satislar`, `satis_detaylari`, `stok_hareketleri` entegrasyonu

- 🖥️ **Ana Ekran:**
  - Satış, stok, raporlama, müşteri gibi ekranlara geçiş


## 🛠️ Kurulum

```bash
# PostgreSQL veritabanınızı başlatın ve 'alp' veritabanını oluşturun
createdb alp

# Ortamı oluşturun
python3 -m venv venv
source venv/bin/activate

# Gereken kütüphaneleri yükleyin
pip install -r requirements.txt

# Ana ekranı başlatın
python anaekran.py
```

## 🗃️ Veritabanı
Aşağıda kullanılan temel tablo şemaları örnek olarak sunulmuştur:

```sql
CREATE TABLE urunler (
    id SERIAL PRIMARY KEY,
    ad TEXT NOT NULL,
    birim_tipi TEXT NOT NULL,
    stok_miktari NUMERIC DEFAULT 0,
    alis_fiyati NUMERIC,
    satis_fiyati NUMERIC,
    barkod TEXT,
    guncellenme_tarihi TIMESTAMP
);

CREATE TABLE alislar (
    id SERIAL PRIMARY KEY,
    tedarikci TEXT,
    tarih TIMESTAMP,
    toplam_tutar NUMERIC,
    aciklama TEXT
);

CREATE TABLE alis_detaylari (
    id SERIAL PRIMARY KEY,
    alis_id INTEGER REFERENCES alislar(id) ON DELETE CASCADE,
    urun_id INTEGER REFERENCES urunler(id),
    miktar NUMERIC,
    birim_fiyat NUMERIC
);

CREATE TABLE satislar (
    id SERIAL PRIMARY KEY,
    musteri TEXT,
    tarih TIMESTAMP,
    toplam_tutar NUMERIC,
    iskonto_orani NUMERIC
);

CREATE TABLE satis_detaylari (
    id SERIAL PRIMARY KEY,
    satis_id INTEGER REFERENCES satislar(id) ON DELETE CASCADE,
    urun_id INTEGER REFERENCES urunler(id),
    miktar NUMERIC,
    birim_fiyat NUMERIC
);

CREATE TABLE stok_hareketleri (
    id SERIAL PRIMARY KEY,
    urun_id INTEGER REFERENCES urunler(id),
    hareket_tipi TEXT CHECK(hareket_tipi IN ('giris', 'cikis')),
    miktar NUMERIC,
    tarih TIMESTAMP,
    aciklama TEXT,
    ref_kaynak TEXT
);

CREATE TABLE musteriler (
    id SERIAL PRIMARY KEY,
    ad TEXT NOT NULL,
    iskonto_orani NUMERIC DEFAULT 0
);
```

> Bu şemalar PostgreSQL için hazırlanmıştır ve `alp` veritabanında kullanılabilir.

## 📁 Dosya Yapısı
```
alp/
├── alis.py
├── anaekran.py
├── satis.py
├── stok.py
└── veritabani/
    └── baglanti.py
```

## 🤝 Katkı
PR’ler ve öneriler memnuniyetle karşılanır.

## 🧑‍💻 Geliştirici
[izzetalp34](https://github.com/izzetalp34)
