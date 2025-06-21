import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ApiService {
    private baseUrl: string;

    constructor() {
        if (window.location.hostname === 'localhost') {
            this.baseUrl = 'http://localhost:8000';
        } else {
            this.baseUrl = 'https://yojanaai.onrender.com';
        }
    }

    private createRequest(endpoint: string, method: string, body: any) {
        const url = `${this.baseUrl}/${endpoint}`;
        return {
            url,
            method,
            body,
            headers: { 'Content-Type': 'application/json' }
        };
    }

    getRecommendations(history: string[], message: string) {
        return this.createRequest('recommend', 'POST', {
            conversation_history: history,
            current_input: message,
        })
    }
} 