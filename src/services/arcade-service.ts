import { logger } from '../utilities/logger.ts';

/**
 * Arcade integration is intentionally stubbed: Holoform's TypeScript port does
 * not yet wire the `@arcadeai/arcadejs` SDK. Each function logs that it is a
 * no-op and returns an empty/placeholder result so the rest of the pipeline
 * runs end-to-end without a live Arcade connection.
 */

/** Relative date windows accepted by the Gmail list tools. */
export enum DateRange {
  Today = 'today',
  Yesterday = 'yesterday',
  Last7Days = 'last_7_days',
  Last30Days = 'last_30_days',
}

/** Shape of an email as returned by Arcade's Gmail tools (post-adapter). */
export interface FetchedEmail {
  id: string;
  headerMessageId?: string;
  threadId?: string;
  labelIds?: string[];
  snippet?: string;
  historyId?: string;
  to?: string[];
  cc?: string[];
  from?: string;
  replyTo?: string[];
  date?: string;
  subject?: string;
  body?: string;
  inReplyTo?: string;
  references?: string[];
}

/** A Gmail label as returned by Arcade's `Google.ListLabels` tool. */
export interface GmailLabel {
  id: string;
  name: string;
}

const STUB_NOTICE = 'Arcade is stubbed — returning placeholder result.';

export interface FetchEmailsOptions {
  userId: string;
  dateRange?: DateRange;
  label?: string;
  maxResults?: number;
}

export function fetchEmails(options: FetchEmailsOptions): FetchedEmail[] {
  logger.warn(`fetchEmails(${options.userId}): ${STUB_NOTICE}`);
  return [];
}

export function fetchThreads(userId: string, maxResults = 10): unknown[] {
  logger.warn(`fetchThreads(${userId}, ${String(maxResults)}): ${STUB_NOTICE}`);
  return [];
}

export function getThreadMessageList(threadId: string, userId: string): FetchedEmail[] {
  logger.warn(`getThreadMessageList(${threadId}, ${userId}): ${STUB_NOTICE}`);
  return [];
}

export interface ChangeLabelsOptions {
  emailId: string;
  labelsToAdd: string[];
  labelsToRemove: string[];
  userId: string;
}

export function changeEmailLabels(options: ChangeLabelsOptions): void {
  logger.warn(`changeEmailLabels(${options.emailId}): ${STUB_NOTICE}`);
}

export function getLabels(userId: string): GmailLabel[] {
  logger.warn(`getLabels(${userId}): ${STUB_NOTICE}`);
  return [];
}

export function authUser(userId: string): string {
  logger.warn(`authUser(${userId}): ${STUB_NOTICE}`);
  return 'stub-token';
}

export function createLabel(labelName: string, userId: string): void {
  logger.warn(`createLabel(${labelName}, ${userId}): ${STUB_NOTICE}`);
}
