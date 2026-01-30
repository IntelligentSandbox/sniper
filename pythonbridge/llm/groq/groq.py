from typing import Optional
import groq
from groq import Groq
from pythonbridge.core import config


DEFAULT_MODEL = "llama-3.3-70b-versatile"


# NOTE: No need to use AsyncGroq since a new, independent python process will be started by Elixir
# GroqLLM ai initializes api key and takes any query in the review code function
# Currently using the free plan for Groq
class GroqLLM:
    def __init__(
        self, curr_model: str = DEFAULT_MODEL, system_prompt: str = ""
    ) -> None:
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.curr_model = curr_model
        self.system_prompt = system_prompt

    def invoke(self, message: str) -> Optional[str]:
        """Sends a message to Groq endpoint and returns the received message

        Args:
            message (str): The message to be sent to Groq

        Returns:
            Optional[str]: Returns the Groq response or None if an error is encountered
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": message},
                ],
                model=self.curr_model,
            )

            return chat_completion.choices[0].message.content

        except groq.APIConnectionError as e:
            print(f"The server could not be reached: {e}")
            return None
        except groq.RateLimitError as e:
            print(f"The rate limit has been reached: {e}")
            return None
        except groq.APIStatusError as e:
            print(f"API Error (status:{e.status_code}): {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
