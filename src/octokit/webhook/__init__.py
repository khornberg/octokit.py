import hashlib
import hmac
import json
from uuid import UUID

from octokit import utils


def verify(headers, payload, secret, events=[]):
    if invalid_guid(headers.get('X-GitHub-Delivery')):
        return False
    if invalid_event(headers.get('X-GitHub-Event'), events):
        return False
    return _compare(headers, payload, secret)


def _compare(headers, payload, secret):
    encoding = 'utf-8'
    algo, sig = headers.get('X-Hub-Signature').split('=')
    digest = hmac.new(secret.encode(encoding), json.dumps(payload).encode(encoding), getattr(hashlib, algo)).hexdigest()
    return hmac.compare_digest(sig.encode(encoding), digest.encode(encoding))


def invalid_guid(guid):
    try:
        return str(UUID(guid)) != guid
    except ValueError:
        return True


def invalid_event(event, events):
    if event not in utils.get_json_data('events.json'):
        return True
    if event not in events and '*' not in events:
        return True
