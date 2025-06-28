import {
    Component,
    signal,
    effect,
    inject,
    ResourceStatus,
    viewChild,
    ElementRef,
    Signal
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { httpResource } from '@angular/common/http';
import { MessageService } from '../services/message.service';
import { ChatMessage, ChatResponse, Role, Scheme } from '../chat';
import { MESSAGES } from '../messages';
import { UserService } from '../services/user.service';
import { SafeHtml } from '@angular/platform-browser';
import { SchemeCardComponent } from '../scheme-card/scheme-card.component';

@Component({
    selector: 'app-chat-window',
    templateUrl: './chat-window.component.html',
    styleUrls: ['./chat-window.component.scss'],
    imports: [FormsModule, SchemeCardComponent],
})
export class ChatWindowComponent {
    readonly ROLE = Role;

    userService = inject(UserService);
    messageService = inject(MessageService);
    private api = inject(ApiService);

    messages = signal<ChatMessage[]>([
        this.messageService.getWelcomMessage(),
    ]);

    userInput = signal('');
    conversationHistory = signal<string[]>([]);

    private trigger = signal(0);
    private _lastInput = '';

    chatResource = httpResource<ChatResponse>(() => {
        if (this.trigger() === 0) return;

        return this.api.getRecommendations(this.conversationHistory(), this._lastInput);
    });

    messagesContainer = viewChild<ElementRef<HTMLDivElement>>('messagesContainer');

    constructor() {
        effect(() => {
            const status = this.chatResource.status();

            if (status === ResourceStatus.Loading) return;

            if (status === ResourceStatus.Error) {
                const error = this.chatResource.error();
                let errorMsg = MESSAGES.ERROR_MESSAGE;
                if (error && typeof error === 'object' && 'status' in error && error.status === 429) {
                    errorMsg = 'You have reached your usage limit. Please try again later.';
                }
                this.messages.update((msgs) => [
                    ...msgs,
                    this.messageService.createNewMessage(Role.AI, errorMsg)
                ]);

                this.userInput.set('');
                this.trigger.set(0);
                return;
            }

            const value = this.chatResource.value();

            if (this.trigger() === 0 || !value) return;

            this.handleApiResponse(value);
        });

        effect(() => {
            this.messages();
            setTimeout(() => {
                const container = this.messagesContainer();
                if (container?.nativeElement) {
                    (container.nativeElement as HTMLDivElement).scrollTop = (container.nativeElement as HTMLDivElement).scrollHeight;
                }
            }, 0);
        });

    }

    private parseLinks(linksString: string): Array<{ label: string, url: string }> {
        if (!linksString || typeof linksString !== 'string') {
            return [];
        }

        const links: Array<{ label: string, url: string }> = [];
        const linkParts = linksString.split(' | ');

        for (const part of linkParts) {
            const colonIndex = part.indexOf(':');
            if (colonIndex !== -1) {
                const label = part.substring(0, colonIndex).trim();
                const url = part.substring(colonIndex + 1).trim();
                if (label && url) {
                    links.push({ label, url });
                }
            }
        }

        return links;
    }

    private processResults(results: Scheme[]): Scheme[] {
        return results.map(result => ({
            ...result,
            parsedLinks: this.parseLinks(result.links || '')
        }));
    }

    private handleApiResponse(value: ChatResponse): void {
        const replies: ChatMessage[] = [];

        this.conversationHistory.update((hist) => [...hist, this._lastInput]);

        if (value.followup_needed) {
            if (value.results && value.results.length > 0) {
                replies.push(this.messageService.createNewMessage(Role.AI, MESSAGES.RECOMMENDATIONS, this.processResults(value.results)));
            }

            replies.push(this.messageService.createNewMessage(Role.AI, value.message))
        } else if (value.results?.length || value.message) {
            replies.push(this.messageService.createNewMessage(Role.AI, value.message ?? MESSAGES.MATCHING, this.processResults(value.results)));
        } else {
            replies.push(this.messageService.createNewMessage(Role.AI, MESSAGES.ERROR_MESSAGE))
        }

        this.messages.update((msgs) => [
            ...msgs,
            ...replies,
        ]);

        this.userInput.set('');
        this.trigger.set(0);
    }

    get loading() {
        return this.chatResource.isLoading();
    }

    sendMessage() {
        const input = this.userInput().trim();
        if (!input) return;
        const userMsg: ChatMessage = this.messageService.createNewMessage(Role.User, input)

        this.messages.update((msgs) => [...msgs, userMsg]);
        this.userInput.set('');
        this._lastInput = input;
        this.trigger.update((v) => v + 1);
    }

    formatUserMessage(message: string | SafeHtml | null): string {
        if (!message) return '';
        if (typeof message !== 'string') return '';
        return message.replace(/&#10;/g, '<br>');
    }
}
