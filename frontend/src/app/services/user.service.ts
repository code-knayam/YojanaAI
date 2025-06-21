import { Injectable, signal, inject } from '@angular/core';
import { Auth, onAuthStateChanged, User } from '@angular/fire/auth';
import { LoaderService } from './loader.service';

@Injectable({ providedIn: 'root' })
export class UserService {
    private loaderService = inject(LoaderService);

    user = signal<User | null>(null);

    constructor(private auth: Auth) {
        onAuthStateChanged(this.auth, (user) => {
            this.user.set(user);
            this.loaderService.hide();
        });
    }

    get displayName() {
        return this.user()?.displayName || '';
    }

    get photoURL() {
        return this.user()?.photoURL || '';
    }

    get email() {
        return this.user()?.email || '';
    }
} 