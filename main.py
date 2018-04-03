import window
import sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
window = window.MainWindow()
window.show()
sys.exit(app.exec_())
