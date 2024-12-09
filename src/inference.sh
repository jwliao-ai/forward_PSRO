model_path="/inspire/ssd/ws-7c23bd1d-9bae-4238-803a-737a35480e18/knowledge/public/Qwen2-VL-72B-Instruct"
# model_path="/inspire/ssd/ws-7c23bd1d-9bae-4238-803a-737a35480e18/knowledge/public/Qwen2.5-72B-Instruct"
# model_path="/inspire/ssd/ws-7c23bd1d-9bae-4238-803a-737a35480e18/knowledge/public/internlm2_5-20b-chat"
api_key="empty"
model_name="Qwen2-VL-72B"
# model_name="Qwen2.5-72B"
# model_name="internlm2_5-20b"
tensor_parallel_size=8

vllm serve ${model_path} --allowed-local-media-path="/inspire/hdd/ws-7c23bd1d-9bae-4238-803a-737a35480e18/knowledge/xuesheng9-student09/" --dtype float16 --api-key ${api_key} --port 8000 --host 127.0.0.1 --served-model-name ${model_name} --trust-remote-code --tensor_parallel_size ${tensor_parallel_size} --gpu_memory_utilization 0.8 --seed 42

pid=$!

sleep 5

kill -SIGINT $pid