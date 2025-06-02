from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QApplication, QComboBox
)
from veritabani.baglanti import get_connection
from datetime import datetime
import sys

class AlisEkrani(QWidget):
    def __init__(self, urun_adi=None):
        super().__init__()
        self.setWindowTitle("Alış Ekranı")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.tedarikci_input = QLineEdit()
        self.tedarikci_input.setPlaceholderText("Tedarikçi")

        self.urun_input = QLineEdit()
        self.urun_input.setPlaceholderText("Ürün Adı")
        if urun_adi:
            self.urun_input.setText(urun_adi)
        self.miktar_input = QLineEdit()
        self.miktar_input.setPlaceholderText("Miktar")
        self.birim_input = QComboBox()
        self.birim_input.addItems(["adet", "koli", "kg", "paket"])
        self.fiyat_input = QLineEdit()
        self.fiyat_input.setPlaceholderText("Birim Fiyat")

        ekle_btn = QPushButton("Ürün Ekle")
        ekle_btn.clicked.connect(self.urun_ekle)

        self.tablo = QTableWidget(0, 4)
        self.tablo.setHorizontalHeaderLabels(["Ürün", "Miktar", "Birim", "Fiyat"])

        kaydet_btn = QPushButton("Alışı Kaydet")
        kaydet_btn.clicked.connect(self.alis_kaydet)

        self.layout.addWidget(QLabel("Tedarikçi:"))
        self.layout.addWidget(self.tedarikci_input)

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.urun_input)
        form_layout.addWidget(self.miktar_input)
        form_layout.addWidget(self.birim_input)
        form_layout.addWidget(self.fiyat_input)
        form_layout.addWidget(ekle_btn)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.tablo)
        self.layout.addWidget(kaydet_btn)

        self.setLayout(self.layout)

    def urun_ekle(self):
        urun_ad = self.urun_input.text().strip()
        miktar = self.miktar_input.text().strip()
        birim = self.birim_input.currentText()
        fiyat = self.fiyat_input.text().strip()

        if not urun_ad or not miktar or not fiyat:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        satir = self.tablo.rowCount()
        self.tablo.insertRow(satir)
        self.tablo.setItem(satir, 0, QTableWidgetItem(urun_ad))
        self.tablo.setItem(satir, 1, QTableWidgetItem(miktar))
        self.tablo.setItem(satir, 2, QTableWidgetItem(birim))
        self.tablo.setItem(satir, 3, QTableWidgetItem(fiyat))

        self.urun_input.clear()
        self.miktar_input.clear()
        self.fiyat_input.clear()

    def alis_kaydet(self):
        tedarikci = self.tedarikci_input.text().strip()

        if not tedarikci:
            QMessageBox.warning(self, "Hata", "Tedarikçi bilgisi zorunludur.")
            return

        toplam = 0
        urunler = []
        for i in range(self.tablo.rowCount()):
            urun_ad = self.tablo.item(i, 0).text()
            miktar = float(self.tablo.item(i, 1).text())
            birim = self.tablo.item(i, 2).text()
            fiyat = float(self.tablo.item(i, 3).text())
            toplam += miktar * fiyat
            urunler.append((urun_ad, miktar, birim, fiyat))

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO alislar (tedarikci, tarih, toplam_tutar, aciklama)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (tedarikci, datetime.now(), toplam, ""))
            alis_id = cur.fetchone()[0]

            for urun_ad, miktar, birim, fiyat in urunler:
                cur.execute("SELECT id FROM urunler WHERE ad = %s AND birim_tipi = %s", (urun_ad, birim))
                urun = cur.fetchone()
                if urun:
                    urun_id = urun[0]
                    cur.execute("""
                        UPDATE urunler
                        SET stok_miktari = stok_miktari + %s,
                            alis_fiyati = %s,
                            guncellenme_tarihi = NOW()
                        WHERE id = %s
                    """, (miktar, fiyat, urun_id))
                else:
                    cur.execute("""
                        INSERT INTO urunler (ad, birim_tipi, stok_miktari, alis_fiyati, barkod, guncellenme_tarihi)
                        VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING id
                    """, (urun_ad, birim, miktar, fiyat, "",))
                    urun_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO alis_detaylari (alis_id, urun_id, miktar, birim_fiyat)
                    VALUES (%s, %s, %s, %s)
                """, (alis_id, urun_id, miktar, fiyat))

                cur.execute("""
                    INSERT INTO stok_hareketleri (urun_id, hareket_tipi, miktar, tarih, aciklama, ref_kaynak)
                    VALUES (%s, 'giris', %s, NOW(), %s, %s)
                """, (urun_id, miktar, f"Tedarikçi: {tedarikci}", f"Alış Fişi #{alis_id}"))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "Başarılı", "Alış başarıyla kaydedildi.")
            self.tablo.setRowCount(0)
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = AlisEkrani()
    pencere.show()
    sys.exit(app.exec_())
