import time
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
from cua_docker_actions import handle_model_action, get_screenshot
from .config import MODEL_NAME

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def computer_use_loop(vm, response):
    """
    Repeatedly processes model actions and sends updated screenshots,
    acknowledging any safety checks as needed.
    """
    while True:
        # Parse computer_call actions
        output_items = response.output
        computer_calls = [
            item for item in output_items
            if (getattr(item, 'type', None) if not isinstance(item, dict) else item.get("type")) == "computer_call"
        ]
        if not computer_calls:
            print("No more computer_call found. Model output:")
            for item in output_items:
                print(item)
            break  # Exit loop

        computer_call = computer_calls[0]
        last_call_id = getattr(computer_call, "call_id", None) or computer_call.get("call_id")
        action = getattr(computer_call, "action", None) or computer_call.get("action")

        # --- SAFETY CHECK HANDLING ---
        if hasattr(computer_call, "pending_safety_checks"):
            pending_checks = getattr(computer_call, "pending_safety_checks", [])
        else:
            pending_checks = computer_call.get("pending_safety_checks", [])
        acknowledged_safety_checks = []
        if pending_checks:
            print("\n⚠️ SAFETY CHECK(S) DETECTED!")
            for check in pending_checks:
                print(f"Safety check: [{check.code}] {check.message}")
                # In a real app, you would show this to the user and require confirmation!
                # Here, we'll auto-acknowledge for the example (not recommended for prod!)
                acknowledged_safety_checks.append(check)

        # --- EXECUTE THE ACTION ---
        step_start = time.perf_counter()
        action_start = time.perf_counter()
        handle_model_action(action, vm)
        action_end = time.perf_counter()
        print(f"Action execution took {action_end - action_start:.2f} seconds")

        # --- CAPTURE SCREENSHOT ---
        screenshot_start = time.perf_counter()
        screenshot_bytes = get_screenshot(vm)
        screenshot_end = time.perf_counter()
        print(f"Screenshot capture took {screenshot_end - screenshot_start:.2f} seconds")
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        image_url = f"data:image/jpeg;base64,{screenshot_base64}"

        # --- SEND RESULT BACK TO CUA (repeat the loop) ---
        input_dict = {
            "type": "computer_call_output",
            "call_id": last_call_id,
            "output": {
                "type": "input_image",
                "image_url": image_url,
                "detail": "low"
            }
        }
        if acknowledged_safety_checks:
            input_dict["acknowledged_safety_checks"] = acknowledged_safety_checks

        api_start = time.perf_counter()
        response = client.responses.create(
            model=MODEL_NAME,
            previous_response_id=getattr(response, "id", None) or getattr(response, "response_id", None),
            tools=[{
                "type": "computer_use_preview",
                "display_width": 1024,
                "display_height": 768,
                "environment": "linux"
            }],
            input=[input_dict],
            truncation="auto"
        )
        api_end = time.perf_counter()
        print(f"API call took {api_end - api_start:.2f} seconds")

    return response

# Example usage:
if __name__ == "__main__":
    from cua_request import client as initial_client, vm
    # Read the prompt from prompt.txt in the project root
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompt", "prompt.txt"))
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read().strip()
    content = [
        {
            "type": "input_text",
            "text": prompt_text
        }
    ]
    # Get initial response
    response = initial_client.responses.create(
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
    computer_use_loop(vm, response)
