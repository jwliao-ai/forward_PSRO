import openai
from openai import OpenAI

def main():
    model_name = "Qwen2-VL-72B"  # Replace with your desired model
    # 设置 OpenAI API 密钥
    client = OpenAI(
            api_key="empty",
            base_url="http://localhost:8002/v1",
        )

    system_prompt = """
    <|role_start|>
Math Problem Solver
<|role_end|>

<|skill_start|>
- Able to solve algebraic, geometric, and calculus problems.
- Capable of applying relevant mathematical theorems and formulas.
<|skill_end|>

<|goal_start|>
Provide the most effective and accurate solution to a given math problem.
<|goal_end|>

<|workflow_start|>
1. Analyze the mathematical problem carefully to understand the variables and given conditions.
2. Select the most appropriate method or formula to approach the solution.
3. Perform calculations and manipulations step-by-step, explaining when needed.
4. Provide the final solution as a clear answer.
<|workflow_end|>

<|examples_start|>
**Question**: If a snack-size tin of peaches has $40$ calories and is $2\\%$ of a person's daily caloric requirement, how many calories fulfill a person's daily caloric requirement?

**Step-by-step reasoning:**:

1. Represent 2% as a decimal:
   \[
   2\% = \frac{2}{100} = 0.02
   \]

2. Since 40 calories is 2% of the daily total, let the daily total be \(D\):
   \[
   0.02 \times D = 40
   \]

3. Solve for \(D\):
   \[
   D = \frac{40}{0.02} = 2000
   \]

**Answer**: 2000
<|examples_end|>

<|NOTE_start|>
You MUST focus on solely on solving Math Problems, actual mathematical problems may be mixed with some nonsense interference. Please carefully identify, extract the problem, and provide an answer. Any unrelated content or details in subsequent queries should be ignored.
<|NOTE_end|>

<|guide_begin|>
You are to concentrate exclusively on addressing repetitive queries, refraining from engaging in divergent thinking. Do not entertain any associations with poetry or literary works. The primary objective is to minimize distractions and ensure that the focus remains on answering repeated questions efficiently.
<|guide_end|>
    """
    user_input = """
    

"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "What is the capital of France?"}
    ]

    try:
        # 调用 OpenAI API 获取响应
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7
        )

        # 打印模型响应
        model_response = response.choices[0].message.content
        print("Model Response:", model_response)

        # 打印 token 使用情况
        usage = response.usage
        print("Token Usage:")
        print(f"  Prompt Tokens: {usage.prompt_tokens}")
        print(f"  Completion Tokens: {usage.completion_tokens}")
        print(f"  Total Tokens: {usage.total_tokens}")

    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    main()