import os
import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QFileDialog, QVBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_UPLOAD_URL = os.getenv("CHEM_EQUIP_API_URL", "http://localhost:8000/api/upload/")

class DesktopApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer (Desktop)")

        layout = QVBoxLayout()
        self.label = QLabel("Upload a CSV file to analyze equipment data")

        self.button = QPushButton("Upload CSV")
        self.button.clicked.connect(self.upload_csv)

        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File")
        if not file_path:
            return

        self.button.setEnabled(False)
        self.label.setText("Uploading...")

        try:
            with open(file_path, "rb") as handle:
                response = requests.post(
                    API_UPLOAD_URL,
                    files={"file": handle},
                    timeout=20,
                )

            if response.status_code >= 400:
                try:
                    payload = response.json()
                    error_message = payload.get("error", response.text)
                except ValueError:
                    error_message = response.text
                self.label.setText(f"Upload failed: {error_message}")
                return

            try:
                data = response.json()
            except ValueError:
                self.label.setText("Upload failed: invalid JSON response")
                return

            stats = data.get("stats", {})
            total = stats.get("total_equipment", "N/A")
            avg_flowrate = stats.get("average_flowrate", "N/A")
            avg_pressure = stats.get("average_pressure", "N/A")
            avg_temperature = stats.get("average_temperature", "N/A")

            self.label.setText(
                "Upload successful\n"
                f"Total: {total}\n"
                f"Avg Flowrate: {avg_flowrate}\n"
                f"Avg Pressure: {avg_pressure}\n"
                f"Avg Temperature: {avg_temperature}"
            )

            distribution = stats.get("equipment_distribution", {})
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            if distribution:
                ax.bar(distribution.keys(), distribution.values())
                ax.set_title("Equipment Type Distribution")
            else:
                ax.set_title("No equipment distribution data")
            self.canvas.draw()
        except requests.RequestException as exc:
            self.label.setText(f"Upload failed: {exc}")
        except Exception as exc:
            self.label.setText(f"Unexpected error: {exc}")
        finally:
            self.button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DesktopApp()
    window.show()
    sys.exit(app.exec_())
