import subprocess
import time
from .config import SCROLL_AMOUNT

def docker_exec(cmd: str, container_name: str, decode=True) -> str:
    """
    Execute a shell command inside a running Docker container.
    """
    safe_cmd = cmd.replace('"', '\\"')
    docker_cmd = f'docker exec {container_name} sh -c "{safe_cmd}"'
    output = subprocess.check_output(docker_cmd, shell=True)
    if decode:
        return output.decode("utf-8", errors="ignore")
    return output

def scroll_form_container(direction, amount, vm):
    """
    Scroll the application form container in the given direction ('down' or 'up') by the specified amount (pixels).
    This function always uses xdotool click 5 for down and click 4 for up, regardless of the amount.
    """
    if direction == "down":
        print(f"Scrolling form container down by {amount} pixels (using xdotool click 5)")
        docker_exec(f"DISPLAY={vm['display']} xdotool click 5", vm["container_name"])
    elif direction == "up":
        print(f"Scrolling form container up by {amount} pixels (using xdotool click 4)")
        docker_exec(f"DISPLAY={vm['display']} xdotool click 4", vm["container_name"])
    else:
        print(f"Unknown scroll direction: {direction}")

def handle_model_action(action, vm):
    """
    Given a computer action (e.g., click, type, scroll, screenshot, etc.),
    execute the corresponding operation on the Docker environment.
    vm: an object or dict with at least 'container_name' and 'display' fields.
    Supports both dict and object action types.
    """
    # Helper to get attribute or dict value
    def get_val(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    action_type = get_val(action, "type")

    try:
        if action_type == "click":
            x = int(get_val(action, "x"))
            y = int(get_val(action, "y"))
            button = get_val(action, "button", "left")
            button_map = {"left": 1, "middle": 2, "right": 3}
            b = button_map.get(button, 1)
            print(f"Action: click at ({x}, {y}) with button '{button}'")
            docker_exec(f"DISPLAY={vm['display']} xdotool mousemove {x} {y} click {b}", vm["container_name"])

        elif action_type == "scroll":
            # Ignore model's scroll parameters, always use our function
            direction = "down"
            amount = SCROLL_AMOUNT
            scroll_form_container(direction, amount, vm)

        elif action_type == "keypress":
            keys = get_val(action, "keys")
            for k in keys:
                print(f"Action: keypress '{k}'")
                if k.lower() == "enter":
                    docker_exec(f"DISPLAY={vm['display']} xdotool key 'Return'", vm["container_name"])
                elif k.lower() == "space":
                    docker_exec(f"DISPLAY={vm['display']} xdotool key 'space'", vm["container_name"])
                else:
                    docker_exec(f"DISPLAY={vm['display']} xdotool key '{k}'", vm["container_name"])

        elif action_type == "type":
            text = get_val(action, "text")
            print(f"Action: type text: {text}")
            docker_exec(f"DISPLAY={vm['display']} xdotool type '{text}'", vm["container_name"])

        elif action_type == "wait":
            print(f"Action: wait (minimal)")
            time.sleep(0.1)

        elif action_type == "screenshot":
            print(f"Action: screenshot")
            # Save screenshot as screenshot.png in the container's home directory
            docker_exec(f"DISPLAY={vm['display']} import -window root screenshot.png", vm["container_name"])

        else:
            print(f"Unrecognized action: {action}")

    except Exception as e:
        print(f"Error handling action {action}: {e}")

def get_screenshot(vm):
    """
    Takes a screenshot of the entire desktop inside the Docker container.
    Returns raw bytes (JPEG format).
    """
    cmd = (
        f"export DISPLAY={vm['display']} && "
        "import -window root jpeg:-"
    )
    screenshot_bytes = docker_exec(cmd, vm["container_name"], decode=False)
    print(f"Screenshot size: {len(screenshot_bytes)/1024:.1f} KB")
    return screenshot_bytes

# Example usage:
if __name__ == "__main__":
    # Example VM config
    vm = {
        "container_name": "cua-image",
        "display": ":99"
    }
    # Example action
    action = {
        "type": "click",
        "x": 100,
        "y": 200,
        "button": "left"
    }
    handle_model_action(action, vm)

    # Capture screenshot after action
    screenshot_bytes = get_screenshot(vm)
    # Save to file for debugging
    with open("debug_screenshot.png", "wb") as f:
        f.write(screenshot_bytes)
    # Encode for API
    import base64
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
    print("Screenshot base64 (truncated):", screenshot_base64[:60], "...")
