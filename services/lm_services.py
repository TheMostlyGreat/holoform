import os
import logging
import time
from openai import OpenAI
from config.settings import LM_BASE_URL, LOG_LEVEL

client = OpenAI(
    api_key=os.environ["ARCADE_API_KEY"],
    base_url=LM_BASE_URL,
)
SYSTEM_PROMPT_SUMMARIZE = "You are a helpful assistant that summarizes threads of emails."

def call_lm(prompt: str, system_prompt: str = SYSTEM_PROMPT_SUMMARIZE, tools: list = None, tool_choice: list = None, max_retries: int = 2) -> str:
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"{prompt}"
                    }
                ],
                # #response_format={"type": "json_object"},
                # **({"tool_choice": tool_choice} if tool_choice else {}),
                #**({"tools": tools} if tool_choice and tools else {}),
                # user=user_id,
                # tools=[
                #     "Google.WriteDraftResponseEmail",
                # ],
                # tool_choice="generate",
            )
            logging.debug(f"LM response: {completion.choices[0].message.content}")
            return completion.choices[0].message.content
        except Exception as e:
            if attempt < max_retries - 1:
                logging.error(f"Error interacting with the LM (attempt {attempt + 1}): {e}")
                time.sleep(5 ** attempt)  # Exponential backoff
            else:
                logging.error(f"LM request failed after {max_retries} attempts: {e}")
                raise RuntimeError(f"LM request failed after multiple attempts. {e}")
