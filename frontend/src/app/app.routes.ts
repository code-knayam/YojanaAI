import { Routes } from '@angular/router';
import { provideRouter } from '@angular/router';
import { ChatWindowComponent } from './chat-window/chat-window.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './auth/auth.guard';

export const routes: Routes = [
    { path: 'signin', component: LoginComponent },
    { path: '', component: ChatWindowComponent, canActivate: [AuthGuard] }
];
