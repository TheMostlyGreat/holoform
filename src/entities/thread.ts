import { randomUUID } from 'node:crypto';

import { getThreadMessageList } from '../services/arcade-service.ts';
import { Message } from './message.ts';

/** A node in the message reply-tree. */
export class TreeNode {
  message: Message;
  children: TreeNode[] = [];

  constructor(message: Message) {
    this.message = message;
  }
}

/** Stores and tracks email thread data through the processing pipeline. */
export class Thread {
  userId: string;
  threadId: string;
  summary = '';
  historyId = '';
  snippet = '';
  readonly uuid: string = randomUUID();
  status = 'unprocessed';
  messages: Message[] = [];
  treeRoots: TreeNode[] = [];

  constructor(userId: string, threadId: string) {
    if (!threadId) {
      throw new Error('thread_id cannot be empty.');
    }
    this.userId = userId;
    this.threadId = threadId;
  }

  /** Fetches the thread's messages (via Arcade) and builds its reply-tree. */
  static fromThreadId(userId: string, threadId: string): Thread {
    const thread = new Thread(userId, threadId);
    thread.messages = getThreadMessageList(threadId, userId).map(
      data =>
        new Message({
          userId,
          gmailMessageId: data.id,
          headerMessageId: data.headerMessageId ?? '',
          threadId,
          inReplyTo: data.inReplyTo,
          body: data.body,
          date: data.date,
          sender: data.from,
          subject: data.subject,
        }),
    );
    thread.treeRoots = Thread.buildTree(thread.messages);
    return thread;
  }

  /** Builds the reply-tree from a flat message list, returning the root nodes. */
  static buildTree(messages: Message[]): TreeNode[] {
    const nodeByGmailId = new Map<string, TreeNode>();
    const gmailIdByHeader = new Map<string, string>();
    for (const message of messages) {
      nodeByGmailId.set(message.gmailMessageId, new TreeNode(message));
      if (message.headerMessageId) {
        gmailIdByHeader.set(message.headerMessageId, message.gmailMessageId);
      }
    }

    const roots: TreeNode[] = [];
    for (const message of messages) {
      const node = nodeByGmailId.get(message.gmailMessageId);
      if (!node) {
        continue;
      }
      const parentGmailId = message.inReplyTo ? gmailIdByHeader.get(message.inReplyTo) : undefined;
      const parentNode = parentGmailId ? nodeByGmailId.get(parentGmailId) : undefined;
      if (parentNode) {
        parentNode.children.push(node);
      } else {
        roots.push(node);
      }
    }
    return roots;
  }
}
