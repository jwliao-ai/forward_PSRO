import json
import os

# 数据集名称到提示路径的映射
Name2Prompt = {
    "cipher": "prompt_backup/cipher/",
    "logic": "prompt_backup/logic/",
    "math": "prompt_backup/math/",
    "operation": "prompt_backup/operation/",
    "PHY": "prompt_backup/PHY/",
    "puzzle": "prompt_backup/puzzle/",
    "Rule": "prompt_backup/Rule/"
}

def load_system_prompt(prompt_dir):
    """
    从指定目录加载系统提示
    """
    system_prompt_path = os.path.join(prompt_dir, "system_prompt.md")
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"System prompt file not found at: {system_prompt_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load system prompt: {e}")

def load_attack_prompts(prompt_dir):
    """
    从指定目录加载 attack_prompt.json
    """
    attack_prompt_path = os.path.join(prompt_dir, "attack_prompt.json")
    try:
        with open(attack_prompt_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Attack prompt file not found at: {attack_prompt_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode attack prompt JSON: {e}")

def process_jsonl(input_path, output_path):
    """
    读取 JSONL 文件，根据 meta_info 替换 system_prompt 和 attack_prompt，并输出新的 JSONL 文件。
    
    :param input_path: 输入的 JSONL 文件路径
    :param output_path: 输出的 JSONL 文件路径
    """
    # 读取输入的 JSONL 文件
    with open(input_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    # 处理每一行数据
    processed_lines = []
    for line in lines:
        data = json.loads(line.strip())
        
        # 获取 meta_info
        meta_info_list = data.get("meta_info", "").split("_")
        if len(meta_info_list) == 2:
            meta_info = data.get("meta_info", "").split("_")[1]
        else:
            meta_info = data.get("meta_info", "")
        
        # 根据 meta_info 获取对应的提示路径
        prompt_dir = Name2Prompt.get(meta_info)
        if not prompt_dir:
            raise ValueError(f"No prompt directory defined for meta_info: {meta_info}")
        
        # 加载系统提示和 attack_prompt
        system_prompt = load_system_prompt(prompt_dir)
        attack_prompts = load_attack_prompts(prompt_dir)
        
        # 替换 system_prompt 和 attack_prompt
        data["system_prompt"] = system_prompt
        data["attack_prompt"] = attack_prompts["before_attack_prompt"] + "\n{}\n" + attack_prompts["after_attack_prompt"]
        
        
        # 将处理后的数据添加到结果列表
        processed_lines.append(json.dumps(data, ensure_ascii=False))

    # 将处理后的数据写入输出文件
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for line in processed_lines:
            outfile.write(line + '\n')


# 示例调用
input_path = "test.jsonl"  # 输入的 JSONL 文件路径
output_path = "group09_test.jsonl"  # 输出的 JSONL 文件路径
process_jsonl(input_path, output_path)