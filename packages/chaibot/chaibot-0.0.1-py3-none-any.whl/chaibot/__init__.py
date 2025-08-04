# chaibot/__init__.py

class Chaibot:
    def __init__(self, use_local: bool = False, local_model_path: str = None):
        """
        :param use_local: if True, routes queries to local_llm.py
        :param local_model_path: path to your GGML model file (for local LLM)
        """
        self.use_local = use_local
        if use_local:
            from .local_llm import LocalLLM
            if not local_model_path:
                raise ValueError("You must provide local_model_path when use_local=True")
            self.backend = LocalLLM(model_path=local_model_path)
        else:
            from .copilot_api import CopilotAPI
            self.backend = CopilotAPI()

    def chat(self, message: str) -> str:
        """Send a user message and return the model’s reply."""
        return self.backend.respond(message)
