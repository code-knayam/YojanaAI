import { Component, inject, signal, computed } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LoaderService } from './services/loader.service';
import { Auth, signOut } from '@angular/fire/auth';
import { Router } from '@angular/router';
import { UserService } from './services/user.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  standalone: true,
  imports: [RouterOutlet]
})
export class AppComponent {
  userService = inject(UserService);
  loaderService = inject(LoaderService);
  private auth = inject(Auth);
  private router = inject(Router);

  isLoading = computed(() => {
    return this.loaderService.isLoading();
  });

  user = this.userService.user;

  constructor() {
    this.loaderService.show();
  }

  async logout() {
    await signOut(this.auth);
    this.router.navigateByUrl('/signin');
  }
}
