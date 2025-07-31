import { IDocumentManager } from '@jupyterlab/docmanager';
import { v4 as uuid } from 'uuid';
import { ContextCommandParams } from './types';
import { postToWebView } from './webview';

type MessageData = Record<string, unknown>;

export interface Message {
  command: string;
  params: MessageData;
  tabId?: string;
}

export interface Response extends Message {
  id: string;
  error?: string;
}

interface WebSocketHandlerParams {
  url: string;
  docManager: IDocumentManager;
  reconnectInterval?: number;
  timeout?: number;
}

export class WebSocketHandler {
  private socket!: WebSocket; // Using definite assignment assertion
  private pendingRequests = new Map<string, (response: Response) => void>();
  private timeout: number;
  private docManager: IDocumentManager;
  private url: string;
  private reconnectInterval: number;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;

  private sendErrorToWebview(
    title: string,
    message: string,
    tabId?: string
  ): void {
    const errorPayload = {
      command: 'errorMessage',
      params: {
        title,
        message,
        tabId
      }
    };
    postToWebView(errorPayload);
  }

  constructor({
    url,
    docManager,
    reconnectInterval = 1000,
    timeout = 600000
  }: WebSocketHandlerParams) {
    this.url = url;
    this.reconnectInterval = reconnectInterval;
    this.timeout = timeout;
    this.setupSocket();
    this.docManager = docManager;
  }

  private setupSocket(): void {
    this.socket = new WebSocket(this.url);
    this.socket.onmessage = this.onMessage.bind(this);

    this.socket.onopen = () => {
      console.log('WebSocket connection established');
      this.reconnectAttempts = 0;
    };

    this.socket.onerror = error => {
      console.error('WebSocket error:', error);
    };

    this.socket.onclose = event => {
      console.log('WebSocket connection closed:', event.code, event.reason);
      this.reconnect();
    };
  }

  private reconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      console.log(
        `Attempting to reconnect (attempt ${this.reconnectAttempts + 1})...`
      );
      this.reconnectAttempts++;
      const delay =
        this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff

      setTimeout(() => {
        this.setupSocket();
      }, delay);
    }
  }

  private onMessage(event: MessageEvent<string>): void {
    if (event.origin && !event.origin.startsWith('wss://')) {
      console.warn(
        `Rejected message from insecure websocket connection: ${event.origin}`
      );
      return;
    }
    // Only allow messages from the same origin
    if (
      event.origin &&
      event.origin.replace('wss://', '') !==
        window.location.origin.replace('https://', '')
    ) {
      console.warn(
        `Rejected message from unauthorized origin: ${event.origin}`
      );
      return;
    }

    try {
      const message = JSON.parse(event.data);
      const id = message.id;
      console.log('WebSocket message received:', message);

      if (id) {
        const handler = this.pendingRequests.get(id);
        if (handler) {
          handler(message);
        } else {
          console.warn(`No handler found for message with id: ${id}`);
        }
      } else {
        this.handleInboundEvent(message);
      }
    } catch (error) {
      console.error('Error processing message:', error);
      const message = JSON.parse(event.data);
      this.sendErrorToWebview(
        'Message Processing Error',
        'Failed to process message, please refresh browser and try again.',
        message.tabId
      );
    }
  }

  private handleInboundEvent(message: Message): void {
    try {
      const command = message.command;
      console.log('Handling inbound event:', { command });

      switch (command) {
        case 'aws/chat/sendChatPrompt':
        case 'aws/chat/buttonClick':
        case 'aws/chat/sendPinnedContext':
        case 'aws/chat/openTab':
        case 'aws/chat/sendChatUpdate':
        case 'aws/chat/chatOptionsUpdate':
          postToWebView(message);
          break;
        case 'aws/chat/sendContextCommands':
          const workingCommands = ['Folders', 'Files'];

          const contextCommandParams =
            message.params as unknown as ContextCommandParams;

          const filteredContextCommandGroups =
            contextCommandParams.contextCommandGroups.map(
              contextCommandGroup => {
                const filteredCommands = contextCommandGroup?.commands.filter(
                  command => workingCommands.includes(command.command)
                );
                return {
                  ...contextCommandGroup,
                  commands: filteredCommands
                };
              }
            );

          postToWebView({
            ...message,
            params: {
              ...message.params,
              contextCommandGroups: filteredContextCommandGroups
            }
          });
          break;
        case 'aws/openFileDiff':
          // TODO: Add diff visual
          this.docManager.openOrReveal(
            (message.params.originalFileUri as string).replace(
              'home/sagemaker-user/',
              ''
            )
          );
          break;
        default:
          console.log(`Unhandled inbound command: ${command}`);
      }
    } catch (error) {
      console.error('Error handling event:', error);
      this.sendErrorToWebview(
        'Event Handling Error',
        'Failed to handle inbound event, please refresh browser and try again.',
        message.tabId
      );
    }
  }

  public sendRequest(message: Message): Promise<Response> {
    if (this.socket.readyState !== WebSocket.OPEN) {
      this.sendErrorToWebview(
        'Connection Error',
        'WebSocket is not connected, please stop and start the space and try again.',
        message.tabId
      );
      return Promise.reject(new Error('WebSocket is not connected'));
    }

    const id = uuid();
    console.log(`Sending request with id: ${id}, command: ${message.command}`);

    return new Promise<Response>((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        this.pendingRequests.delete(id);
        console.error(`Request timed out: ${message.command} (id: ${id})`);
        this.sendErrorToWebview(
          'Request Timeout',
          `Request timed out: ${message.command}`,
          message.tabId
        );
        reject(new Error(`Request timed out: ${message.command}`));
      }, this.timeout);

      this.pendingRequests.set(id, response => {
        clearTimeout(timeoutId);
        this.pendingRequests.delete(id);

        if (response.error) {
          if (
            response.error
              .toLowerCase()
              .includes('you are not subscribed to amazon q developer')
          ) {
            this.sendErrorToWebview(
              'No active subscription',
              response.error,
              message.tabId
            );
          } else if (response.error.includes('Something went wrong')) {
            this.sendErrorToWebview(
              'Internal Server Error',
              response.error,
              message.tabId
            );
          } else {
            this.sendErrorToWebview(
              'Response Error',
              response.error,
              message.tabId
            );
          }
          reject(new Error(response.error));
        } else {
          console.log(`Received response for id: ${id}`);
          resolve(response);
        }
      });

      try {
        const payload = { ...message, id };
        console.log('Sending payload:', payload);
        this.socket.send(JSON.stringify(payload));
      } catch (error) {
        clearTimeout(timeoutId);
        this.pendingRequests.delete(id);
        this.sendErrorToWebview(
          'Message Sending Error',
          'Failed to send message, please refresh browser and try again.',
          message.tabId
        );
        reject(error);
      }
    });
  }

  public sendNotification(message: Message): void {
    if (this.socket.readyState === WebSocket.OPEN) {
      console.log(`Sending notification: ${message.command}`);
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn(`Cannot send notification: WebSocket is not connected`);
    }
  }
}
