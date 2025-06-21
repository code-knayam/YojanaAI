import { SafeHtml } from "@angular/platform-browser";

export enum Role {
    AI,
    User
}

export interface Scheme {
    name: string;
    reason: string;
    link: string;
}

export interface ChatMessage {
    id: number;
    role: Role;
    message: string | SafeHtml | null;
    schemes?: Scheme[];
}

export interface Result {
    name: string;
    link: string;
    reason: string;
}

export interface ChatResponse {
    followup_needed: boolean;
    message: string;
    results: Result[];
}