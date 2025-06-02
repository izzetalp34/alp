from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QApplication, QLineEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt
from veritabani.baglanti import get_connection
from alis import AlisEkrani
import sys

class StokEkrani(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stok Ekranı")
        self.setGeometry(100, 100, 900, 600)

        self.layout = QVBoxLayout()

        arama_layout = QHBoxLayout()
        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText("Ürün ara (örn: karton, 7, 7oz, bardak)...")
        self.arama_input.textChanged.connect(self.urun_ara)
        arama_layout.addWidget(QLabel("Arama:"))
        arama_layout.addWidget(self.arama_input)
        self.layout.addLayout(arama_layout)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Ürün Adı", "Birim", "Stok Miktarı", "Maliyet"])
        self.tablo.cellDoubleClicked.connect(self.urun_secildi)

        self.yenile_btn = QPushButton("Stokları Yenile")
        self.yenile_btn.clicked.connect(self.stoklari_getir)

        self.alis_btn = QPushButton("Yeni Ürün Kaydet / Mal Girişi Yap")
        self.alis_btn.clicked.connect(self.ac_alis_ekrani)

        self.layout.addWidget(QLabel("Stok Listesi"))
        self.layout.addWidget(self.tablo)
        self.layout.addWidget(self.yenile_btn)
        self.layout.addWidget(self.alis_btn)

        self.setLayout(self.layout)
        self.stoklari_getir()

    def stoklari_getir(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, ad, birim_tipi, stok_miktari, alis_fiyati FROM urunler ORDER BY id")
            rows = cur.fetchall()
            self.tablo.setRowCount(0)
            for row in rows:
                id, ad, birim, stok, alis = row
                maliyet = round(float(alis) * 1.2, 2)
                veri_listesi = [id, ad, birim, stok, maliyet]
                satir = self.tablo.rowCount()
                self.tablo.insertRow(satir)
                for sutun, veri in enumerate(veri_listesi):
                    item = QTableWidgetItem(str(veri))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.tablo.setItem(satir, sutun, item)
            conn.close()
        except Exception as e:
            print("Stok verisi çekilemedi:", str(e))

    def urun_ara(self):
        kelime = self.arama_input.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, ad, birim_tipi, stok_miktari, alis_fiyati FROM urunler
                WHERE ad ILIKE %s OR birim_tipi ILIKE %s
            """, (f"%{kelime}%", f"%{kelime}%"))
            rows = cur.fetchall()
            self.tablo.setRowCount(0)
            for row in rows:
                id, ad, birim, stok, alis = row
                maliyet = round(float(alis) * 1.2, 2)
                veri_listesi = [id, ad, birim, stok, maliyet]
                satir = self.tablo.rowCount()
                self.tablo.insertRow(satir)
                for sutun, veri in enumerate(veri_listesi):
                    item = QTableWidgetItem(str(veri))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.tablo.setItem(satir, sutun, item)
            conn.close()
        except Exception as e:
            print("Arama hatası:", str(e))

    def ac_alis_ekrani(self, urun_adi=None):
        self.alis_ekrani = AlisEkrani(urun_adi)
        self.alis_ekrani.show()

    def urun_secildi(self, row, column):
        urun_adi = self.tablo.item(row, 1).text()
        self.ac_alis_ekrani(urun_adi)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = StokEkrani()
    pencere.show()
    sys.exit(app.exec_())
