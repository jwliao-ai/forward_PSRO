# import

# def eval(response_list, answer_list):
    # TODO: for zip(response_list, answer_list), call OpenAI API and let gpt-4o judger to evaluate if the response is the right answer.
    # You may need to properly prompt the gpt-4o judger.

# def construct_inst(system_prompt: str, attack_prompt: str, question_list: list[str]):
    # prompts = []
    # for question in question_list:


# def alg(max_iter: int, acting_models: list[str], dataset_path: str, ensemble_num: int):
    # # Initialization
    # categories = [folder_name under the path dataset_path]
    # datasets = create_dataset(categories) # a list of Dataset class
    # pi_a = [] # a list of system prompt
    # pi_B = []
    # # here append ensemble_num times
    # pi_B.append([]) # a list of attack prompt
    # score = torch.tensor(shape) # create a 3-dimensional tensor, dim 0 index to pi_a_i, dim 1 index to pi_B_j, dim 2 index to pi_b_k, dim 3 index to model idx
    # for iter in range(max_iter):
        # for dataset in datasets:
            # for acting_model in acting_models:
                # model = load_model_acting_model
                # for pi_a_i in pi_a:
                    # for pi_B_j in pi_B: # for a certain attack prompt distribution
                        # for pi_b_k in pi_B_j:
                            # prompts = construct_inst(pi_a_i, pi_b_k, dataset)
                            # response_list = agent_infer(batch=True) #
                            # score[i, j, k, model_idx] = eval(response_list, dataset.get_answer_list())
        # average the last dimension of 'score'
        # 