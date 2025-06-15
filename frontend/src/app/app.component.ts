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
  followup_needed: boolean;
  message: string;
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
  conversationHistory = signal<string[]>([]);
  // Triggers a new request when user sends a message
  private trigger = signal(0);
  private api = inject(ApiService);

  chatResource = httpResource<ChatResponse>(() => {
    if (this.trigger() === 0) return undefined;
    return this.api.createRequest('/recommend', {
      conversation_history: this.conversationHistory(),
      current_input: this.userInput(),
    });
  });

  constructor() {
    effect(() => {
      const status = this.chatResource.status();
      if (status.toString() === 'loading') return;

      const value = this.chatResource.value();

      if (this.trigger() === 0 || !value) return;
      // Update conversation history after successful request
      this.conversationHistory.update(hist => [...hist, this.userInput()]);

      if (value.followup_needed) {
        // Show a template message, then the actual message
        this.messages.update(msgs => [
          ...msgs,
          { role: 'ai', text: 'Some recommendations are like:', schemes: value.results },
          { role: 'ai', text: value.message }
        ]);
      } else if (value.results?.length || value.message) {
        this.messages.update(msgs => [
          ...msgs,
          { role: 'ai', text: value.message ?? 'Here are some schemes that match your query:', schemes: value.results }
        ]);
      } else {
        this.messages.update(msgs => [...msgs, { role: 'ai', text: 'Sorry, something went wrong. Please try again.' }]);
      }

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
