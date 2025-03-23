""" #libraries
from PyQt5.QtWidgets import QFileDialog, QApplication
import sys
import pandas as pd
import plotly.express as px

#local
from GraphDataDashboard import GraphDataDashboardExplorer
 """

import sys
import tempfile
import plotly.express as px
from PyQt5.QtWidgets import QApplication
from GraphDataDashboard import ScaleLinePlot
from GraphDataDashboard import GraphDataDashboardExplorer


fileSelector = GraphDataDashboardExplorer()
file_path, data, df = fileSelector.selectFile()

if df is not None:
    print(df.head())
else:
    print("No file selected or data could not be processed")

fig = px.line(df, x='timeRawSec', y='Weight', title='Weight over Time (Seconds)')
html_path = tempfile.NamedTemporaryFile(delete=False, suffix='.html').name
fig.write_html(html_path)

app = QApplication(sys.argv)
viewer = ScaleLinePlot(html_path)
viewer.show()
sys.exit(app.exec_())


""" 
#for selcting the file to analyze
def selectFile():
    app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(None, "Select File")
    app.quit()

    if not file_path:
        return None, None

    with open(file_path, 'r') as file:
        content = ''.join(file.readlines())

    # Split measurements by blank lines
    measurements = content.strip().split("\n\n")

    # Parse the measurements into a structured format
    # Removes uneccassary formatting like date, time, units ect
    data = []
    for measurement in measurements:
        lines = measurement.strip().split("\n")
        if len(lines) < 2:
            continue

        date, time = lines[0].split()

        net_line_parts = lines[1].split()
        net_value = float(net_line_parts[1])
        unit = net_line_parts[2]

        data.append({
            "Date": date,
            "Time": time,
            "Weight": net_value,
            "Unit": unit
        })

        
            

        df = pd.DataFrame(data)
        df["timeRawSec"] = [i * 10 for i in range(len(df))]
        df['timeRawMin'] = df["timeRawSec"] / 60
        df['timeRawMin'] = df['timeRawMin'].round(2)

    

    return file_path, data, df """

##if __name__ == '__main__':
"""     selected_file, measurements, measurmentsDF = selectFile()
    print(measurmentsDF)
    fig = px.line(measurmentsDF,x = "timeRawMin", y = "Weight")
    fig.show() """



"""     if selected_file:
        print("Selected file:", selected_file)
        print("Parsed measurements:")
        print(measurements[0])
        print()
        print(measurements[1])
        #for m in measurements:
         #   print(m)
    else:
        print("No file selected") """
