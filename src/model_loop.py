import os
import signal
import subprocess
import time

if __name__ == "__main__":
    process = subprocess.Popen("vllm serve \"/inspire/ssd/ws-7c23bd1d-9bae-4238-803a-737a35480e18/knowledge/public/internlm2_5-20b-chat\" --allowed-local-media-path=\"/inspire/hdd/ws-7c23bd1d-9bae-4238-803a-737a35480e18/knowledge/xuesheng9-student09/\" \
        --dtype float16 --api-key \"empty\" --port 8002 --host 127.0.0.1 --served-model-name \"not_important\" --trust-remote-code \
        --tensor_parallel_size 8 --gpu_memory_utilization 0.87 --seed 42", shell=True, executable="/bin/bash")

    print(f"PID: {process.pid}")

    # 主进程等待 5 秒
    time.sleep(5)

    # 使用 os.kill 终止子进程
    print(f"主进程终止子进程 (PID: {process.pid})")
    os.kill(process.pid, signal.SIGTERM)

    # 检查子进程是否已终止
    process.wait()  # 等待子进程完全退出
    print(f"子进程状态码: {process.returncode}")