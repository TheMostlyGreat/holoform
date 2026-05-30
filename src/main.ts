import { DEFAULT_USER_ID } from './config/settings.ts';
import { getFullLabel, GmailSystemLabel, HoloformLabel } from './entities/labels.ts';
import { createMessageObjects, processMessages } from './processors/message-processor.ts';
import { authUser, createLabel, fetchEmails, getLabels } from './services/arcade-service.ts';
import { logger } from './utilities/logger.ts';

/**
 * Ensures the `Holoform` parent label and its child labels exist in the user's
 * Gmail account, creating any that are missing.
 */
export function checkAndCreateLabels(userId: string): void {
  const parentLabel: string = HoloformLabel.Holoform;
  const childLabels = Object.values(HoloformLabel).filter(
    label => label !== HoloformLabel.Holoform,
  );

  const existingLabels = getLabels(userId);
  logger.debug(`Existing labels: ${JSON.stringify(existingLabels)}`);
  const existingLabelNames = new Set(existingLabels.map(label => label.name));

  if (existingLabelNames.has(parentLabel)) {
    logger.debug(`Parent label '${parentLabel}' already exists.`);
  } else {
    logger.info(`Parent label '${parentLabel}' not found. Creating it.`);
    createLabel(parentLabel, userId);
  }

  for (const label of childLabels) {
    const fullLabelName = getFullLabel(label);
    if (existingLabelNames.has(fullLabelName)) {
      logger.debug(`Child label '${fullLabelName}' already exists.`);
    } else {
      logger.info(`Child label '${fullLabelName}' not found. Creating it.`);
      createLabel(fullLabelName, userId);
    }
  }
}

export async function main(): Promise<void> {
  logger.info('Starting Gmail processing script...');

  // Authorize user and get Gmail token.
  authUser(DEFAULT_USER_ID);
  logger.debug('User authorized successfully.');

  // Check and create necessary labels.
  checkAndCreateLabels(DEFAULT_USER_ID);

  // Fetch recent Gmail messages.
  const emails = fetchEmails({
    userId: DEFAULT_USER_ID,
    label: GmailSystemLabel.Inbox,
    maxResults: 100,
  });

  // Create Message objects and process them.
  const messages = createMessageObjects(emails, DEFAULT_USER_ID);
  await processMessages(messages);

  // Further actions (e.g., storing to DB) can be added here.
}

if (import.meta.main) {
  await main();
}
