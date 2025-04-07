# UI class
# inputs: none
# reads files: FileSelector.py, ScaleDataProcessor.py, Plotter.py

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

        self.slope_button = QPushButton("Measure Slope")
        self.slope_button.clicked.connect(self.measure_slope_instruction)

        layout = QVBoxLayout()
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.select_button)
        btn_row.addWidget(self.remove_button)
        btn_row.addWidget(self.slope_button)

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

            fig.update_layout(
                title="Scale Plot - Click Two Points to Calculate Slope",
                clickmode='event+select'
            )

            fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))

            fig.add_annotation(
                text="Click two points to see slope",
                xref="paper", yref="paper",
                x=0, y=1.1, showarrow=False, font=dict(size=12)
            )

            fig.write_html("slope_plot.html", include_plotlyjs='cdn', full_html=True, div_id='plot')

            # Inject JavaScript to enable slope measurement
            with open("slope_plot.html", "r") as f:
                html = f.read()

            custom_js = """
<script>
let selectedPoints = [];

document.addEventListener('DOMContentLoaded', function () {
    const plotDiv = document.getElementById('plot');

 plotDiv.on('plotly_click', function(data) {
    if (data.points.length > 0) {
        const pt = data.points[0];
        selectedPoints.push({ x: pt.x, y: pt.y });

        if (selectedPoints.length === 2) {
            const [pt1, pt2] = selectedPoints;
            const dx = pt2.x - pt1.x;
            const dy = pt2.y - pt1.y;
            const slope = dy / dx;

            const annotation = {
                x: (pt1.x + pt2.x) / 2,
                y: (pt1.y + pt2.y) / 2,
                text: 'Weight Drift: ' + dy.toFixed(6) + ' grams in ' + dx + ' seconds',
                showarrow: true,
                arrowhead: 3,
                ax: 0,
                ay: -40,
                bgcolor: "lightyellow",
                bordercolor: "black"
            };

            const tracesToAdd = [
                {
                    x: [pt1.x, pt2.x],
                    y: [pt1.y, pt2.y],
                    mode: 'lines',
                    line: { color: 'red', dash: 'dash' },
                    name: 'Slope Line'
                },
                {
                    x: [pt1.x, pt2.x],
                    y: [pt1.y, pt2.y],
                    mode: 'markers',
                    marker: { color: 'red', size: 10 },
                    name: 'Selected Points'
                }
            ];

            Plotly.deleteTraces('plot', Array.from({length: plotDiv.data.length}, (_, i) => i).filter(i => plotDiv.data[i].name === 'Slope Line' || plotDiv.data[i].name === 'Selected Point' || plotDiv.data[i].name === 'Selected Points'));
            Plotly.relayout('plot', { annotations: [] });
            Plotly.addTraces('plot', tracesToAdd);
            Plotly.relayout('plot', { annotations: [annotation] });

            selectedPoints = [];
        }
    }
});

});
</script>
"""

            html = html.replace("</body>", custom_js + "\n</body>")

            with open("slope_plot.html", "w") as f:
                f.write(html)

            webbrowser.open("slope_plot.html")

        except Exception as e:
            self.browser.setHtml(f"<h3>Error while plotting: {e}</h3>")
            print(f"Error during plotting: {e}")

    def measure_slope_instruction(self):
        QMessageBox.information(self, "How to Measure Slope",
                                "After the plot loads, click two data points.\n"
                                "The slope will be calculated and displayed as an annotation.")