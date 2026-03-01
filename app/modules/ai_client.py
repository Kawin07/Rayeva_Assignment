import anthropic
from config import Config
import time
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

class AIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.retry_count = int(getattr(Config, 'AI_RETRY_COUNT', 3))
        self.timeout_seconds = int(getattr(Config, 'AI_TIMEOUT_SECONDS', 15))

    def _invoke_with_timeout(self, payload):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.client.messages.create, **payload)
            return future.result(timeout=self.timeout_seconds)

    def call_claude(self, messages, system_prompt, temperature=0.7, max_tokens=2000):
        start_time = time.time()

        payload = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': max_tokens,
            'temperature': temperature,
            'system': system_prompt,
            'messages': messages,
        }

        last_error = 'AI request failed'
        for attempt in range(self.retry_count):
            try:
                response = self._invoke_with_timeout(payload)
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    'success': True,
                    'response': response.content[0].text,
                    'latency_ms': latency_ms,
                    'usage': {
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens
                    }
                }
            except FuturesTimeoutError:
                last_error = 'AI request timeout'
            except Exception:
                last_error = 'AI provider unavailable'

            if attempt < self.retry_count - 1:
                backoff = 2 ** attempt
                time.sleep(backoff)

        latency_ms = int((time.time() - start_time) * 1000)
        return {
            'success': False,
            'error': last_error,
            'latency_ms': latency_ms,
            'usage': {'input_tokens': 0, 'output_tokens': 0}
        }

    def _extract_json_candidates(self, response_text):
        candidates = []
        decoder = json.JSONDecoder()
        length = len(response_text)
        for index, char in enumerate(response_text):
            if char not in '{[':
                continue
            try:
                value, end_pos = decoder.raw_decode(response_text[index:])
                if end_pos > 0:
                    candidates.append(value)
            except Exception:
                continue
            if len(candidates) >= 5:
                break
        return candidates

    def parse_json_response(self, response_text):
        try:
            if isinstance(response_text, (dict, list)):
                return response_text
            parsed_direct = json.loads(response_text)
            return parsed_direct
        except Exception:
            candidates = self._extract_json_candidates(response_text)
            for candidate in candidates:
                if isinstance(candidate, dict):
                    return candidate
            return None
