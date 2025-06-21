import { inject, Injectable, SecurityContext } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { ChatMessage, Role, Scheme } from '../chat';
import { MESSAGES } from '../messages';
import { UserService } from './user.service';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  domSanitizer = inject(DomSanitizer);
  userService = inject(UserService);

  createNewMessage(role: Role, msg: string, schemes?: Scheme[]): ChatMessage {
    return {
      id: this.getMsgId(),
      role,
      message: this.getSanitizedMessage(msg),
      schemes
    }
  }

  getWelcomMessage(): ChatMessage {
    return this.createNewMessage(Role.AI, MESSAGES.WELCOME_MESSAGE.replace(/{NAME}/g, this.firstName));
  }

  private getSanitizedMessage(message: string): string | null {
    return this.domSanitizer.sanitize(SecurityContext.HTML, message);
  }

  private getMsgId() {
    return new Date().getTime();
  }

  private get firstName() {
    const name = this.userService.displayName;
    return name ? name.split(' ')[0] : '';
  }
}
