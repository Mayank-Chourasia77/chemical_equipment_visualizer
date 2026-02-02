import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QFileDialog, QVBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_UPLOAD_URL = "http://localhost:8000/api/upload/"

class DesktopApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer (Desktop)")

        layout = QVBoxLayout()
        self.label = QLabel("Upload a CSV file to analyze equipment data")

        button = QPushButton("Upload CSV")
        button.clicked.connect(self.upload_csv)

        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.label)
        layout.addWidget(button)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File")
        if not file_path:
            return

        response = requests.post(
            API_UPLOAD_URL,
            files={"file": open(file_path, "rb")}
        )
        data = response.json()

        self.label.setText(
            f"Total: {data['total_equipment']}\n"
            f"Avg Flowrate: {data['avg_flowrate']}\n"
            f"Avg Pressure: {data['avg_pressure']}\n"
            f"Avg Temperature: {data['avg_temperature']}"
        )

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.bar(data["type_distribution"].keys(),
               data["type_distribution"].values())
        ax.set_title("Equipment Type Distribution")
        self.canvas.draw()
