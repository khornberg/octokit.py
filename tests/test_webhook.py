from octokit import webhook


class TestWebhook(object):

    def test_can_verify_webhook(self):
        headers = {
            'X-Hub-Signature': 'sha1=5d61605c3feea9799210ddcb71307d4ba264225f',
            'X-GitHub-Event': 'push',
            'X-GitHub-Delivery': '72d3162f-cc78-11e3-81ab-4c9367dc0958'
        }
        payload = {}
        secret = 'secret'
        events = ['push']
        assert webhook.verify(headers, payload, secret, events=events)

    def test_can_filter_webhook_events(self):
        headers = {
            'X-Hub-Signature': 'sha1=5d61605c3feea9799210ddcb71307d4ba264225f',
            'X-GitHub-Delivery': '72d3162f-cc78-11e3-81ab-4c9367dc0958'
        }
        payload = {}
        secret = 'secret'
        events = ['push']
        assert webhook.verify(headers, payload, secret, events=events) is False

    def test_must_specify_events_to_allow(self):
        headers = {
            'X-Hub-Signature': 'sha1=5d61605c3feea9799210ddcb71307d4ba264225f',
            'X-GitHub-Delivery': '72d3162f-cc78-11e3-81ab-4c9367dc0958'
        }
        payload = {}
        secret = 'secret'
        assert webhook.verify(headers, payload, secret) is False

    def test_can_specify_all_events(self):
        headers = {
            'X-Hub-Signature': 'sha1=5d61605c3feea9799210ddcb71307d4ba264225f',
            'X-GitHub-Event': 'push',
            'X-GitHub-Delivery': '72d3162f-cc78-11e3-81ab-4c9367dc0958'
        }
        payload = {}
        secret = 'secret'
        events = ['*']
        assert webhook.verify(headers, payload, secret, events=events)

    def test_only_known_events_are_valid(self):
        headers = {
            'X-Hub-Signature': 'sha1=5d61605c3feea9799210ddcb71307d4ba264225f',
            'X-GitHub-Event': 'pushy',
            'X-GitHub-Delivery': '72d3162f-cc78-11e3-81ab-4c9367dc0958'
        }
        payload = {}
        secret = 'secret'
        events = ['pushy']
        assert webhook.verify(headers, payload, secret, events=events) is False

    def test_delivery_guids_must_be_valid_guids(self):
        headers = {
            'X-Hub-Signature': 'sha1=5d61605c3feea9799210ddcb71307d4ba264225f',
            'X-GitHub-Event': 'push',
            'X-GitHub-Delivery': 'not-a-guid'
        }
        payload = {}
        secret = 'secret'
        events = ['push']
        assert webhook.verify(headers, payload, secret, events=events) is False

    def test_can_verify_user_agent(self):
        headers = {
            'X-Hub-Signature': 'sha1=5d61605c3feea9799210ddcb71307d4ba264225f',
            'X-GitHub-Event': 'push',
            'X-GitHub-Delivery': '72d3162f-cc78-11e3-81ab-4c9367dc0958',
            'User-Agent': 'GitHub-Hookshot/',
        }
        payload = {}
        secret = 'secret'
        events = ['push']
        assert webhook.verify(headers, payload, secret, events=events, verify_user_agent=True)

    def test_verifies_user_agent(self):
        headers = {
            'X-Hub-Signature': 'sha1=5d61605c3feea9799210ddcb71307d4ba264225f',
            'X-GitHub-Event': 'push',
            'X-GitHub-Delivery': '72d3162f-cc78-11e3-81ab-4c9367dc0958',
            'User-Agent': 'GitHub-Hooks',
        }
        payload = {}
        secret = 'secret'
        events = ['push']
        assert webhook.verify(headers, payload, secret, events=events, verify_user_agent=True) is False

    def test_verify_ping_event(self):
        headers = {
            'X-Hub-Signature': 'sha1=02ad50e35622a4cf597de5fb86f4d59520f5adda',
            'X-GitHub-Event': 'ping',
            'X-GitHub-Delivery': '72d3162f-cc78-11e3-81ab-4c9367dc0958',
            'User-Agent': 'GitHub-Hookshot/',
        }
        payload = {
            'hook': {
                'type': 'App',
                'id': 11,
                'active': True,
                'events': ['pull_request'],
                'app_id': 42,
            }
        }
        secret = 'secret'
        assert webhook.verify(headers, payload, secret, events=['*'], return_app_id=True) == 42

    def test_can_request_app_id_be_returned_on_non_ping_events(self):
        headers = {
            'X-Hub-Signature': 'sha1=5d61605c3feea9799210ddcb71307d4ba264225f',
            'X-GitHub-Event': 'push',
            'X-GitHub-Delivery': '72d3162f-cc78-11e3-81ab-4c9367dc0958',
            'User-Agent': 'GitHub-Hookshot/',
        }
        payload = {}
        secret = 'secret'
        assert webhook.verify(headers, payload, secret, events=['*'], return_app_id=True)
