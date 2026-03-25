// lib/firebase.ts
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getAnalytics, isSupported } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyBtM080L9atsQTH_rb__dNoRnnbw1ehd1Q",
  authDomain: "lamigo-core.firebaseapp.com",
  projectId: "lamigo-core",
  storageBucket: "lamigo-core.firebasestorage.app",
  messagingSenderId: "461121459169",
  appId: "1:461121459169:web:386cac6d72ec081c7238a0",
  measurementId: "G-DLLFMZV72K",
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);

// ✅ Only initialize analytics in the browser
let analytics: ReturnType<typeof getAnalytics> | null = null;

if (typeof window !== "undefined") {
  isSupported().then((supported) => {
    if (supported) {
      analytics = getAnalytics(app);
    }
  });
}

export { app, auth, analytics };
