import uuid
import requests
from .auth_util import gen_sign_headers

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from lightrag.exceptions import (
    APIConnectionError,
    RateLimitError,
    APITimeoutError,
)

# 请替换APP_ID、APP_KEY
APP_ID = '2025371607'
APP_KEY = 'jxDGEJyDHTHwVFyZ'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'

class VivoError(Exception):
    """莫名其妙的错误？？"""

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, APITimeoutError, VivoError)
    ),
)
async def sync_vivogpt(prompt, system_prompt=None, history_messages=[], **kwargs):
    print('Call VivoGPT')
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    URI = '/vivogpt/completions'
    params = {
        'requestId': str(uuid.uuid4())
    }

    data = {
        'messages': messages,
        'model': 'vivo-BlueLM-TB-Pro',
        'sessionId': str(uuid.uuid4()),
        'extra': {
            'temperature': 0.9,
            'max_new_tokens': 5000,
        },
    }
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
    headers['Content-Type'] = 'application/json'

    url = 'https://{}{}'.format(DOMAIN, URI)
    response = requests.post(url, json=data, headers=headers, params=params)

    if response.status_code == 200:
        res_obj = response.json()
        print(f'response:{res_obj}')
        if res_obj['code'] == 0 and res_obj.get('data'):
            content = res_obj['data']['content']
            print(f'final content:\n{content}')
            return content
    else:
        print(messages, URI, DOMAIN)
        print(response.status_code, response.content)
        raise VivoError()

async def embedding(texts):
    URI = '/embedding-model-api/predict/batch'
    params = {}
    post_data = {
        "model_name": "m3e-base",
        "sentences": texts
    }
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)

    url = 'https://{}{}'.format(DOMAIN, URI)
    response = requests.post(url, json=post_data, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(URI, DOMAIN, texts)
        print(response.status_code, response.text)
        exit()

if __name__ == '__main__':
    import asyncio
    #asyncio.run(sync_vivogpt('你好？'))
    #asyncio.run(embedding(['123456']))