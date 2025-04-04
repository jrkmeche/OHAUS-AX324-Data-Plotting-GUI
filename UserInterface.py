#UI class
#inputs: none
#reads files: FileSelector.py,   ScaleDataProcessor.py,    Plotter.py

import tempfile
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QHBoxLayout
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from FileSelector import FileSelector
from ScaleDataProcessor import ScaleDataProcessor
from Plotter import DerivativePlotter
import pandas as pd
import webbrowser

class ScaleLinePlotUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pump Scale Data")
        self.setGeometry(100, 100, 1000, 700)

        self.loaded_files = []
        self.df = pd.DataFrame()

        self.browser = QWebEngineView()
        self.file_list_widget = QListWidget()

        self.select_button = QPushButton("Select Files")
        self.select_button.clicked.connect(self.add_files)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_files)

        layout = QVBoxLayout()
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.select_button)
        btn_row.addWidget(self.remove_button)

        layout.addLayout(btn_row)
        layout.addWidget(self.file_list_widget)
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_files(self):
        file_paths = FileSelector.get_files()
        new_files = [f for f in file_paths if f not in self.loaded_files]

        if not new_files:
            return

        self.loaded_files.extend(new_files)
        for f in new_files:
            self.file_list_widget.addItem(QListWidgetItem(f))

        self.update_plot()

    def remove_selected_files(self):
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select files to remove.")
            return

        for item in selected_items:
            self.loaded_files.remove(item.text())
            self.file_list_widget.takeItem(self.file_list_widget.row(item))

        self.update_plot()

    def update_plot(self):
        if not self.loaded_files:
            self.df = pd.DataFrame()
            self.browser.setHtml("<h3>No files loaded.</h3>")
            print("No files loaded.")
            return

        processor = ScaleDataProcessor(self.loaded_files)
        self.df = processor.process_all()
        print(f"Processed DataFrame:\n{self.df.head()}")

        if self.df.empty:
            self.browser.setHtml("<h3>No data to display. Check file format.</h3>")
            print("Empty DataFrame — possibly invalid file format.")
            return

        try:
            plotter = DerivativePlotter(self.df)
            fig = plotter.build_plot()

            html_path = tempfile.NamedTemporaryFile(delete=False, suffix='.html').name
            fig.write_html(html_path)
            print(f"Plot written to: {html_path}")

            webbrowser.open(f"file://{html_path}")
            #self.browser.load(QUrl.fromLocalFile(html_path))
        except Exception as e:
            self.browser.setHtml(f"<h3>Error while plotting: {e}</h3>")
            print(f"Error during plotting: {e}")
