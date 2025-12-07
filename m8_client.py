import requests
import traceback
import json
from typing import Optional, Dict, Any

# Configuration
DEFAULT_HOST = "https://m8p.desktop.farm" 
DEFAULT_TIMEOUT = 60

class M8:
    """
    Wrapper for M8P Engine API interactions.
    """
    
    @staticmethod
    def _post_request(url: str, payload: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> Any:
        print("URL: ", url)
        headers = {'content-type': 'application/json'}
        tries = 3
        
        while tries > 0:
            tries -= 1
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
                # Attempt to parse JSON, fall back to text if response isn't JSON
                try:
                    R=resp.json()
                    print("Return: ", R)
                except json.JSONDecodeError:
                    return resp.text
                    
            except requests.exceptions.ConnectionError:
                print(f"Warning: Connection Error to {url}. Retrying...")
            except requests.exceptions.ConnectTimeout:
                print(f"Warning: Connection Timeout to {url}. Retrying...")
            except Exception:
                return {
                    'Status': "FAILED",
                    'Msg': traceback.format_exc()
                }
        
        return {'Status': "FAILED", 'Msg': "Max retries exceeded"}

    @staticmethod
    def LLM_Call(url: str, req_obj: Dict[str, Any], timeout: int = 60):
        """
        Direct LLM inference call bypassing script engine (if supported by endpoint).
        """
        return M8._post_request(url, req_obj, timeout)

    @staticmethod
    def RunScript(code: str, timeout: int = 7, retry: int = 3, check: bool = False, host: str = None):
        """
        Executes a script in a dry-run / ephemeral context.
        """
        base_host = host or DEFAULT_HOST
        url = f"{base_host}/api/v1/m8/dry-run"
        return M8._post_request(url, {'code': code}, timeout)

    @staticmethod
    def EnsureExists(session_id: str, code: str = "", timeout: int = 7, retry: int = 3, check: bool = False, host: str = None):
        """
        Checks if a session exists, creates/runs init code if necessary.
        """
        base_host = host or DEFAULT_HOST
        url = f"{base_host}/api/v1/m8/session-check/{session_id}"
        return M8._post_request(url, {'code': code}, timeout)

    @staticmethod
    def RunSession(session_id: str, code: str, timeout: int = 7, retry: int = 3, check: bool = False, host: str = None):
        """
        Executes M8 code within a specific persistent session context.
        """
        base_host = host or DEFAULT_HOST
        url = f"{base_host}/api/v1/m8/session-run/{session_id}"
        return M8._post_request(url, {'code': code}, timeout)

    @staticmethod
    def DestroySession(session_id: str, host: str = None):
        """
        Frees memory associated with the session.
        """
        base_host = host or DEFAULT_HOST
        url = f"{base_host}/api/v1/m8/session-destroy/{session_id}"
        return M8._post_request(url, {'code': ""}, timeout=10)