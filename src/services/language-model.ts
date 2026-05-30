import OpenAI from 'openai';

import { LM_BASE_URL } from '../config/settings.ts';
import { logger } from '../utilities/logger.ts';

const SYSTEM_PROMPT_SUMMARIZE = 'You are a helpful assistant that summarizes threads of emails.';

let client: OpenAI | undefined;

/** Lazily construct the OpenAI-compatible client so import never requires a key. */
function getClient(): OpenAI {
  client ??= new OpenAI({ apiKey: process.env.ARCADE_API_KEY ?? '', baseURL: LM_BASE_URL });
  return client;
}

const sleep = (milliseconds: number): Promise<void> =>
  new Promise(resolve => setTimeout(resolve, milliseconds));

export interface CallOptions {
  systemPrompt?: string;
  maxRetries?: number;
}

async function attemptCall(
  prompt: string,
  systemPrompt: string,
  attempt: number,
  maxRetries: number,
): Promise<string> {
  try {
    const completion = await getClient().chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: prompt },
      ],
    });
    const content = completion.choices[0]?.message.content ?? '';
    logger.debug(`LM response: ${content}`);
    return content;
  } catch (error) {
    if (attempt < maxRetries - 1) {
      logger.error(
        `Error interacting with the LM (attempt ${String(attempt + 1)}): ${String(error)}`,
      );
      await sleep(5 ** attempt * 1000); // Exponential backoff, mirroring the Python original.
      return attemptCall(prompt, systemPrompt, attempt + 1, maxRetries);
    }
    logger.error(`LM request failed after ${String(maxRetries)} attempts: ${String(error)}`);
    throw new Error(`LM request failed after multiple attempts. ${String(error)}`, {
      cause: error,
    });
  }
}

/** Send a single prompt to the language model and return its text content. */
export async function callLanguageModel(
  prompt: string,
  options: CallOptions = {},
): Promise<string> {
  const systemPrompt = options.systemPrompt ?? SYSTEM_PROMPT_SUMMARIZE;
  const maxRetries = options.maxRetries ?? 2;
  return attemptCall(prompt, systemPrompt, 0, maxRetries);
}
