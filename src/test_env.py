from openai import OpenAI
import openai

openai_api_key = "empty"
# openai_api_base = "http://localhost:8000/v1"
openai_api_base = "http://localhost:8002/v1"

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# image_url = "https://github.com/Rainforest-Sun/RISC-V-Simulator-Final-Version/blob/master/Pipeline%20Design.png"
# image_url = "file://inspire/hdd/ws-7c23bd1d-9bae-4238-803a-737a35480e18/knowledge/xuesheng9-student09 \
#     /img/question/004336/0043361.png"
image_url = "file://./img/question/004336/0043361.png"

models = client.models.list()
model = models.data[0].id

chat_completion = client.chat.completions.create(
    messages=[{
            "role": "system",
            "content": "You are a helpful assistant."
        }, 
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        },
    ],
    model=model,
)

print("Chat completion results:")
messages = [choice.message.content for choice in chat_completion.choices]
print(messages)