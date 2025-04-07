#DashboardApp class
#inputs: none
#reads files: ScaleLinePlotUI.py
#displays plots

from PyQt5.QtWidgets import QApplication
import sys
from UserInterface import ScaleLinePlotUI

class DashboardApp:
    def run(self):
        app = QApplication(sys.argv)
        viewer = ScaleLinePlotUI()
        viewer.show()
        sys.exit(app.exec_())