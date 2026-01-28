# SAR-C: Search & Rescue with Copernicus

**SAR-C** is an open-source decision support tool designed for maritime authorities and civil protection agencies. It defines search areas for objects or people adrift at sea by using real-time oceanographic data from the Copernicus Marine Service.

## 🚀 Overview

The system allows operators to input the "Last Known Position" (LKP) of a target. It then crosses this position with current and wind data to calculate a "Cone of Uncertainty" using the Leeway algorithm and Monte Carlo simulations, predicting where the target might be after a certain period.

### Key Benefits
- **Reduced Response Time:** Automates complex manual calculations.
- **Precision:** Uses real physical data instead of generic estimates.
- **Efficiency:** Optimizes search assets (aircraft/vessels) by focusing on the highest probability areas.

## 🏗 Architecture

### Backend
- **Framework:** Python (FastAPI)
- **Data Processing:** `xarray`, `netCDF4` (Copernicus Data)
- **Physics Engine:** `numpy`, `scipy` (Vector calculations, Monte Carlo)
- **API:** RESTful API for drift calculation and data retrieval.

### Data Sources
- **Currents:** Copernicus Global Ocean Physics Analysis and Forecast (`GLOBAL_ANALYSIS_FORECAST_PHY_001_024`)
- **Wind:** Global Ocean Hourly Sea Surface Wind and Stress (`WIND_GLO_PHY_L4_NRT_012_004`)

## 🛠 Installation & Setup

### Prerequisites
- Python 3.10+
- Copernicus Marine Service Account (for API credentials)

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Create a `.env` file in the `backend` directory based on the example (if available) or add:
   ```env
   COPERNICUS_USERNAME=your_username
   COPERNICUS_PASSWORD=your_password
   DEBUG=False
   ```

5. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## 🧪 Testing

Run the test suite (ensure you are in the `backend` directory):
```bash
pytest
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
