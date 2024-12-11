# Run in the ONLINE NODE
import argparse
import json
import os
from datetime import datetime
from src.dataset import Dataset

import openai
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

class Agent:
    def __init__(self, api_key: str, api_base: str = None, model_name: str = None):
        """
        Initialize the LLM-based agent.

        :param api_key: OpenAI API key.
        :param api_base: OpenAI API base (for custom endpoints).
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base,
        )
        self.model = model_name

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
    def get_response(self, content_type: str, system_prompt: str, user_input: str, image_url: str = None, temperature: float = 0.7):
        """
        Get a response from the LLM model with retry.

        :param model_info: A dictionary containing model name and content type.
        :param system_prompt: The system prompt for the assistant.
        :param user_input: User's input (text question).
        :param image_url: The URL of the image (required for 'multimodal').
        :param temperature: The temperature setting for the model's response generation.
        :return: Model's response.
        """
        messages = self.generate_messages(system_prompt, user_input, content_type, image_url)
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={ "type": "json_object" }
        )
        response = chat_completion.choices[0].message.content
        response = json.loads(response)
        return response

api_key = ""
api_base = ""
model_name = ""

Name2Path = {
    "cipher" : "data/cipher.json",
    "logic" : "data/logic.json",
    "math" : "data/math.json",
    "operation" : "data/operation.json",
    "PHY" : "data/PHY.json",
    "puzzle" : "data/puzzle.json",
    "Rule" : "data/Rule.json"
}

Name2Prompt = {
    "cipher" : "prompt/cipher/",
    "logic" : "prompt/logic/",
    "math" : "prompt/math/",
    "operation" : "prompt/operation/",
    "PHY" : "prompt/PHY/",
    "puzzle" : "prompt/puzzle/",
    "Rule" : "prompt/Rule/"
}

def load_system_prompt(prompt_dir):
    """
    从指定目录加载系统提示
    """
    system_prompt_path = os.path.join(prompt_dir, "best_system_prompt.json")
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"System prompt file not found at: {system_prompt_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load system prompt: {e}")


def load_attack_prompts(prompt_dir):
    """
    从指定目录加载 attack_prompt.json
    """
    attack_prompt_path = os.path.join(prompt_dir, "best_attack_prompt.json")
    try:
        with open(attack_prompt_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Attack prompt file not found at: {attack_prompt_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode attack prompt JSON: {e}")

def run_agent_test(dataset, agent, system_prompt, attack_prompts, temperature=0.7):
    """
    对agent进行测试
    """

    before_attack_prompt = attack_prompts.get("before_attack_prompt", "")
    after_attack_prompt = attack_prompts.get("after_attack_prompt", "")
    # 构造 user_input
    attack_evol_req = '''I have a good attack prompt, please guess it's most likely probability distribution, and generate two more prompt by sampling according to the distribution, please ensure diversity. The attack prompt is here: {
            "before_attack_prompt" : "''' + before_attack_prompt + '''}",
            "after_attack_prompt" : "''' + after_attack_prompt + '''}"
        }.
        Please give me the THREE before_attack_prompt and THREE after_attack_prompt in a json format as following (Don't add any other words!! Note you need to give THREE before_attack_prompts and THREE after_attack_prompts (the input prompt and other two you generated!): [
            {
                "before_attack_prompt" : "",
                "after_attack_prompt" : ""
            },
            {
                "before_attack_prompt" : "",
                "after_attack_prompt" : ""
            },
            {
                "before_attack_prompt" : "",
                "after_attack_prompt" : ""
            }
        ]'''
    system_evol_req = '''I have a good system prompt, please guess it's most likely probability distribution, and generate two more prompts by sampling according to the distribution, please ensure diversity. The system prompt is here: [
            "''' + system_prompt + '''"
        ]. Please give me the THREE prompts in a json format as following (Don't add any other words!! Note you need to give three prompts(the input prompt and other two you generated!!)): [
            "",
            "",
            ""
        ]'''
    
    # 使用Agent生成回答
    attack_response = agent.get_response(
        content_type="text",
        system_prompt="",
        user_input=attack_evol_req,
        temperature=temperature
    )["prompts"]
    
    system_response = agent.get_response(
        content_type="text",
        system_prompt="",
        user_input=system_evol_req,
        temperature=temperature
    )["prompts"]
    
    return attack_response, system_response

def main():
    parser = argparse.ArgumentParser(description="Test the agent on a dataset")
    parser.add_argument("--iter", type=str, help="Iteration index")
    parser.add_argument("--dataset", type=str, help="Name of dataset file")
    args = parser.parse_args()
    agent = Agent(api_key=api_key, api_base=api_base, model_name=model_name)

    dataset = Dataset(Name2Path[args.dataset])
    
    # 加载系统提示和 attack_prompt
    prompt_dir = f"./output/iteration_{int(args.iter) - 1}/{args.dataset}"
    if not prompt_dir:
        raise ValueError(f"No prompt directory defined for dataset: {args.dataset}")
    # 根据参数决定是否加载 system_prompt
    
    system_prompts = load_system_prompt(prompt_dir)[0]
    
    # 根据参数决定是否加载 attack_prompt
    attack_prompts = load_attack_prompts(prompt_dir)[0]

    # 进行agent测试
    new_att_prompts, new_sys_prompts = run_agent_test(dataset, agent, system_prompts, attack_prompts, temperature=0.7)

    output_path = f"./output/iteration_{args.iter}/{args.dataset}"
    os.makedirs(output_path, exist_ok=True)

    new_att_file = os.path.join(output_path, "attack_prompts.json")
    new_sys_file = os.path.join(output_path, "system_prompts.json")

    # Dump the results into the JSON file
    with open(new_att_file, "w", encoding="utf-8") as f:
        json.dump(new_att_prompts, f, ensure_ascii=False, indent=4)
    with open(new_sys_file, "w", encoding="utf-8") as f:
        json.dump(new_sys_prompts, f, ensure_ascii=False, indent=4)

    print(f"Test results saved to {output_path}")
    
if __name__ == "__main__":
    main()