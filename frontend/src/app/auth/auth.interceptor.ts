import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Auth } from '@angular/fire/auth';
import { from, switchMap, timeout } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const auth = inject(Auth);

    return from(
        auth.currentUser?.getIdToken() || Promise.resolve(null)
    ).pipe(
        switchMap((token) => {
            if (token) {
                const cloned = req.clone({
                    setHeaders: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                return next(cloned).pipe(
                    timeout(60000) // 60 seconds timeout
                );
            }

            return next(req).pipe(
                timeout(60000) // 60 seconds timeout
            );
        })
    );
};
