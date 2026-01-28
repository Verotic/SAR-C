# SAR-C Frontend

The frontend interface for **SAR-C (Search & Rescue with Copernicus)**, a decision support tool for maritime search and rescue operations. This application visualizes drift predictions and search areas on an interactive map.

## 🚀 Features

- **Interactive Map:** Visualize search areas, drift trajectories, and particle simulations.
- **Mission Setup:** Easy-to-use form to input Last Known Position (LKP), incident time, and object type.
- **Real-time Feedback:** View drift predictions and uncertainty cones.
- **Layer Control:** Toggle wind and current vector layers for environmental context.

## 🛠 Tech Stack

- **Framework:** [React](https://react.dev/) with [Vite](https://vitejs.dev/)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **Maps:** [Leaflet](https://leafletjs.com/) / [React Leaflet](https://react-leaflet.js.org/)
- **State Management:** [Zustand](https://github.com/pmndrs/zustand) or Context API
- **Data Fetching:** [TanStack Query](https://tanstack.com/query/latest)

## 📦 Installation & Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Steps

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Environment Configuration:**
   Create a `.env` file in the `frontend` directory:
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

## 🧪 Scripts

- `npm run dev`: Start the development server.
- `npm run build`: Build the application for production.
- `npm run lint`: Run ESLint to check for code quality issues.
- `npm run preview`: Preview the production build locally.

## 🤝 Contributing

Please refer to the root [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on how to contribute to this project.
