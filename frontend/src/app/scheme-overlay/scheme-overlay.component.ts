import { Component, input, output, effect, OnDestroy, inject, Renderer2, ElementRef, Inject } from '@angular/core';
import { Scheme } from '../chat';
import { DOCUMENT } from '@angular/common';

@Component({
  selector: 'app-scheme-overlay',
  imports: [],
  templateUrl: './scheme-overlay.component.html',
  styleUrl: './scheme-overlay.component.scss'
})
export class SchemeOverlayComponent implements OnDestroy {
  scheme = input.required<Scheme>();
  onOverlayClose = output<void>();

  private renderer = inject(Renderer2);

  constructor(@Inject(DOCUMENT) private document: Document) {
    effect(() => {
      if (this.scheme()) {
        this.toggleScroll(false);
      }
    });
  }

  ngOnDestroy() {
    this.toggleScroll(true);
  }

  closeOverlay() {
    this.toggleScroll(true);
    this.onOverlayClose.emit();
  }

  private toggleScroll(scrollValue: boolean) {
    const chatMessagesElement = this.document.querySelector('.chat-messages') as HTMLElement;

    if (chatMessagesElement) {
      this.renderer.setStyle(chatMessagesElement, 'overflow', scrollValue ? 'auto' : 'hidden');
    }
  }
}
