"""
Supabase client initialisation.

Usage:
    from techshop_proj.supabase_client import get_supabase_client, get_supabase_admin_client

- `get_supabase_client()`       uses the anon key — safe for authenticated user operations.
- `get_supabase_admin_client()` uses the service_role key — admin-level access, server-side ONLY.

IMPORTANT: Never pass the service_role key to the browser / frontend.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_anon_client = None
_admin_client = None


def get_supabase_client():
    """
    Return a Supabase client using the anon (publishable) key.
    Suitable for operations that respect Row Level Security policies.
    """
    global _anon_client
    if _anon_client is None:
        try:
            from supabase import create_client, Client  # noqa: F401
            _anon_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY,
            )
        except Exception as exc:
            logger.error("Failed to create Supabase anon client: %s", exc)
            raise
    return _anon_client


def get_supabase_admin_client():
    """
    Return a Supabase client using the service_role key.
    Bypasses RLS — use ONLY in trusted server-side code (e.g. admin views, webhooks).
    Never expose to the browser or include in API responses.
    """
    global _admin_client
    if _admin_client is None:
        try:
            from supabase import create_client, Client  # noqa: F401
            _admin_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY,
            )
        except Exception as exc:
            logger.error("Failed to create Supabase admin client: %s", exc)
            raise
    return _admin_client
