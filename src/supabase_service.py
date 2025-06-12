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