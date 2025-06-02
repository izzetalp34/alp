from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QApplication, QListWidget
)
from PyQt5.QtCore import Qt
from veritabani.baglanti import get_connection
import sys
from datetime import datetime

class SatisEkrani(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satış Ekranı")
        self.setGeometry(150, 150, 900, 600)

        self.layout = QVBoxLayout()

        self.musteri_input = QLineEdit()
        self.musteri_input.setPlaceholderText("Müşteri Adı")
        self.musteri_input.textChanged.connect(self.musteri_iskonto_getir)

        self.musteri_iskonto_label = QLabel("Müşteri İskontosu: 0%")

        self.ekstra_iskonto_input = QLineEdit()
        self.ekstra_iskonto_input.setPlaceholderText("Ekstra İskonto (%)")

        self.urun_arama_input = QLineEdit()
        self.urun_arama_input.setPlaceholderText("Ürün ara...")
        self.urun_arama_input.textChanged.connect(self.urun_ara)

        self.urun_listesi = QListWidget()
        self.urun_listesi.itemClicked.connect(self.urun_secildi)

        self.miktar_input = QLineEdit()
        self.miktar_input.setPlaceholderText("Miktar")

        self.urun_ekle_btn = QPushButton("Ürün Ekle")
        self.urun_ekle_btn.clicked.connect(self.urun_ekle)

        self.tablo = QTableWidget(0, 4)
        self.tablo.setHorizontalHeaderLabels(["Ürün Adı", "Miktar", "Birim Fiyat", "Ara Toplam"])

        self.satis_tamamla_btn = QPushButton("Satışı Tamamla")
        self.satis_tamamla_btn.clicked.connect(self.satisi_kaydet)

        self.layout.addWidget(QLabel("Müşteri Adı:"))
        self.layout.addWidget(self.musteri_input)
        self.layout.addWidget(self.musteri_iskonto_label)
        self.layout.addWidget(QLabel("Ekstra İskonto (%):"))
        self.layout.addWidget(self.ekstra_iskonto_input)
        self.layout.addWidget(self.urun_arama_input)
        self.layout.addWidget(self.urun_listesi)
        self.layout.addWidget(self.miktar_input)
        self.layout.addWidget(self.urun_ekle_btn)
        self.layout.addWidget(self.tablo)
        self.layout.addWidget(self.satis_tamamla_btn)

        self.setLayout(self.layout)
        self.musteri_iskonto = 0.0
        self.secilen_urun = None

    def musteri_iskonto_getir(self):
        musteri_adi = self.musteri_input.text().strip()
        if not musteri_adi:
            self.musteri_iskonto = 0.0
            self.musteri_iskonto_label.setText("Müşteri İskontosu: 0%")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT iskonto_orani FROM musteriler WHERE ad = %s", (musteri_adi,))
            sonuc = cur.fetchone()
            if sonuc:
                self.musteri_iskonto = float(sonuc[0])
                self.musteri_iskonto_label.setText(f"Müşteri İskontosu: %{int(self.musteri_iskonto)}")
            else:
                self.musteri_iskonto = 0.0
                self.musteri_iskonto_label.setText("Müşteri İskontosu: 0%")
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def urun_ara(self):
        kelime = self.urun_arama_input.text().strip()
        if not kelime:
            self.urun_listesi.clear()
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT ad FROM urunler WHERE ad ILIKE %s", (f"%{kelime}%",))
            urunler = cur.fetchall()
            self.urun_listesi.clear()
            for urun in urunler:
                self.urun_listesi.addItem(urun[0])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def urun_secildi(self, item):
        self.urun_arama_input.setText(item.text())
        self.secilen_urun = item.text()

    def urun_ekle(self):
        urun_ad = self.secilen_urun or self.urun_arama_input.text().strip()
        miktar = self.miktar_input.text().strip()
        if not urun_ad or not miktar:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen ürün seçin ve miktar girin.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, satis_fiyati FROM urunler WHERE ad = %s", (urun_ad,))
            urun = cur.fetchone()
            if not urun:
                QMessageBox.warning(self, "Bulunamadı", "Ürün bulunamadı.")
                return
            urun_id, birim_fiyat = urun
            miktar = float(miktar)
            ara_toplam = round(miktar * birim_fiyat, 2)

            satir = self.tablo.rowCount()
            self.tablo.insertRow(satir)
            self.tablo.setItem(satir, 0, QTableWidgetItem(urun_ad))
            self.tablo.setItem(satir, 1, QTableWidgetItem(str(miktar)))
            self.tablo.setItem(satir, 2, QTableWidgetItem(str(birim_fiyat)))
            self.tablo.setItem(satir, 3, QTableWidgetItem(str(ara_toplam)))
            conn.close()

            self.urun_arama_input.clear()
            self.urun_listesi.clear()
            self.miktar_input.clear()
            self.secilen_urun = None
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def satisi_kaydet(self):
        musteri = self.musteri_input.text().strip()
        try:
            ekstra_iskonto = float(self.ekstra_iskonto_input.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Hatalı Giriş", "Ekstra iskonto geçerli değil.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            toplam = 0
            satir_sayisi = self.tablo.rowCount()
            satis_satirlari = []

            for i in range(satir_sayisi):
                urun_ad = self.tablo.item(i, 0).text()
                miktar = float(self.tablo.item(i, 1).text())
                birim_fiyat = float(self.tablo.item(i, 2).text())
                cur.execute("SELECT id FROM urunler WHERE ad = %s", (urun_ad,))
                urun_id = cur.fetchone()[0]
                ara_toplam = miktar * birim_fiyat
                toplam += ara_toplam
                satis_satirlari.append((urun_id, miktar, birim_fiyat))

            toplam_iskonto = self.musteri_iskonto + ekstra_iskonto
            indirimli_toplam = round(toplam * (1 - toplam_iskonto / 100), 2)

            cur.execute("""
                INSERT INTO satislar (musteri, tarih, toplam_tutar, iskonto_orani)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (musteri, datetime.now(), indirimli_toplam, toplam_iskonto))
            satis_id = cur.fetchone()[0]

            for urun_id, miktar, birim_fiyat in satis_satirlari:
                cur.execute("""
                    INSERT INTO satis_detaylari (satis_id, urun_id, miktar, birim_fiyat)
                    VALUES (%s, %s, %s, %s)
                """, (satis_id, urun_id, miktar, birim_fiyat))

                cur.execute("""
                    UPDATE urunler
                    SET stok_miktari = stok_miktari - %s,
                        guncellenme_tarihi = NOW()
                    WHERE id = %s
                """, (miktar, urun_id))

            cur.execute("""
                INSERT INTO stok_hareketleri (urun_id, hareket_tipi, miktar, tarih, aciklama, ref_kaynak)
                VALUES (%s, 'cikis', %s, NOW(), %s, %s)
            """, (urun_id, miktar, f"Müşteri: {musteri}", f"Satış Fişi #{satis_id}"))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Başarılı", f"Satış kaydedildi. Toplam: {indirimli_toplam} TL")
            self.tablo.setRowCount(0)
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = SatisEkrani()
    pencere.show()
    sys.exit(app.exec_())
