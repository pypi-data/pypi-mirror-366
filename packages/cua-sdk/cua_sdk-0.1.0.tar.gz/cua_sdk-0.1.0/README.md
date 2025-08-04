# CUA Agent SDK

A reusable, pip-installable Python SDK for controlling a computer-using agent in a virtual desktop (e.g., Docker, VNC, or any custom environment) using OpenAI CUA models. The SDK is fully configurable, class-based, and easy to integrate into any Python project.

---

## 🚀 Installation

**Install from source:**
```sh
pip install .
```
or (when published):
```sh
pip install cua-sdk
```

---

## 🛠️ Usage

```python
from cua_sdk import ComputerAgent

agent = ComputerAgent(
    openai_api_key="sk-...",
    llm_model="computer-use-preview",
    docker_container_name="cua-image",
    docker_display=":99",
    sleep_time=0.2,
    screen_width=800,
    screen_height=600,
    screenshot_format="jpeg",
    screenshot_detail="low",
    prompt_path="prompt.txt",
    # ...any other config
)

agent.start()
agent.send_prompt("Apply to this job: https://company.com/apply/123")
agent.change_config(llm_model="gpt-4.1-mini", sleep_time=0.1)
screenshot = agent.get_screenshot()
agent.reset_history()
agent.stop()
```

- All parameters can be set via constructor, environment variables, or config defaults.
- The agent is fully modular and can be used in any Python project.

---

## ⚙️ Configuration

**Parameters (constructor, env, or config):**
- `openai_api_key`
- `llm_model`
- `docker_container_name`
- `docker_display`
- `sleep_time`
- `screen_width`, `screen_height`
- `screenshot_format` (`jpeg`/`png`)
- `screenshot_detail` (`low`/`high`)
- `prompt_path`
- ...and more

**Precedence:**  
Constructor argument > Environment variable > SDK default

---

## 📦 Project Structure

```
cua-sdk/
│
├── cua_sdk/
│   ├── __init__.py
│   ├── agent.py           # Main class-based SDK
│   └── ... (other helpers)
├── setup.py
├── pyproject.toml
├── README.md
├── requirements.txt
├── examples/              # (optional) usage scripts
├── docker/                # (optional) Dockerfiles, utilities
```

---

## 📝 Notes

- The SDK does **not** require Docker or any specific environment—just pass the right config for your use case.
- Example Dockerfiles and scripts are provided in `/docker` for convenience, but are not required for SDK use.
- You can use your own prompt templates, models, and agent configuration.

---

## 🧑‍💻 Author

- [Elias Tsoukatos](https://github.com/eliastsoukatos)

---

**Build universal, automated desktop agents with the CUA Agent SDK!**
