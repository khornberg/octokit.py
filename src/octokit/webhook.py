import hashlib
import hmac
import json
from uuid import UUID

from octokit import utils


def valid_signature(headers, payload, secret):
    encoding = 'utf-8'
    algo, sig = headers.get('X-Hub-Signature').split('=')
    digest = hmac.new(secret.encode(encoding), payload.encode(encoding), getattr(hashlib, algo)).hexdigest()
    return hmac.compare_digest(sig.encode(encoding), digest.encode(encoding))


def valid_guid(guid):
    try:
        return str(UUID(guid)) == guid
    except ValueError:
        return False


def valid_event(event, events):
    return event in utils.get_json_data('events.json') and (event in events or '*' in events)


def valid_user_agent(ua):
    return ua.startswith('GitHub-Hookshot/')


def valid_headers(headers, events, verify_user_agent):
    if not valid_guid(headers.get('X-GitHub-Delivery')):
        return False
    if not valid_event(headers.get('X-GitHub-Event'), events):
        return False
    if verify_user_agent and not valid_user_agent(headers.get('User-Agent', '')):
        return False
    return True


def verify(headers, payload, secret, events=[], verify_user_agent=False, return_app_id=False):
    if not valid_headers(headers, events, verify_user_agent):
        return False
    validity = valid_signature(headers, payload, secret)
    if validity and return_app_id and headers.get('X-GitHub-Event') == 'ping':
        return json.loads(payload).get('hook').get('app_id')
    return validity
