import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideFirebaseApp, initializeApp } from '@angular/fire/app';
import { provideAuth, getAuth } from '@angular/fire/auth';
import { provideAnalytics } from '@angular/fire/analytics';
import { getAnalytics } from 'firebase/analytics';
import { authInterceptor } from './auth/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideFirebaseApp(() => initializeApp({
      apiKey: "AIzaSyDmrjo0VML9YWvttq9PGmHcFr-UeGaAwZA",
      authDomain: "yojanaai.firebaseapp.com",
      projectId: "yojanaai",
      storageBucket: "yojanaai.firebasestorage.app",
      messagingSenderId: "510673118881",
      appId: "1:510673118881:web:c6a89b14ff8c8660ac32e0",
      measurementId: "G-5G7BHMVMQ6"
    })),
    provideAnalytics(() => getAnalytics()),
    provideAuth(() => getAuth())
  ]
};
