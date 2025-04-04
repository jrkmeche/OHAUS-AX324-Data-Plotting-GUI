import sys
import os
import tempfile
import pandas as pd
import plotly.graph_objects as go
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QWidget, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView


class FileSelector:
    def select_files(self):
        app = QApplication(sys.argv)
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            None, "Select one or more files", "", "Text Files (*.txt)"
        )
        app.quit()
        return file_paths if file_paths else None


class ScaleDataProcessor:
    def __init__(self, file_paths):
        self.file_paths = file_paths

    def process_all(self):
        all_data = []
        for path in self.file_paths:
            all_data.extend(self._process_single(path))

        df = pd.DataFrame(all_data)
        df["timeRawSec"] = [i * 10 for i in range(len(df))]
        df["timeRawMin"] = (df["timeRawSec"] / 60).round(2)
        return df

    def _process_single(self, file_path):
        with open(file_path, 'r') as file:
            content = ''.join(file.readlines())

        scale_readings = content.strip().split("\n\n")
        data = []
        file_label = os.path.basename(file_path)

        for weight in scale_readings:
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
                "SourceFile": file_label
            })

        return data


class DerivativePlotter:
    def __init__(self, df, epsilon=1e-4):
        self.df = df
        self.epsilon = epsilon

    def build_plot(self):
        fig = go.Figure()

        for file_name in self.df['SourceFile'].unique():
            df_subset = self.df[self.df['SourceFile'] == file_name].copy()
            df_subset = df_subset.reset_index(drop=True)
            df_subset['AlignedTime'] = df_subset.index * 10

            fig.add_trace(go.Scatter(
                x=df_subset['AlignedTime'],
                y=df_subset['Weight'],
                mode='lines',
                name=f'{file_name}'
            ))

            derivative = df_subset['Weight'].diff()
            zero_indices = derivative[derivative.abs() < self.epsilon].index
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
        return fig


class ScaleLinePlotUI(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.setWindowTitle("Pump Scale Data")
        self.setGeometry(100, 100, 800, 600)

        self.browser = QWebEngineView()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.show_plot()

    def show_plot(self):
        plotter = DerivativePlotter(self.df)
        fig = plotter.build_plot()
        html_path = tempfile.NamedTemporaryFile(delete=False, suffix='.html').name
        fig.write_html(html_path)
        self.browser.load(QUrl.fromLocalFile(html_path))


class DashboardApp:
    def run(self):
        file_selector = FileSelector()
        file_paths = file_selector.select_files()

        if not file_paths:
            print("No file selected")
            return

        processor = ScaleDataProcessor(file_paths)
        df = processor.process_all()

        app = QApplication(sys.argv)
        viewer = ScaleLinePlotUI(df)
        viewer.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    DashboardApp().run()
