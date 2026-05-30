import {
  getClassificationDefinitions,
  getFullLabel,
  getPriorityDefinitions,
  GmailSystemLabel,
  HoloformLabel,
} from '../entities/labels.ts';
import { type Classification, Message } from '../entities/message.ts';
import {
  changeEmailLabels,
  type FetchedEmail,
  getThreadMessageList,
} from '../services/arcade-service.ts';
import { callLanguageModel } from '../services/language-model.ts';
import { logger } from '../utilities/logger.ts';
import { markdownToJson } from '../utilities/markdown.ts';

/** Converts a list of fetched emails into {@link Message} objects. */
export function createMessageObjects(emails: FetchedEmail[], userId: string): Message[] {
  if (emails.length === 0) {
    logger.info('No Gmail messages found.');
    return [];
  }

  const messages: Message[] = [];
  for (const email of emails) {
    logger.debug(`Creating Message object for Message: ${email.id}`);
    const message = new Message({
      userId,
      gmailMessageId: email.id,
      headerMessageId: email.headerMessageId ?? '',
      threadId: email.threadId ?? '',
      labels: email.labelIds,
      snippet: email.snippet,
      historyId: email.historyId,
      to: email.to,
      cc: email.cc,
      sender: email.from,
      replyToAddress: email.replyTo,
      date: email.date,
      subject: email.subject,
      body: email.body,
      inReplyTo: email.inReplyTo,
      references: email.references,
    });
    logger.debug(`message_obj created: ${message.gmailMessageId}`);
    messages.push(message);
  }
  return messages;
}

/** Summarizes the message's thread into the message's `summary` field. */
export async function summarizeThread(message: Message): Promise<void> {
  const prompt =
    `${JSON.stringify(message)} \n` +
    'Summarize the following thread of emails. ' +
    `Put it in 2nd person to ${message.userId} and highlight the most important parts to them. ` +
    'And if anyone is waiting on them for a response, highlight that prominently. ' +
    'Be concise, clear, direct, specific, and correct.';
  message.summary = await callLanguageModel(prompt);
}

/** Classifies and prioritizes a message via the language model. */
export async function classifyMessage(message: Message): Promise<void> {
  const prompt = `
        ## Message: ${JSON.stringify(message)}
        ----
        ## Prompt:
        Classify the email into one of the following categories with definitions:
        ${JSON.stringify(getClassificationDefinitions())}

        Then assign a priority level:
        ${JSON.stringify(getPriorityDefinitions())}

        Consider:
        - **Content:** Analyze the main topics and purpose.
        - **Tone:** Determine the formality and sentiment.
        - **Sender:** Identify if the sender is known or reputable.
        - **Time-Sensitivity:** Assess if immediate action is needed.
        - **Calls to Action:** Look for requests or required responses.


        RESPONSE FORMAT:
        Return JSON only: {"classification": "...", "priority": "...", "explanation": "..."}
        ----`;
  const response = await callLanguageModel(prompt);
  const parsed = markdownToJson(response) as Classification;

  // Add the Holoform prefix to the classification and priority.
  const classification: Classification = {
    classification: getFullLabel(parsed.classification),
    priority: getFullLabel(parsed.priority),
    explanation: parsed.explanation,
  };
  message.classification = classification;

  logger.debug(`\nMessage Classification: ${classification.classification}\n`);
  logger.debug(`Priority Level: ${classification.priority}\n`);
  logger.debug(`Explanation: ${classification.explanation}\n`);
}

/** Applies Holoform labels (and conditionally archives) based on classification. */
export function updateLabels(message: Message): void {
  const { classification, gmailMessageId, userId } = message;
  if (!classification) {
    throw new Error(`Cannot update labels: message ${gmailMessageId} is unclassified.`);
  }

  logger.debug(`Updating labels for message: ${gmailMessageId}`);
  const labelsToAdd = [
    getFullLabel(HoloformLabel.Holoform),
    classification.classification,
    classification.priority,
  ];
  let labelsToRemove: string[] = [];
  if (
    !(
      classification.classification.toLowerCase() === getFullLabel(HoloformLabel.ActionRequired) ||
      classification.priority === getFullLabel(HoloformLabel.HighPriority)
    )
  ) {
    labelsToRemove = [GmailSystemLabel.Inbox];
  }
  logger.debug(`\nLabels to add: ${labelsToAdd.join(', ')}\n`);
  logger.debug(`\nLabels to remove: ${labelsToRemove.join(', ')}\n`);
  changeEmailLabels({ emailId: gmailMessageId, labelsToAdd, labelsToRemove, userId });
  logger.debug(`Finished updating labels for message: ${gmailMessageId}\n`);
}

/** Drafts a reply-all response to the message via the language model. */
export async function draftResponse(message: Message): Promise<void> {
  const draftPrompt =
    `## Message: ${JSON.stringify(message)}\n` +
    `${'-'.repeat(8)}\n` +
    '## Prompt: \n' +
    'Draft a response to the message. ' +
    `Write in the first person as ${message.userId}. ` +
    'Be concise, clear, direct, specific, authentic, empathetic, personal, and correct. ' +
    'Use technical language where appropriate but remain plainspoken. Avoid clichés. ' +
    'The response should be a reply-all, sent to the sender and all other recipients. Retain CC. ' +
    "Reponse should be in JSON format: {'thread_id': '...', 'to': '...', 'cc': '...', 'subject': '...', 'body': '...'}";
  const draft = await callLanguageModel(draftPrompt);
  logger.debug(`draft_response_email: response draft: ${draft} \n`);
}

/** Processes a single message: fetch thread, classify, label. */
export async function processMessage(message: Message): Promise<Message> {
  message.threadMessages = getThreadMessageList(message.threadId, message.userId);
  await classifyMessage(message);
  logger.debug(
    `\n\n Subject: ${message.subject} \n Classification: ${JSON.stringify(message.classification)} \n ${'-'.repeat(20)}\n`,
  );
  updateLabels(message);
  logger.debug(`\n\nFinished processing message: ${message.gmailMessageId}\n\n`);
  message.status = 'processed';
  return message;
}

/** Processes every message. */
export async function processMessages(messages: Message[]): Promise<Message[]> {
  return Promise.all(messages.map(message => processMessage(message)));
}
