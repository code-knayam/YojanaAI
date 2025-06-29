import { Component, input, signal } from '@angular/core';
import { Scheme } from '../chat';
import { SlicePipe } from '@angular/common';
import { SchemeOverlayComponent } from '../scheme-overlay/scheme-overlay.component';

@Component({
  selector: 'app-scheme-card',
  imports: [SlicePipe, SchemeOverlayComponent],
  templateUrl: './scheme-card.component.html',
  styleUrl: './scheme-card.component.scss'
})
export class SchemeCardComponent {
  scheme = input.required<Scheme>();
  showOverlay = signal(false);

  openOverlay() {
    this.showOverlay.set(true);
  }

  closeOverlay() {
    this.showOverlay.set(false);
  }
}
