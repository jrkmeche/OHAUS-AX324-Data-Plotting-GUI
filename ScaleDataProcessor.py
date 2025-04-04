import os
import pandas as pd

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
