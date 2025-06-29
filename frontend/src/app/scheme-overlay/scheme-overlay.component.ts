import { Component, input, output } from '@angular/core';
import { Scheme } from '../chat';

@Component({
  selector: 'app-scheme-overlay',
  imports: [],
  templateUrl: './scheme-overlay.component.html',
  styleUrl: './scheme-overlay.component.scss'
})
export class SchemeOverlayComponent {
  scheme = input.required<Scheme>();

  onOverlayClose = output();

  closeOverlay(): void {
    this.onOverlayClose.emit();
  }
}
