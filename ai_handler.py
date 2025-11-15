
# ai_handler.py
import requests

class AI:
    def __init__(self):
        self.messages = []

    def set_system_prompt(self, prompt):
        """Sets the initial system prompt for the AI conversation."""
        self.messages = [{"role": "system", "content": prompt}]

    def msg_ai(self, msg):
        """Sends a message to the AI and gets a response."""
        self.messages.append({"role": "user", "content": msg})
        try:
            response = requests.post(
                url="https://api.featherless.ai/v1/chat/completions",
                headers={"Authorization": "Bearer rc_fdc6c2e981e09168b83cdd3eee0a846ff2970cd35a6e77c88d5368d7c8a5939b"},
                json={"model": "deepseek-ai/DeepSeek-V3-0324", "messages": self.messages},
                timeout=45
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            response_text = response.json()['choices'][0]["message"]["content"]
            self.messages.append({"role": "assistant", "content": response_text})
            return response_text
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with LLM API: {e}")
            # Return a formatted error message for the game to handle gracefully
            return (f"Error: Could not connect to the VeriNews AI network.\n\n"
                    f"Let's move on to another topic.\n\n"
                    '{"popularity": null, "bias": null}')