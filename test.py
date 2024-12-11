import argparse
import json
import os
import numpy as np
from tqdm import tqdm
from datetime import datetime
from src.dataset import Dataset  
from src.agent import Agent  

Name2Path = {
    "cipher" : "data/cipher.json",
    "logic" : "data/logic.json",
    "math" : "data/math.json",
    "operation" : "data/operation.json",
    "PHY" : "data/PHY.json",
    "puzzle" : "data/puzzle.json",
    "Rule" : "data/Rule.json"
}

def parse_arguments():
    """
    使用 argparse 解析命令行参数
    """
    parser = argparse.ArgumentParser(description="Test the agent on a dataset")
    parser.add_argument("--iter", type=str, help="Iteration index")
    parser.add_argument("--dataset", type=str, help="Name of dataset file")
    parser.add_argument("--api_base", type=str, help="OpenAI API base url")
    parser.add_argument("--api_key", type=str, help="OpenAI API key")
    parser.add_argument("--model_name", type=str, help="Name of the agent's model to test")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for the agent's response")
    
    return parser.parse_args()

def load_system_prompt(prompt_dir):
    """
    从指定目录加载系统提示
    """
    system_prompt_path = os.path.join(prompt_dir, "system_prompts.json")
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
    attack_prompt_path = os.path.join(prompt_dir, "attack_prompts.json")
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
    response_list = []
    answer_list = []
    
    for idx in tqdm(range(len(dataset))):
        data_item = dataset[idx]
        data_id = data_item.get('id', '')
        question = data_item.get('question', '')
        answer = data_item.get('answer', '')
        if type(answer) == list:
            answer = answer[0]
        
        # 构造 user_input：在 question 前后插入 attack_prompts（如果启用）
        before_attack_prompt = attack_prompts.get("before_attack_prompt", "")
        after_attack_prompt = attack_prompts.get("after_attack_prompt", "")
        user_input = f"{before_attack_prompt}\n{question}\n{after_attack_prompt}"
        
        # 判断是否为多模态问题
        if data_item["img_path"] != "":  # 假设多模态问题包含 "image_url" 字段
            image_url = data_item["img_path"]
            content_type = "multimodal"
        else:
            image_url = None
            content_type = "text"
        
        # 使用Agent生成回答
        response = agent.get_response(
            content_type=content_type,
            system_prompt=system_prompt,
            user_input=user_input,
            image_url=image_url,
            temperature=temperature
        )
        
        response_list.append(response)
        answer_list.append(answer)
        
    result = {
        "response_list": response_list,
        "answer_list": answer_list
    }
    return result

def is_answer_correct(expected_answer, generated_answer, agent):
    """
    Evaluate whether the generated answer matches the expected answer.

    :param expected_answer: The expected answer.
    :param generated_answer: The generated answer.
    :return: True if the generated answer is correct, False otherwise.
    """
    # Create a prompt for the agent to evaluate the correctness
    system_prompt = """
        You are given pairs of “expected answer” and “generated answer.” Your task is to compare them and determine if they match. The answers are considered a match if:
	1.	They have the same core meaning or correct result, even if the format or wording is different.
	2.	The generated answer contains additional explanation but still reaches the same conclusion as the expected answer.

If the generated answer is incorrect or does not match the expected answer, it is not a match.

Respond with only “Yes” or “No” for each pair. Do not include explanations. Directly give your judgment.

Example:
	•	Expected Answer: [[-14+52i]]
	•	Generated Answer: “The final answer is \\(-14 + 52i\\).”
	•	Your Response: Yes
	•	Expected Answer: [“4”]
	•	Generated Answer: “The value is 6 due to calculation.”
	•	Your Response: No

Now, compare the following pairs:
    """
    user_input = f"""
        Expected Answer: {str(expected_answer)}
        Generated Answer: {str(generated_answer)}
        Is the generated answer correct? (yes/no)
    """

    # Get the evaluation response from the agent
    try:
        response = agent.get_response(
            content_type="text",
            system_prompt=system_prompt,
            user_input=user_input,
            temperature=0.3
        )
        # Return True if the response is 'yes', otherwise False
        return response.strip().lower() == "yes"
    except Exception as e:
        print(f"Error evaluating answer: {str(e)}")
        return False


def main():
    # 解析命令行参数
    args = parse_arguments()
    args.model_name_0 = "Qwen2-VL-72B"
    args.api_key_0 = "empty"
    args.api_base_0 = "http://localhost:8002/v1"
    args.model_name_1 = "internlm2_5-20b"
    args.api_key_1 = "empty"
    args.api_base_1 = "http://localhost:8003/v1"


    dataset = Dataset(Name2Path.get(args.dataset))    
    prompt_dir = f"./output/iteration_{int(args.iter)}/{args.dataset}"
    if not prompt_dir:
        raise ValueError(f"No prompt directory defined for dataset: {args.dataset}")
    system_prompts = load_system_prompt(prompt_dir) # list
    attack_prompts = load_attack_prompts(prompt_dir) # list

    # 创建Agent对象
    agent_0 = Agent(api_key=args.api_key_0, api_base=args.api_base_0, model_name=args.model_name_0)
    agent_1 = Agent(api_key=args.api_key_1, api_base=args.api_base_1, model_name=args.model_name_1)

    results = []
    score = np.zeros((len(system_prompts), len(attack_prompts)), dtype=np.float64)
    
    for sys_prompt_idx, sys_prompt in enumerate(system_prompts):
        for att_prompt_idx, att_prompt in enumerate(attack_prompts):
            result = {}
            result["response_list"] = []
            result["answer_list"] = []
            result_0 = run_agent_test(dataset, agent_0, sys_prompt, att_prompt, temperature=args.temperature)
            result["response_list"].extend(result_0["response_list"])
            result["answer_list"].extend(result_0["answer_list"])
            result_1 = run_agent_test(dataset, agent_1, sys_prompt, att_prompt, temperature=args.temperature)
            result["response_list"].extend(result_1["response_list"])
            result["answer_list"].extend(result_1["answer_list"])
            result['sys_prompt_idx'] = sys_prompt_idx
            result['att_prompt_idx'] = att_prompt_idx
            result['sys_prompt'] = sys_prompt
            result['att_prompt'] = att_prompt
            results.append(result)
    
    for entry in tqdm(results):
        total_count = 0.
        correct_count = 0.
        for response, answer in zip(entry['response_list'], entry['answer_list']):
            total_count += 1
            is_correct = is_answer_correct(answer, response, agent_0)
            if is_correct:
                correct_count += 1
        acc = correct_count / total_count
        entry["accuracy"] = acc
        score[entry["sys_prompt_idx"]][entry["att_prompt_idx"]] = np.float64(acc)
        
    system_prompt_score = score.sum(axis=-1)
    attack_prompt_score = score.sum(axis=0)
    best_system_prompt_idx = np.argmax(system_prompt_score)
    best_attack_prompt_idx = np.argmax(attack_prompt_score)
    best_system_prompt = [system_prompts[best_system_prompt_idx]]
    best_attack_prompt = [
        {
            "before_attack_prompt": attack_prompts[best_attack_prompt_idx]["before_attack_prompt"],
            "after_attack_prompt": attack_prompts[best_attack_prompt_idx]["after_attack_prompt"],
        }
    ]
        
    output_path = f"output/iteration_{args.iter}/{args.dataset}"
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "result.json")
    best_system_prompt_file = os.path.join(output_path, "best_system_prompt.json")
    best_attack_prompt_file = os.path.join(output_path, "best_attack_prompt.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    with open(best_system_prompt_file, "w", encoding="utf-8") as f:
        json.dump(best_system_prompt, f, ensure_ascii=False, indent=4)
    with open(best_attack_prompt_file, "w", encoding="utf-8") as f:
        json.dump(best_attack_prompt, f, ensure_ascii=False, indent=4)

    print(f"files saved to {output_path}")


if __name__ == "__main__":
    main()