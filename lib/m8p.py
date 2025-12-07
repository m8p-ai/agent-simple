import requests
import traceback
import json

DEFAULT_HOST = "http://10.4.20.191:9500" 
# DEFAULT_HOST = "http://10.4.20.193:9500"
# api/v1/m8/session-run/MY_SESSION_546
# api/v1/m8/session-stats/MY_SESSION_546
# api/v1/m8/session-create/MY_SESSION_546
# api/v1/m8/session-check/MY_SESSION_546
# api/v1/m8/session-activity
# api/v1/m8/dry-run

# default_req = {
#     "stream": True,
#     "stop":[],
#     "repeat_last_n":256,
#     "repeat_penalty":1.18,
#     "top_k":40,
#     "top_p":0.95,
#     "min_p":0.05,
#     "tfs_z":1,
#     "typical_p":1,
#     "presence_penalty":0,
#     "frequency_penalty":0,
#     "mirostat":0,
#     "mirostat_tau":5,
#     "mirostat_eta":0.1,
#     "grammar":"",
#     "n_probs":0,
#     "min_keep":0,
#     "image_data":[],
#     "n_predict": 120,
#     "temperature":0.1,
#     "cache_prompt": True,
#     "api_key": "",
#     "prompt": ""
# }

MAX_TOKENS_OUT = 5000
AMODEL=''
DEFAULT_TOKENS_OUT = 63

def Exec_LLM_Call(url, reqObj, xheaders=None, timeout=60):
    if xheaders is None:
        xheaders = {
            'content-type' : 'application/json',
        }

    Tries = 3
    while Tries > 0:
        Tries -= 1
        try:
            resp = requests.post(url, json.dumps(reqObj), headers=xheaders, timeout=timeout)
            Resp = json.loads(resp.text)

            return {
                'Status' : 'OK',
                'R' : Resp
            }
        except requests.exceptions.ConnectionError as timeout:
            print("HAS TIMEOUT ON CONNECTION: ")

        except requests.exceptions.ConnectTimeout as timeout:
            print("HAS TIMEOUT TRY AGAIN: ")

        except Exception as e:
            tb = traceback.format_exc()
            return {
                'Status' : "FAILED",
                "Msg" : tb
            }

def ExecM8Script(code, api=None, timeout=7, retry=3, check=False, host=None):
    if host is None:
        host = DEFAULT_HOST
    url = host + '/api/v1/m8/dry-run'
    if api:
        # url = DEFAULT_HOST + "/api/v1/m8/" + api_name + "/" + session_id
        url = DEFAULT_HOST + api

    xheaders = {
        'content-type' : 'application/json',
        # 'Authorization': f"Bearer {api_key}"
    }

    reqObj = {
        'code' : code
    }

    Resp = requests.post(url, json.dumps(reqObj), headers=xheaders, timeout=timeout)
    output_buf = Resp.text
    ## TODO: Catch connection and retry if params passed
    try:
        response_dict = json.loads(output_buf)
        # if response_dict.get('Ret'):
        #     RX = json.loads(response_dict['Ret'])
        return response_dict
    except Exception:
        return output_buf

class M8(object):
    @staticmethod
    def LLM_Call(*args, **kwargs):
        return Exec_LLM_Call(*args, **kwargs)

    @staticmethod
    def RunScript(code, timeout=7, retry=3, check=False, host=None):
        return ExecM8Script(code, timeout=timeout, retry=retry, check=check, host=host)

    @staticmethod
    def EnsureExists(sessionId, code="", timeout=7, retry=3, check=False, host=None):
        return ExecM8Script(code, 
            api=f'/api/v1/m8/session-check/{sessionId}', 
            timeout=timeout, 
            retry=retry, 
            check=check,
            host=host)

    @staticmethod
    def RunSession(sessionId, code, timeout=7, retry=3, check=False, host=None):
        return ExecM8Script(code, 
            timeout=timeout, retry=retry, check=check,
            api=f'/api/v1/m8/session-run/{sessionId}', 
            host=host)

    @staticmethod
    def DestroySession(sessionId, host=None):
        return ExecM8Script("", 
            timeout=10, retry=3, check=False,
            api=f'/api/v1/m8/session-destroy/{sessionId}', 
            host=host)


return M8




