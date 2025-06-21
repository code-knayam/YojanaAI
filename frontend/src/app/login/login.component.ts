import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Auth, signInWithPopup, GoogleAuthProvider } from '@angular/fire/auth';
import { LoaderService } from '../services/loader.service';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
    error = '';
    private auth = inject(Auth);
    private router = inject(Router);
    private loaderService = inject(LoaderService);

    async signInWithGoogle() {
        this.error = '';
        this.loaderService.show();

        try {
            const provider = new GoogleAuthProvider();
            await signInWithPopup(this.auth, provider);
            this.router.navigateByUrl('/');
        } catch (err: any) {
            this.error = 'Google sign-in failed. Try again later.';
            this.loaderService.hide();
        }
    }
} 