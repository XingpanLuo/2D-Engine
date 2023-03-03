import sys
from PyQt5.QtWidgets import QApplication

from MainWidget import MainWidget

if __name__ == '__main__':
     
    app = QApplication(sys.argv)
    ex = MainWidget()
    ex.show()
    sys.exit(app.exec_())