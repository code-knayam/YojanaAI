import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Auth } from '@angular/fire/auth';
import { from, map, take, tap } from 'rxjs';

export const AuthGuard: CanActivateFn = () => {
    const auth = inject(Auth);
    const router = inject(Router);
    return from(new Promise(resolve => auth.onAuthStateChanged(resolve))).pipe(
        take(1),
        map(user => !!user),
        tap(isAuth => {
            if (!isAuth) router.navigateByUrl('/signin');
        })
    );
}; 