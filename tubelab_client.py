"""Own TubeLab API client. Never resubmit the original request while polling."""
import argparse
import json
import os
import re
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, HTTPRedirectHandler, build_opener


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirect rejected; set the intended API base explicitly')


def get_result(base, api_key, route, max_wait=600):
    parsed = urlparse(base)
    if not parsed.hostname or parsed.scheme not in ('https', 'http'):
        raise ValueError('Use the configured own API hostname')
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
        raise ValueError('Unexpected API base URL')
    if parsed.scheme != 'https' and parsed.hostname not in ('localhost', '127.0.0.1'):
        raise ValueError('Remote API requires HTTPS')
    deadline = time.monotonic() + max_wait
    while True:
        request = Request(base.rstrip('/') + route, headers={
            'Authorization': 'Api-Key ' + api_key,
            'Prefer': 'respond-async',
        })
        with build_opener(_NoRedirect()).open(request, timeout=90) as response:
            result = json.load(response)
            if response.status != 202:
                return result
            route = result.get('resultUrl', '')
            if not re.fullmatch(r'/v1/jobs/[a-fA-F0-9-]{36}/result', route):
                raise ValueError('Unexpected job result path')
            delay = min(30, max(1, int(response.headers.get('Retry-After', '2'))))
        if time.monotonic() + delay > deadline:
            raise TimeoutError('Polling budget exceeded; job remains available at ' + route)
        time.sleep(delay)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='http://127.0.0.1:8086')
    parser.add_argument('--query', required=True)
    parser.add_argument('--language', default='en')
    parser.add_argument('--size', type=int, default=3)
    args = parser.parse_args()
    key = os.environ.get('TUBELAB_API_KEY')
    if not key:
        parser.error('Set TUBELAB_API_KEY to your own service key')
    route = '/v1/search/outliers?' + urlencode({'query': args.query, 'language': args.language, 'size': args.size})
    print(json.dumps(get_result(args.base, key, route), ensure_ascii=False, indent=2))
