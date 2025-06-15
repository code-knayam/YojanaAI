import { Component, signal, computed, effect, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { httpResource } from '@angular/common/http';
import { ApiService } from './api.service';

interface Scheme {
  name: string;
  reason: string;
  link: string;
}

interface ChatMessage {
  role: 'user' | 'ai';
  text: string;
  schemes?: Scheme[];
}

interface Result {
  name: string;
  link: string;
  reason: string;
}

interface ChatResponse {
  text: string;
  results: Result[];
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  imports: [FormsModule]
})
export class AppComponent {
  messages = signal<ChatMessage[]>([]);
  userInput = signal('');
  lastUserQuery = signal('');
  isFollowup = computed(() => !!this.lastUserQuery());
  // Triggers a new request when user sends a message
  private trigger = signal(0);
  private api = inject(ApiService);

  // Resource for recommendations or refine
  chatResource = httpResource<ChatResponse>(() => {
    // Only trigger when user sends a message
    if (this.trigger() === 0) return undefined;
    const isFollowup = this.isFollowup();

    const endpoint = isFollowup ? '/refine' : '/recommend';
    const payload = isFollowup
      ? { original_query: this.lastUserQuery(), followup_answer: this.userInput() }
      : { query: this.userInput() };
    return this.api.createRequest(endpoint, payload);
  });

  constructor() {
    // Effect to update messages when resource value changes
    effect(() => {
      const status = this.chatResource.status();

      if (status.toString() === 'loading') return;

      const value = this.chatResource.value();

      if (this.trigger() === 0 || !value) return;
      this.lastUserQuery.set(this.userInput());

      // Handle API response with 'results' array
      if (value.results?.length) {
        this.messages.update(msgs => [
          ...msgs,
          { role: 'ai', text: 'Here are some schemes that match your query:', schemes: value.results }
        ]);
      } else {
        this.messages.update(msgs => [...msgs, { role: 'ai', text: 'Sorry, something went wrong. Please try again.' }]);
      }

      // Reset user input and trigger
      this.userInput.set('');
      this.trigger.set(0);
    });
  }

  get loading() {
    return this.chatResource.isLoading();
  }

  sendMessage() {
    if (!this.userInput().trim()) return;
    const userMsg: ChatMessage = { role: 'user', text: this.userInput() };
    this.messages.update(msgs => [...msgs, userMsg]);
    this.trigger.update(v => v + 1);
  }
}
