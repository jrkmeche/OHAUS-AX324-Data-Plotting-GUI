from PyQt5.QtWidgets import QFileDialog, QApplication
import sys
import pandas as pd

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

    return file_path, data, df

if __name__ == '__main__':
    selected_file, measurements, measurmentsDF = selectFile()
    print(measurmentsDF)


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
