import sys
import tempfile
import plotly.express as px
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from GraphDataDashboard import ScaleLinePlot
from GraphDataDashboard import GraphDataDashboardExplorer

fileSelector = GraphDataDashboardExplorer()
file_paths, data, df = fileSelector.selectFile()

if df is not None:
    print(df.head())
    app = QApplication(sys.argv)
    viewer = ScaleLinePlot(df)
    viewer.show()
    sys.exit(app.exec_())
else:
    print("No file selected or data could not be processed")