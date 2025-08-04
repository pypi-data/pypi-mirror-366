import os
from openai import OpenAI
from dotenv import load_dotenv
from .config import MODEL_NAME

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "sk-your-placeholder-key":
    raise ValueError("Please set your real OpenAI API key in the .env file.")

client = OpenAI(api_key=api_key)

# Read the prompt from prompt.txt in the project root
prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompt", "prompt.txt"))
with open(prompt_path, "r", encoding="utf-8") as f:
    prompt_text = f.read().strip()

# Optional: attach a screenshot (uncomment and set the path if needed)
# import base64
# with open("screenshot.png", "rb") as image_file:
#     screenshot_base64 = base64.b64encode(image_file.read()).decode('utf-8')
#     input_image = {
#         "type": "input_image",
#         "image_url": f"data:image/png;base64,{screenshot_base64}"
#     }
# else:
#     input_image = None

content = [
    {
        "type": "input_text",
        "text": prompt_text
    }
    # Uncomment below to add screenshot context
    # , input_image
]

response = client.responses.create(
    model=MODEL_NAME,
    tools=[{
        "type": "computer_use_preview",
        "display_width": 1024,
        "display_height": 768,
        "environment": "linux",
    }],
    input=[
        {
            "role": "user",
            "content": content
        }
    ],
    reasoning={
        "summary": "concise"
    },
    truncation="auto"
)

from cua_docker_actions import handle_model_action, get_screenshot
import base64

print("CUA Model Output:")
output_items = response.output  # Should be a list

# VM config for Docker container
vm = {
    "container_name": "cua-image",
    "display": ":99"
}

if not isinstance(output_items, list):
    print("Unexpected response format:", output_items)
else:
    for item in output_items:
        # Convert item to dict if it's a Pydantic model or similar
        if hasattr(item, "model_dump"):
            item_dict = item.model_dump()
        elif hasattr(item, "__dict__"):
            item_dict = vars(item)
        else:
            item_dict = item

        if isinstance(item_dict, dict):
            if item_dict.get("type") == "reasoning":
                summary = item_dict.get("summary", [])
                if summary and isinstance(summary, list):
                    summary_text = summary[0].get("text", "")
                    print("Reasoning:", summary_text)
            elif item_dict.get("type") == "computer_call":
                action = item_dict.get("action", {})
                print("Executing action:", action)
                handle_model_action(action, vm)
                # Step 4: Capture screenshot after action
                screenshot_bytes = get_screenshot(vm)
                with open("debug_screenshot.png", "wb") as f:
                    f.write(screenshot_bytes)
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                print("Screenshot base64 (truncated):", screenshot_base64[:60], "...")
            else:
                print("Other item:", item_dict)
        else:
            print("Other item (non-dict):", item_dict)
