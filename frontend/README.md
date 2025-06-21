# YojanaAI Frontend

YojanaAI is a modern Angular app that lets users chat with an AI assistant to discover government schemes. It features a ChatGPT-inspired UI, Google sign-in, and real-time recommendations from the backend.

## 🏗️ Architecture
- **Angular 19**: Modern, standalone component-based frontend
- **Firebase Auth**: Google sign-in, route protection, and token management
- **Signals**: For reactive state and UI updates
- **API Service**: Switches between local and production backend
- **Loader Service**: Global app loading state
- **Chat Window**: Signal-based, auto-scrolls, supports AI and user messages, and scheme cards
- **Dark Theme**: ChatGPT-inspired with green accents

## 📂 File Structure
- `src/app/` — Main app code (components, services, guards)
- `src/styles.scss` — Global theme and styles
- `angular.json` — Angular CLI config
- `package.json` — Scripts and dependencies

## 🚀 Local Development

1. **Install dependencies**
   ```bash
   npm install
   ```
2. **Run the app**
   ```bash
   npm start
   ```
   The app will be available at `http://localhost:4200`.

## ☁️ Deployment
- Build for production:
  ```bash
  npm run build
  ```
- Deploy the contents of `dist/frontend` to your static host (e.g., Vercel, Netlify, Firebase Hosting)
- The app auto-detects backend URL (localhost or production)

## 🧠 How It Works
- Users sign in with Google (Firebase Auth)
- Auth tokens are attached to API requests via an HTTP interceptor
- Chat window sends conversation history to backend for recommendations
- Loader service manages global loading state
- All UI is reactive using Angular signals

## 🤝 Contributing
See [../../CONTRIBUTIONS.md](../CONTRIBUTIONS.md) for guidelines.
