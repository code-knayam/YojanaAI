import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ApiService {
    private baseUrl: string;

    constructor() {
        // Switch base URL based on environment
        if (window.location.hostname === 'localhost') {
            this.baseUrl = 'http://localhost:8000';
        } else {
            this.baseUrl = 'https://yojanaai.onrender.com';
        }
    }

    createRequest(endpoint: string, body: any) {
        // Ensure endpoint starts with '/'
        const url = this.baseUrl + (endpoint.startsWith('/') ? endpoint : '/' + endpoint);
        return {
            url,
            method: 'POST',
            body,
            headers: { 'Content-Type': 'application/json' }
        };
    }
} 