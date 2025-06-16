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
  results?: Result[];
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  imports: [FormsModule]
})
export class AppComponent {
  messages = signal<ChatMessage[]>([
    {
      role: 'ai',
      text: `Hello! 👋 I am Yojana AI, your assistant for discovering government schemes in India.\n\nYou can ask me about education, business, agriculture, women empowerment, scholarships, and more. Just type your query and I'll recommend the most relevant schemes for you!`
    }
  ]);
  userInput = signal('');
  conversationHistory = signal<string[]>([]);
  // Triggers a new request when user sends a message
  private trigger = signal(0);
  private api = inject(ApiService);
  private _lastInput = '';

  chatResource = httpResource<ChatResponse>(() => {
    if (this.trigger() === 0) return undefined;
    return this.api.createRequest('/recommend', {
      conversation_history: this.conversationHistory(),
      current_input: this._lastInput,
    });
  });

  constructor() {
    effect(() => {
      const status = this.chatResource.status();
      if (status.toString() === 'loading') return;

      const value = this.chatResource.value();

      if (this.trigger() === 0 || !value) return;
      // Update conversation history after successful request
      this.conversationHistory.update(hist => [...hist, this._lastInput]);

      if (value.followup_needed) {
        if (value.results && value.results.length > 0 && value.results.length < 6) {
          this.messages.update(msgs => [
            ...msgs,
            { role: 'ai', text: 'Some recommendations are like:', schemes: value.results },
            { role: 'ai', text: value.message }
          ]);
        } else {
          this.messages.update(msgs => [
            ...msgs,
            { role: 'ai', text: value.message }
          ]);
        }
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
    const input = this.userInput().trim();
    if (!input) return;
    const userMsg: ChatMessage = { role: 'user', text: input };
    this.messages.update(msgs => [...msgs, userMsg]);
    this.userInput.set('');
    this._lastInput = input;
    this.trigger.update(v => v + 1);
  }
}
