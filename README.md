# Chemical Equipment Visualizer

A full-stack application for uploading chemical equipment CSV data, running Pandas analysis, visualizing summary statistics with interactive charts, and generating a downloadable PDF report. The project also includes an optional desktop app for local CSV analysis and visualization.

---

## Features

- Upload CSV files with equipment data (Name, Type, Flowrate, Pressure, Temperature)
- Store recent uploads in SQLite
- Compute summary statistics with Pandas
- Interactive dashboard with equipment type distribution charts
- Downloadable PDF report generated on the backend
- Optional desktop app for local CSV analysis and visualization

---

## Architecture

**Backend (Django + DRF)**
- REST API for CSV upload and analysis
- SQLite storage for uploaded files
- ReportLab PDF generation

**Frontend (React + Tailwind + Chart.js)**
- CSV upload UI
- Dashboard with charts and stats
- PDF download

**Desktop (Optional, Python + PyQt5 + Matplotlib)**
- Local CSV upload
- Local visualization
- Uses the same backend API by default

---

## Folder Structure

```
chemical_equipment_visualizer/
├─ backend/                 # Django backend
│  ├─ config/
│  ├─ equipment/
│  ├─ media/
│  ├─ manage.py
│  └─ requirements.txt
├─ frontend/                # React frontend
│  ├─ src/
│  ├─ public/
│  ├─ package.json
│  └─ .env
├─ desktop/                 # Optional desktop app
│  ├─ app.py
│  └─ requirements.txt
└─ README.md
```

---

## Requirements

- Python 3.9+ recommended
- Node.js 18 LTS (recommended)
- npm or yarn
- Optional: virtualenv

---

## Sample CSV Format

```
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,45,300
Reactor-7,Reactor,400,85,550
```

---

## Setup Instructions

### 1) Backend (Django)

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### 2) Frontend (React)

```bash
cd frontend
npm install
npm start
```

By default, the frontend reads the backend URL from `frontend/.env`:

```
REACT_APP_BACKEND_URL=http://127.0.0.1:8000
```

### 3) Desktop App (Optional)

```bash
cd desktop
pip install -r requirements.txt
python app.py
```

Optional override for the API URL:

```bash
# Windows PowerShell
$env:CHEM_EQUIP_API_URL="http://127.0.0.1:8000/api/upload/"
```

---

## Running Locally (Quick Start)

1. Start backend on `http://127.0.0.1:8000`
2. Start frontend on `http://localhost:3000`
3. Upload a CSV from the frontend and view charts/stats
4. Download the PDF report

---

## API Endpoints

- `POST /api/upload/` — Upload CSV and return stats + data
- `GET /api/latest/` — Get latest uploaded analysis
- `GET /api/pdf/` — Download PDF report

---

## Known Limitations

- **Node 20 incompatibility with CRA**: Create React App is not fully compatible with Node 20; use Node 18 LTS for best results.

---

## Screenshots

- Dashboard view (placeholder)
- Upload flow (placeholder)
- PDF report (placeholder)
- Desktop app (placeholder)

---

## License

MIT (or specify your preferred license)
