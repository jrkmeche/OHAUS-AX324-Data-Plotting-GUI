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
        self.filePaths = []  # Multiple files
        self.data = []
        self.df = None

    def selectFile(self):
        """
        Opens a file dialog to select multiple text files,
        processes each file, and combines the results into one DataFrame.
        """
        app = QApplication(sys.argv)
        fileExplore = QFileDialog()
        self.filePaths, _ = fileExplore.getOpenFileNames(
            None, "Select one or more files", "", "Text Files (*.txt)"
        )
        app.quit()

        if not self.filePaths:
            print("No files selected")
            return None, None, None

        all_data = []
        for path in self.filePaths:
            file_data = self._processData(path)
            all_data.extend(file_data)

        if all_data:
            self.df = pd.DataFrame(all_data)
            self.df["timeRawSec"] = [i * 10 for i in range(len(self.df))]
            self.df["timeRawMin"] = (self.df["timeRawSec"] / 60).round(2)
            return self.filePaths, all_data, self.df

        return None, None, None
    

    #removes raw syntax from .txt selected by the user
    #returns processed data as a list. Globally muted and only used within this class
    def _processData(self, file_path):
        import os

        with open(file_path, 'r') as file:
            content = ''.join(file.readlines())

        scaleReading = content.strip().split("\n\n")
        data = []
        file_label = os.path.basename(file_path)

        for weight in scaleReading:
            lines = weight.strip().split("\n")
            if len(lines) < 2:
                continue

            try:
                date, time = lines[0].split()
                net_line_parts = lines[1].split()
                net_value = float(net_line_parts[1])
                unit = net_line_parts[2]
            except (IndexError, ValueError):
                continue

            data.append({
                "Date": date,
                "Time": time,
                "Weight": net_value,
                "Unit": unit,
                "SourceFile": file_label  # 🆕 tag with filename
            })

        return data




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
        import plotly.graph_objects as go
        import tempfile

        fig = go.Figure()

        for file_name in self.df['SourceFile'].unique():
            df_subset = self.df[self.df['SourceFile'] == file_name].copy()

            # Reset time to start at 0 and increment by 10s per point
            df_subset = df_subset.reset_index(drop=True)
            df_subset['AlignedTime'] = df_subset.index * 10

            # Plot line
            fig.add_trace(go.Scatter(
                x=df_subset['AlignedTime'],
                y=df_subset['Weight'],
                mode='lines',
                name=f'{file_name}'
            ))

            # Compute and plot zero-derivative points
            derivative = df_subset['Weight'].diff()
            zero_indices = derivative[derivative.abs() < epsilon].index
            x_zero = df_subset['AlignedTime'].loc[zero_indices]
            y_zero = df_subset['Weight'].loc[zero_indices]

            fig.add_trace(go.Scatter(
                x=x_zero,
                y=y_zero,
                mode='markers',
                name=f'{file_name} Zero Deriv',
                marker=dict(color='red', size=8, symbol='circle')
            ))

        fig.update_layout(title='Scale Plots (All Start at t=0)',
                        xaxis_title='Time (s)', yaxis_title='Weight (g)')

        html_path = tempfile.NamedTemporaryFile(delete=False, suffix='.html').name
        fig.write_html(html_path)
        self.browser.load(QUrl.fromLocalFile(html_path))
    

            
            

    