
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load the token from backend/.env
load_dotenv()

token = os.getenv("HF_TOKEN")

if not token:
    raise ValueError(
        "HF_TOKEN not found. Check your backend/.env file."
    )

client = InferenceClient(
    api_key=token,
    model="openai/gpt-oss-120b:fastest",
)

print("Connecting to the hosted LLM...")

response = client.chat_completion(
    messages=[
        {
            "role": "system",
            "content": (
                "You are Sorim.AI, an IT support assistant. "
                "Answer clearly and briefly."
            ),
        },
        {
            "role": "user",
            "content": (
                "An employee cannot connect to the company VPN. "
                "Give two safe troubleshooting steps."
            ),
        },
    ],
    max_tokens=150,
    temperature=0.2,
)

print("\nLLM response:")
print(response.choices[0].message.content)
