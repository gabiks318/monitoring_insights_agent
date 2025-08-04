import os
import openai
import logging
import re
from jinja2 import StrictUndefined, Template
from smolagents.local_python_executor import LocalPythonExecutor, InterpreterError

from src.tools import CloudWatchListMetricsTool
from tools import FinalAnswerTool, CloudWatchGetMetricsTool
from prompts import SYSTEM_PROMPT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

BASE_BUILTIN_MODULES = [
    "datetime", "time", "math", "re", "json", "timedelta"
]

client = openai.OpenAI()


class CloudWatchInsightsAgent:
    def __init__(self, model="gpt-4o", max_steps=20):
        self.model = model
        self.max_steps = max_steps
        self.tools = {
            tool.name: tool for tool in [FinalAnswerTool(), CloudWatchGetMetricsTool(), CloudWatchListMetricsTool()]
        }
        self.authorized_imports = BASE_BUILTIN_MODULES

        self.python_executor = LocalPythonExecutor(
            additional_authorized_imports=[]
        )
        self.python_executor.send_tools(self.tools)

        self.system_prompt = self._init_system_prompt(SYSTEM_PROMPT)
        self.history = [{"role": "system", "content": self.system_prompt}]

        # Ensure OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("Set OPENAI_API_KEY as environment variable.")

    def _init_system_prompt(self, template_str: str):
        return Template(template_str, undefined=StrictUndefined).render(
            tools=self.tools, authorized_imports=self.authorized_imports
        )

    def _extract_code(self, text: str) -> str | None:
        pattern = r"```py([\s\S]*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "print()"

    def run(self, task: str) -> str:
        self.history.append({"role": "user", "content": f"Task: {task}"})
        for step_num in range(self.max_steps):
            logger.info(f"Step {step_num}")
            is_final, obs, output = self.step()
            self.history.append(obs)
            if is_final:
                return output
        return "Max steps exceeded."

    def step(self):
        response = client.chat.completions.create(
            model=self.model,
            messages=self.history
        )
        content = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": content})
        logger.info(f"Thought:{content}")

        code = self._extract_code(content)
        logger.info(f"Code extracted:\n{code}")

        try:
            result = self.python_executor(code)
        except InterpreterError as e:
            logger.error(f"Interpreter error: {e}")
            return False, {"role": "assistant", "content": f"Error: {str(e)}"}, ""

        output = result.output
        logs = result.logs
        is_final = result.is_final_answer or "final_answer" in code
        logger.info(f"Tool executed. is_final: {is_final}, output: {output}")

        obs = {"role": "user", "content": f"Observation:{logs}"}
        return is_final, obs, output
