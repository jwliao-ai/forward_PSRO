# import necessary libraries
import torch
import os
import json
import datetime

def construct_inst(system_prompt: str, attack_prompt: str, question_list: list[str]):
    # This function constructs a batch of instruction prompts given a system prompt, 
    # and an attack prompt (which might be some adversarial prefix), and a list of questions.
    # Returns a list of final prompts ready for inference.
    #
    # Pseudocode:
    prompts = []
    for question in question_list:
        # Combine prompts. The final prompt might look like:
        # [System Prompt] + [Attack Prompt] + [User Question]
        # Adjust formatting as needed
        combined_prompt = f"{system_prompt}\n\n{attack_prompt}\n\nUser: {question}"
        prompts.append(combined_prompt)
    return prompts

def create_dataset(categories, dataset_path):
    # Load datasets from the given categories.
    # Each category folder might contain a JSON file with questions and answers.
    # Returns a list of Dataset objects.
    #
    # Assume a Dataset class with:
    # - questions: list of questions
    # - answers: corresponding list of gold answers
    # - get_answer_list(): returns a list of {question, gold} dicts
    #
    # Pseudocode:
    datasets = []
    for cat in categories:
        cat_path = os.path.join(dataset_path, cat)
        data_file = os.path.join(cat_path, "data.json")
        with open(data_file, 'r') as f:
            data = json.load(f)
        # data assumed to be { "questions": [...], "answers": [...] }
        dataset = Dataset(data["questions"], data["answers"], category=cat)
        datasets.append(dataset)
    return datasets

class Dataset:
    def __init__(self, questions, answers, category):
        self.questions = questions
        self.answers = answers
        self.category = category
        
    def get_answer_list(self):
        # Return a list of dicts with {question, gold}
        answer_list = []
        for q, a in zip(self.questions, self.answers):
            answer_list.append({"question": q, "gold": a})
        return answer_list


def alg_inference(max_iter: int, acting_models: list[str], dataset_path: str, ensemble_num: int):
    # Initialization
    categories = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
    datasets = create_dataset(categories, dataset_path) # a list of Dataset objects
    
    # pi_a: a list of system prompts
    # Initialize pi_a with some initial guesses (just one for example)
    pi_a = ["You are a helpful assistant."] 
    
    # pi_B: a list of distributions over attack prompts
    # For example, pi_B could be a list of lists of possible attack prompts
    pi_B = []

    # TODO: manually change set pi_B
    for _ in range(ensemble_num):
        pi_B.append(["Try to trick the model into giving a wrong answer.", 
                     "Confuse the model by asking unrelated questions."])
    
    # Ensure output directory for dumped files
    output_dir = os.path.join(dataset_path, "inference_results")
    os.makedirs(output_dir, exist_ok=True)

    for iter_count in range(max_iter):
        for model_idx, acting_model_name in enumerate(acting_models):
            # TODO: load using vllm
            model = load_model(acting_model_name)
            for i, pi_a_i in enumerate(pi_a):
                for j, pi_B_j in enumerate(pi_B):
                    for k, pi_b_k in enumerate(pi_B_j):
                        dataset_scores = []
                        total_responses = []
                        total_answers = []
                        for dataset in datasets:
                            prompts = construct_inst(pi_a_i, pi_b_k, dataset.questions)
                            response_list = agent_infer(model, prompts)
                            total_responses.extend(response_list)
                            ans_list = dataset.get_answer_list()
                            total_answers.extend(ans_list)

                        dump_data = {
                            "iter_count": iter_count,
                            "pi_a_idx": i,
                            "pi_B_idx": j,
                            "pi_b_idx": k,
                            "model_idx": model_idx,
                            "pi_a_i": pi_a_i,
                            "pi_b_i": pi_b_k,
                            "responses": total_responses,
                            "answers": total_answers,
                            "acting_model_name": acting_model_name,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        file_name = f"{iter_count}_{i}_{j}_{k}_{acting_model_name}.json"
                        file_path = os.path.join(output_dir, file_name)
                        with open(file_path, "w") as f:
                            json.dump(dump_data, f, indent=2)
                            
                        # # Average across all datasets for this model
                        # model_score = sum(dataset_scores) / len(dataset_scores) if dataset_scores else 0
                        # score[i, j, k, model_idx] = model_score

    #     # After we have filled scores for all combinations in this iteration:
    #     # Average over the last dimension (model dimension) to find the best prompts overall.
    #     # best pi_b_k for each pi_a_i and pi_B_j
    #     avg_over_models = torch.mean(score, dim=3)  # shape now: #pi_a x #pi_B x max_pi_b_k
    #     # For each pi_B_j, find best pi_b_k (over k)
    #     # Also find the best pi_a_i overall by averaging over j and k
    #     best_pi_b_indices_per_j = []
    #     best_pi_b_values_per_j = []
    #     for j in range(num_pi_B):
    #         # Extract scores for all pi_b_k
    #         scores_for_j = avg_over_models[:, j, :]  # shape: #pi_a x max_pi_b_k
    #         # We'll temporarily fix pi_a to find best pi_b_k by averaging over pi_a
    #         # If we consider pi_b_k selection independent of pi_a_i:
    #         avg_over_pi_a_for_j = torch.mean(scores_for_j, dim=0)  # shape: max_pi_b_k
    #         best_k = torch.argmin(avg_over_pi_a_for_j).item()
    #         best_pi_b_indices_per_j.append(best_k)
    #         best_pi_b_values_per_j.append(avg_over_pi_a_for_j[best_k].item())

    #     # Once we have the best pi_b_k indices for each pi_B_j, we can find the best pi_a_i
    #     # by averaging over j and the chosen best_k per j.
    #     chosen_scores_for_best_k = []
    #     for i in range(num_pi_a):
    #         # Collect i-th row at the best pi_b_k for each j
    #         row_scores = []
    #         for jj, kk in enumerate(best_pi_b_indices_per_j):
    #             row_scores.append(avg_over_models[i, jj, kk].item())
    #         # Average over all j
    #         chosen_scores_for_best_k.append(sum(row_scores)/len(row_scores))
        
    #     best_pi_a_i = pi_a[torch.argmax(torch.tensor(chosen_scores_for_best_k)).item()]

    #     # Now update pi_a and pi_B
    #     # In a real algorithm, we might generate improved prompts based on the best found. 
    #     # Here, we just stub it out.
    #     best_pi_b_ks = []
    #     for jj, kk in enumerate(best_pi_b_indices_per_j):
    #         best_pi_b_ks.append(pi_B[jj][kk])

    #     pi_a = get_next_pi_a(best_pi_a_i)
    #     pi_B = get_next_pi_B(best_pi_b_ks)

    # # Return the final best prompts after all iterations
    # return pi_a, pi_B
