// Import the functions you need from the SDKs you need
// import { initializeApp } from "firebase/app";
// import { getAnalytics } from "firebase/analytics";
// import { getAuth } from "firebase/auth";

// // Your web app's Firebase configuration
// const firebaseConfig = {
//   apiKey: "AIzaSyAsMKnViuFT1cidM4hpsYfvhoGrfCmcHQM",
//   authDomain: "lamigo-platform.firebaseapp.com",
//   projectId: "lamigo-platform",
//   storageBucket: "lamigo-platform.firebasestorage.app",
//   messagingSenderId: "46047859896",
//   appId: "1:46047859896:web:2195ff103da3c52045104d",
//   measurementId: "G-51ZVPKFYNW"
// };

// // Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);
// const auth = getAuth(app);

// export { app, auth };

// lib/firebase.ts
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getAnalytics, isSupported } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyAsMKnViuFT1cidM4hpsYfvhoGrfCmcHQM",
  authDomain: "lamigo-platform.firebaseapp.com",
  projectId: "lamigo-platform",
  storageBucket: "lamigo-platform.firebasestorage.app",
  messagingSenderId: "46047859896",
  appId: "1:46047859896:web:2195ff103da3c52045104d",
  measurementId: "G-51ZVPKFYNW"
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);

// ✅ Only initialize analytics in the browser
let analytics: any = null;

if (typeof window !== "undefined") {
  isSupported().then((supported) => {
    if (supported) {
      analytics = getAnalytics(app);
    }
  });
}

export { app, auth, analytics };
