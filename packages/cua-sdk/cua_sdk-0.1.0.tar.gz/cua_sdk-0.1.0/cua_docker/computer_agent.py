import os
import base64
import time
from dotenv import load_dotenv
from .cua_docker_actions import handle_model_action, get_screenshot

# Default config (can be moved to config.py)
DEFAULTS = {
    "openai_api_key": None,
    "llm_model": "computer-use-preview",
    "docker_container_name": "cua-image",
    "docker_display": ":99",
    "sleep_time": 0.2,
    "screen_width": 1024,
    "screen_height": 768,
    "screenshot_format": "jpeg",
    "screenshot_detail": "low",
    "prompt_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompt.txt")),
}

class ComputerAgent:
    """
    A reusable, configurable agent for automating tasks in a virtual desktop via OpenAI CUA models.
    """

    def __init__(self, **kwargs):
        load_dotenv()
        # Config precedence: constructor > env > defaults
        self.config = {}
        for key, default in DEFAULTS.items():
            env_key = key.upper()
            self.config[key] = (
                kwargs.get(key)
                or os.environ.get(env_key)
                or default
            )
        self._client = None
        self._vm = {
            "container_name": self.config["docker_container_name"],
            "display": self.config["docker_display"],
        }
        self._session_active = False
        self._history = []
        self._last_response = None

    def start(self):
        """Initialize the agent/session."""
        from openai import OpenAI
        self._client = OpenAI(api_key=self.config["openai_api_key"])
        self._session_active = True
        print("[ComputerAgent] Session started.")

    def send_prompt(self, prompt: str):
        """Send a prompt/instruction to the agent (e.g., a job URL or task)."""
        if not self._session_active:
            self.start()
        # Replace {JOB_URL} in the prompt if present
        if "{JOB_URL}" in prompt:
            prompt = prompt.replace("{JOB_URL}", self.config.get("job_url", ""))
        content = [{"type": "input_text", "text": prompt}]
        response = self._client.responses.create(
            model=self.config["llm_model"],
            tools=[{
                "type": "computer_use_preview",
                "display_width": self.config["screen_width"],
                "display_height": self.config["screen_height"],
                "environment": "linux",
            }],
            input=[{"role": "user", "content": content}],
            reasoning={"summary": "concise"},
            truncation="auto"
        )
        self._last_response = response
        self._history.append(response)
        # Main loop (single prompt)
        while True:
            output_items = response.output
            computer_calls = [
                item for item in output_items
                if (getattr(item, 'type', None) if not isinstance(item, dict) else item.get("type")) == "computer_call"
            ]
            if not computer_calls:
                print("No more computer_call found. Model output:")
                for item in output_items:
                    print(item)
                break
            computer_call = computer_calls[0]
            last_call_id = getattr(computer_call, "call_id", None) or computer_call.get("call_id")
            action = getattr(computer_call, "action", None) or computer_call.get("action")
            # Safety checks
            if hasattr(computer_call, "pending_safety_checks"):
                pending_checks = getattr(computer_call, "pending_safety_checks", [])
            else:
                pending_checks = computer_call.get("pending_safety_checks", [])
            acknowledged_safety_checks = []
            if pending_checks:
                print("\n⚠️ SAFETY CHECK(S) DETECTED!")
                for check in pending_checks:
                    print(f"Safety check: [{check.code}] {check.message}")
                    acknowledged_safety_checks.append(check)
            # Action execution
            action_start = time.perf_counter()
            handle_model_action(action, self._vm)
            action_end = time.perf_counter()
            print(f"Action execution took {action_end - action_start:.2f} seconds")
            # Screenshot
            screenshot_start = time.perf_counter()
            screenshot_bytes = get_screenshot(self._vm)
            screenshot_end = time.perf_counter()
            print(f"Screenshot capture took {screenshot_end - screenshot_start:.2f} seconds")
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            image_url = f"data:image/{self.config['screenshot_format']};base64,{screenshot_base64}"
            # Send result back to CUA
            input_dict = {
                "type": "computer_call_output",
                "call_id": last_call_id,
                "output": {
                    "type": "input_image",
                    "image_url": image_url,
                    "detail": self.config["screenshot_detail"]
                }
            }
            if acknowledged_safety_checks:
                input_dict["acknowledged_safety_checks"] = acknowledged_safety_checks
            api_start = time.perf_counter()
            response = self._client.responses.create(
                model=self.config["llm_model"],
                previous_response_id=getattr(response, "id", None) or getattr(response, "response_id", None),
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": self.config["screen_width"],
                    "display_height": self.config["screen_height"],
                    "environment": "linux"
                }],
                input=[input_dict],
                truncation="auto"
            )
            api_end = time.perf_counter()
            print(f"API call took {api_end - api_start:.2f} seconds")
            self._last_response = response
            self._history.append(response)

    def change_config(self, **kwargs):
        """Dynamically update any configuration parameter."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                print(f"[ComputerAgent] Config updated: {key} = {value}")
            else:
                print(f"[ComputerAgent] Unknown config key: {key}")

    def stop(self):
        """Gracefully stop/close the agent/session."""
        self._session_active = False
        self._client = None
        print("[ComputerAgent] Session stopped.")

    def reset_history(self):
        """Reset the conversation or action history."""
        self._history = []
        print("[ComputerAgent] History reset.")

    def get_screenshot(self):
        """Retrieve the latest screenshot from the agent's environment."""
        screenshot_bytes = get_screenshot(self._vm)
        return screenshot_bytes

    @property
    def last_response(self):
        return self._last_response

    @property
    def history(self):
        return self._history
