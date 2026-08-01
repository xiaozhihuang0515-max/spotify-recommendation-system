import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({ plugins: [react()], server: { proxy: { "/api": "http://localhost:8000", "/users": "http://localhost:8000", "/recommendations": "http://localhost:8000", "/feedback": "http://localhost:8000", "/analytics": "http://localhost:8000" } } });
