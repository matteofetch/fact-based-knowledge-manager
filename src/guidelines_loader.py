import os

class GuidelinesLoader:
    def __init__(self):
        self.source = os.getenv("GUIDELINES_SOURCE", "local")
        self.local_path = os.getenv("GUIDELINES_LOCAL_PATH", "guidelines-local.md")
        # Placeholder for future Google Docs integration
        self.google_doc_id = os.getenv("KNOWLEDGE_GUIDELINES_DOC_ID")

    def load(self) -> str:
        if self.source == "local":
            return self._load_local()
        elif self.source == "google_docs":
            # Placeholder for Google Docs integration
            return "[Google Docs integration not yet implemented]"
        else:
            raise ValueError(f"Unknown guidelines source: {self.source}")

    def _load_local(self) -> str:
        try:
            with open(self.local_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"[Error loading local guidelines: {str(e)}]" 