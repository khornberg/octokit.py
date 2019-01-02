class MockHeaders(object):

    def __init__(self, requested_page):
        Link = 'Links <https://api.github.com/installation/repositories?page={}>; rel="next", <https://api.github.com/installation/repositories?page=4>; rel="last"'.format(  # noqa E501
            min(requested_page + 1, 4)
        )
        self.headers = {'Link': Link}


class MockObject(object):

    def __init__(self, page, kwargs):
        self._response = MockHeaders(page)
        self.json = {'page': page, 'kwargs': kwargs}
        # self.is_last_page = True if page == 4 else False
        # self.next_page = min(page + 1, 4) if page else 2


def MockResponse(page=None, **kwargs):
    print('mr', page, kwargs)
    return MockObject(page, kwargs)


class TestOctokit(object):

    def test_can_instantiate_class(self):
        import octokit
        assert isinstance(octokit.Octokit, object)
        octo = octokit.Octokit()
        assert isinstance(octo, object)

    def test_can_import_class(self):
        from octokit import Octokit
        assert isinstance(Octokit, object)
        octokit = Octokit()
        assert isinstance(octokit, object)

    def test_clients_are_lower_case(self):
        from octokit import Octokit
        assert all(client.islower() for client in Octokit.__dict__)

    def test_pagination(self):
        from octokit import Octokit
        sut_obj = MockResponse
        p = Octokit().paginate(sut_obj, param='value')
        assert next(p) == {'page': 1, 'kwargs': {'param': 'value'}}
        assert next(p) == {'page': 2, 'kwargs': {'param': 'value'}}
        assert next(p) == {'page': 3, 'kwargs': {'param': 'value'}}
        assert next(p) == {'page': 4, 'kwargs': {'param': 'value'}}

    def test_can_speficy_the_route_specifications_used(self):
        from octokit import Octokit
        octokit = Octokit(routes='ghe-2.15')
        assert '/enterprise/2.15' in octokit.issues.create.__doc__
        octokit = Octokit()
        assert '/developer.github.com' in octokit.issues.create.__doc__
        octokit = Octokit(routes='api.github.com')
        assert '/developer.github.com' in octokit.issues.create.__doc__
