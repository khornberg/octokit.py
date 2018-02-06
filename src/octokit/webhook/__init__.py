import hashlib
import hmac
import json

from octokit import utils


def verify(headers, payload, secret, events=[]):
    event = headers.get('X-GitHub-Event')
    if event not in utils.get_json_data('events.json'):
        return False
    if event not in events and '*' not in events:
        return False
    return _compare(headers, payload, secret)


def _compare(headers, payload, secret):
    encoding = 'utf-8'
    algo, sig = headers.get('X-Hub-Signature').split('=')
    digest = hmac.new(secret.encode(encoding), json.dumps(payload).encode(encoding), getattr(hashlib, algo)).hexdigest()
    return hmac.compare_digest(sig.encode(encoding), digest.encode(encoding))
