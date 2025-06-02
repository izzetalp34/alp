from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from stok import StokEkrani
import sys

class AnaEkran(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ambalaj Dükkanı - Ana Ekran")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.layout = QVBoxLayout()

        self.baslik = QLabel("📦 Ambalaj Dükkanı Yönetim Sistemi")
        self.baslik.setFont(QFont("Arial", 16, QFont.Bold))
        self.baslik.setAlignment(Qt.AlignCenter)
        self.baslik.setStyleSheet("color: #333;")
        self.layout.addWidget(self.baslik)

        self.layout.addWidget(self._cizgi())

        self.stok_btn = self._buton_olustur("📦 Stok Ekranı", self.stok_ekranini_ac)
        self.satis_btn = self._buton_olustur("💸 Satış Ekranı")
        self.raporlama_btn = self._buton_olustur("📊 Raporlama")
        self.musteri_btn = self._buton_olustur("👥 Müşteri")

        for btn in [self.stok_btn, self.satis_btn, self.raporlama_btn, self.musteri_btn]:
            self.layout.addWidget(btn)

        self.setLayout(self.layout)

    def _buton_olustur(self, metin, handler=None):
        btn = QPushButton(metin)
        btn.setFixedHeight(50)
        btn.setFont(QFont("Arial", 12))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        if handler:
            btn.clicked.connect(handler)
        return btn

    def _cizgi(self):
        cizgi = QFrame()
        cizgi.setFrameShape(QFrame.HLine)
        cizgi.setFrameShadow(QFrame.Sunken)
        cizgi.setStyleSheet("color: #aaa;")
        return cizgi

    def stok_ekranini_ac(self):
        self.stok_pencere = StokEkrani()
        self.stok_pencere.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = AnaEkran()
    pencere.show()
    sys.exit(app.exec_())
