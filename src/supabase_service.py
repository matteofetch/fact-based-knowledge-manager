import os
from typing import Optional

try:
    from supabase import create_client, Client
except ImportError:
    # If supabase-py is not installed yet, downstream code will fall back automatically
    create_client = None  # type: ignore
    Client = None  # type: ignore


class SupabaseService:
    """Lightweight wrapper around Supabase client for read-only operations."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.client: Optional["Client"] = None

        if self.supabase_url and self.supabase_key and create_client:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
            except Exception:
                # Fail silently – will fall back to hard-coded data
                self.client = None

    def fetch_guidelines(self) -> Optional[str]:
        """Fetch the knowledge-management guidelines from the `guidelines` table.

        Returns None on any failure so the caller can fall back to the local copy.
        """
        if not self.client:
            return None
        try:
            res = (
                self.client.table("guidelines")
                .select("content")
                .eq("id", 1)
                .single()
                .execute()
            )
            return res.data.get("content") if res and res.data else None
        except Exception:
            return None

    # ---------------------------------------------------------------------
    # Knowledge Base
    # ---------------------------------------------------------------------

    def fetch_knowledge_base(self):
        """Return a KnowledgeBase object built from the `facts` table, or None."""
        if not self.client:
            return None
        try:
            from src.models import Fact, KnowledgeBase  # local import to avoid circular

            res = (
                self.client.table("facts")
                .select("number, description, last_validated")
                .order("number")
                .execute()
            )

            if not res or not res.data:
                return None

            facts = [
                Fact(
                    number=row["number"],
                    description=row["description"],
                    last_validated=row["last_validated"],
                )
                for row in res.data
            ]

            return KnowledgeBase(title="Current RN Project Facts", facts=facts)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def upsert_knowledge_base(self, kb):
        """Upsert all facts from a KnowledgeBase into the `facts` table.

        Requires a key with write permissions (service role or anon with RLS off).
        Returns True on success, False on failure.
        """
        if not self.client or not kb:
            return False
        try:
            rows = [
                {
                    "number": fact.number,
                    "description": fact.description,
                    "last_validated": fact.last_validated,
                }
                for fact in kb.facts
            ]

            # Perform upsert (on conflict number)
            self.client.table("facts").upsert(rows).execute()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    def fetch_tasks(self):
        """Fetch all tasks from the `tasks` table.
        
        Returns a list of task strings, or empty list on failure.
        """
        if not self.client:
            return []
        try:
            res = (
                self.client.table("tasks")
                .select("task")
                .order("created_date", desc=True)
                .execute()
            )
            
            if not res or not res.data:
                return []
                
            return [row["task"] for row in res.data]
        except Exception:
            return []

    def add_task(self, task_description: str) -> bool:
        """Add a new task to the `tasks` table.
        
        Returns True on success, False on failure.
        """
        if not self.client or not task_description:
            return False
        try:
            self.client.table("tasks").insert({
                "task": task_description
            }).execute()
            return True
        except Exception:
            return False 