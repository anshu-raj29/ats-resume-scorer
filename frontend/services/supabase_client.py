import hashlib
import os
import logging
import re
from pathlib import Path
from typing import Any, Dict
import streamlit as st
from supabase import Client, create_client

logger = logging.getLogger('ats_resume_scorer')


try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / '.env')
except ImportError:
    pass


def _secret(key: str, section: str = 'supabase') -> str:
    """Read from env first, then fall back to st.secrets[section][key]."""
    val = os.getenv(key, '')
    if val:
        return val
    try:
        return st.secrets[section][key]
    except (KeyError, FileNotFoundError, AttributeError):
        return ''


SUPABASE_URL = _secret('SUPABASE_URL')
SUPABASE_ANON_KEY = _secret('SUPABASE_ANON_KEY')

_USERNAME_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{2,31}$')


def _missing_config() -> str | None:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return 'Supabase is not configured — set SUPABASE_URL and SUPABASE_ANON_KEY in .env or .streamlit/secrets.toml'
    return None


@st.cache_resource
def get_client() -> Client | None:
    """Cached singleton for Supabase authentication."""
    if _missing_config():
        return None
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def _normalize_username(username: str) -> str:
    normalized = username.strip().lower()
    if not _USERNAME_PATTERN.fullmatch(normalized):
        raise ValueError(
            'Username must be 3–32 characters and contain only letters, '
            'numbers, periods, underscores, or hyphens; it must start with '
            'a letter or number.'
        )
    return normalized


def _username_email(username: str) -> str:
    """Map a username to a non-deliverable address for Supabase password auth."""
    username_hash = hashlib.sha256(username.encode('utf-8')).hexdigest()[:48]
    return f'u{username_hash}@username-login.example.com'


def _session_dict(session, user, username: str) -> Dict[str, Any]:
    return {
        'access_token':  session.access_token,
        'refresh_token': session.refresh_token,
        'user_id':       user.id,
        'username':      username,
    }


def sign_in_with_password(username: str, password: str) -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {'error': err}
    try:
        normalized_username = _normalize_username(username)
    except ValueError as exc:
        return {'error': str(exc)}

    try:
        resp = get_client().auth.sign_in_with_password(
            {
                'email': _username_email(normalized_username),
                'password': password,
            }
        )
        if not resp.session or not resp.user:
            return {'error': 'Invalid username or password'}
        return _session_dict(resp.session, resp.user, normalized_username)
    except Exception as exc:
        logger.warning(f'sign_in_with_password failed: {exc}')
        return {'error': _humanize(exc)}


def sign_up_with_password(username: str, password: str) -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {'error': err}
    try:
        normalized_username = _normalize_username(username)
    except ValueError as exc:
        return {'error': str(exc)}
    if len(password) < 6:
        return {'error': 'Password must be at least 6 characters'}

    try:
        resp = get_client().auth.sign_up({
            'email': _username_email(normalized_username),
            'password': password,
            'options': {'data': {'username': normalized_username}},
        })
        if resp.session and resp.user:
            return _session_dict(resp.session, resp.user, normalized_username)
        if resp.user:
            return {
                'error': (
                    'Account created, but Supabase email confirmation is still '
                    'enabled. Disable it in Supabase Authentication settings '
                    'to use username-only accounts.'
                )
            }
        return {'error': 'Sign-up failed'}
    except Exception as exc:
        logger.warning(f'sign_up failed: {exc}')
        return {'error': _humanize(exc)}


def sign_out() -> None:
    if _missing_config():
        return
    try:
        get_client().auth.sign_out()
    except Exception as exc:
        logger.warning(f'sign_out failed: {exc}')


def _humanize(exc: Exception) -> str:
    msg = str(exc)
    if any(
        phrase in msg.lower()
        for phrase in (
            'name or service not known',
            'getaddrinfo failed',
            'temporary failure in name resolution',
        )
    ):
        return (
            'Could not connect to Supabase. Check SUPABASE_URL and your '
            'network connection.'
        )
    # supabase errors arrive as "<status>: {json blob}" — surface the human bit
    if 'invalid_grant' in msg.lower() or 'invalid login' in msg.lower():
        return 'Invalid username or password'
    if (
        'user already registered' in msg.lower()
        or 'already been registered' in msg.lower()
        or 'email address already exists' in msg.lower()
    ):
        return 'That username is already taken'
    if 'password should be at least' in msg.lower():
        return 'Password must be at least 6 characters'
    return msg
