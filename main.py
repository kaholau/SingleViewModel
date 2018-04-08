import window
import sys
from PyQt5.QtWidgets import QApplication


app = QApplication(sys.argv)
window = window.MainWindow()
window.setDebug(True)
window.show()

sys.exit(app.exec_())
