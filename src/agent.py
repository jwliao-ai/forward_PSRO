import openai
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

class Agent:
    def __init__(self, api_key: str, api_base: str = None):
        """
        Initialize the LLM-based agent.

        :param api_key: OpenAI API key.
        :param api_base: OpenAI API base (for custom endpoints).
        """
        openai.api_key = api_key
        if api_base:
            openai.base_url = api_base

    @staticmethod
    def generate_messages(system_prompt: str, user_input: str, content_type: str, image_url: str = None):
        """
        Generate appropriate messages structure based on the content type.

        :param system_prompt: The system prompt for the assistant.
        :param user_input: User's input (text question).
        :param content_type: The type of content ('text' or 'multimodal').
        :param image_url: The URL of the image (required for 'multimodal').
        :return: A list of messages.
        """
        if content_type == "text":
            # Text-based content
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        elif content_type == "multimodal":
            # Multimodal content
            if not image_url:
                raise ValueError("Image URL is required for multimodal content.")
            return [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_input},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

    @retry(
        stop=stop_after_attempt(3),  # Retry up to 3 times
        wait=wait_fixed(2),          # Wait 2 seconds between retries
        retry=retry_if_exception_type(Exception)  # Retry on any exception
    )
    def get_response(self, model_info: dict, system_prompt: str, user_input: str, image_url: str = None, temperature: float = 0.7):
        """
        Get a response from the LLM model with retry.

        :param model_info: A dictionary containing model name and content type.
        :param system_prompt: The system prompt for the assistant.
        :param user_input: User's input (text question).
        :param image_url: The URL of the image (required for 'multimodal').
        :param temperature: The temperature setting for the model's response generation.
        :return: Model's response.
        """
        messages = self.generate_messages(system_prompt, user_input, model_info["content_type"], image_url)
        response = openai.chat.completions.create(
            model=model_info["name"],
            messages=messages,
            temperature=temperature
        )
        return response['choices'][0]['message']['content']

# Example usage
if __name__ == "__main__":
    # Initialize the agent with your OpenAI API key and optional API base
    agent = Agent(api_key="your-api-key", api_base="https://api.openai.com/v1")
    
    # Define model information
    models = [
        {"name": "internlm/internlm2-chat-20b", "content_type": "text"},
        {"name": "Qwen/Qwen2.5-72B-Instruct", "content_type": "text"},
        {"name": "Qwen/Qwen2-VL-72B-Instruct", "content_type": "multimodal"},
        {"name": "internthinker", "content_type": "text"}
    ]
    
    # Define inputs
    selected_model = models[2]  # Qwen2-VL-72B-Instruct (multimodal)
    system_prompt = "You are a helpful assistant."
    user_input = "What's in this image?"
    image_url = "https://example.com/image.png"  # Replace with an actual URL

    # Call the agent
    try:
        answer = agent.get_response(selected_model, system_prompt, user_input, image_url)
        print(answer)
    except Exception as e:
        print(f"Failed to get a response: {e}")