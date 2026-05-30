/**
 * Cleans markdown code-block formatting from a JSON string response and parses it.
 *
 * @param response Raw response string potentially containing markdown formatting.
 * @returns The parsed JSON value (caller narrows the type).
 */
export function markdownToJson(response: string): unknown {
  const cleaned = response.replaceAll('```json', '').replaceAll('```', '').trim();
  return JSON.parse(cleaned);
}
