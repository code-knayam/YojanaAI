import { Component, input } from '@angular/core';
import { Scheme } from '../chat';
import { SlicePipe } from '@angular/common';

@Component({
  selector: 'app-scheme-card',
  imports: [SlicePipe],
  templateUrl: './scheme-card.component.html',
  styleUrl: './scheme-card.component.scss'
})
export class SchemeCardComponent {
  scheme = input.required<Scheme>();
}
