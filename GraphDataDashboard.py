#-----object for the user interface-----
#----------has functions----------------
#----------------selectFile-------------


#allow the user to browse to a file in the file explorer to process
#only works with .txt extions that were recorded from a XXXXX scale


import sys
import tempfile
import pandas as pd
import numpy as np
import plotly.express as px
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl



class GraphDataDashboardExplorer:
    def __init__(self):
        self.filePath = None
        self.data = []
        self.df = None


    #allow the user to browse to a file in the file explorer to process
    #only works with .txt extions from an XXXX scale
    def selectFile(self):
        app = QApplication(sys.argv)
        fileExplore = QFileDialog()
        self.filePath, _ = fileExplore.getOpenFileName(None, "Select a file")
        app.quit()

        if not self.filePath:
            print("File not selected")
            return None
        
        self._processData()
        return self.filePath, self.data, self.df

    def _processData(self):
        with open(self.filePath, 'r') as file:
            content = ''.join(file.readlines())
        
        scaleReading = content.strip().split("\n\n")
        self.data = []

        for weight in scaleReading:
            lines = weight.strip().split("\n")
            if len(lines) < 2:
                continue

            date, time = lines[0].split()
            net_lines_parts = lines[1].split()

            try:
                date, time = lines[0].split()
                net_line_parts = lines[1].split()
                net_value = float(net_line_parts[1])
                unit = net_line_parts[2]
            except (IndexError, ValueError):
                continue

            self.data.append({
                "Date": date,
                "Time": time,
                "Weight": net_value,
                "Unit": unit
            })

        if self.data:
            self.df = pd.DataFrame(self.data)
            self.df["timeRawSec"] = [i * 10 for i in range(len(self.df))]
            self.df["timeRawMin"] = (self.df["timeRawSec"] / 60).round(2)      



#PyQt plotting application
class ScaleLinePlot:
    def __init__(self, html_path):

        self.html_path = html_path
        #calls __init__ method, initializes QMainWindow in PyQt
        super().__init__()

        self.setWindowTitle("Pump Scale Data")
        #sets the size of the window (x-coord, y-coord, window width, windo height
        self.setGeometry(100, 100, 800, 600)

        self.browser = QWebEngineView()
        self.browser.load(QUrl.fromLocalFile(html_path)) 

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        container.setLayout(layout)
        self.setCentralWidget(container)


            
            
            

    