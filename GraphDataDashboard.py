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
import plotly.graph_objects as pgo
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QWidget, QMainWindow



class GraphDataDashboardExplorer():
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
class ScaleLinePlot(QMainWindow):  # Inherit from QMainWindow
    def __init__(self, df):
        super().__init__()  # Calls QMainWindow constructor

        self.df = df

        self.setWindowTitle("Pump Scale Data")
        self.setGeometry(100, 100, 800, 600)

        self.browser = QWebEngineView()

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        container.setLayout(layout)
        self.setCentralWidget(container)

        #call derivativeZero for calculating and plotting where the derivative changes from positive to negative
        self.derivativeZero(self.df['Weight'], self.df['timeRawSec'])  # Plot on load

    #for finding where the scale data in a the dataframe has a derivative = 0. This signifies a change in graph direction (or inflection point). 
    #The tolerance of the derivative funtion is controlled by the epsilon vale (+/- epsilon is the tolerance)
    #plots the locations of derivative inflection points
    def derivativeZero(self, column: pd.Series, time_column: pd.Series, epsilon: float = 1e-4):
        
        #determine the derivative of the time series scale data, imported as pd.Series
        derivative = column.diff()

        #find where the derivative is close to zero using epsilon as the tolerance
        zero_indices = derivative[derivative.abs() < epsilon].index

        #determing the time (x) and scale weight (y) values at which the zero indices exist
        x_zero = time_column.loc[zero_indices]
        y_zero = column.loc[zero_indices]

        #create base plot
        fig = pgo.Figure()
        fig.add_trace(pgo.Scatter(x=time_column, y=column, mode='lines', name='Original Data'))

        #add the points where the derivative equals zero
        fig.add_trace(pgo.Scatter(x=x_zero, y=y_zero, mode='markers', name='Zero Derivative',
                                 marker=dict(color='red', size=8, symbol='circle')))

        fig.update_layout(title='Weight Over Time with Zero Derivative Points',
                          xaxis_title='Time (s)', yaxis_title='Weight')

        #display plot
        html_path = tempfile.NamedTemporaryFile(delete=False, suffix='.html').name
        fig.write_html(html_path)
        self.browser.load(QUrl.fromLocalFile(html_path))    
            
            

    