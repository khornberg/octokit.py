import pytest


class MockHeaders(object):

    def __init__(self, requested_page, **kwargs):
        link = 'Links <https://api.github.com/installation/repositories?page={}another=%2Cwith+a+space>; rel="next", <https://api.github.com/installation/repositories?page=4>; rel="last"'.format(  # noqa E501
            min(requested_page + 1, 4)
        )
        self.headers = {'Link': kwargs.get('link', link)}


class MockObject(object):

    def __init__(self, page, kwargs):
        self._response = MockHeaders(page, **kwargs)
        self.json = {'page': page, 'kwargs': kwargs}


def MockResponse(page=None, **kwargs):
    return MockObject(page, kwargs)


def MockResponseWithoutLinks(page=None, **kwargs):
    kwargs['link'] = ''
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

    def test_pagination_does_break_when_iterating_over_a_single_page(self):
        from octokit import Octokit
        sut_obj = MockResponseWithoutLinks
        p = Octokit().paginate(sut_obj, param='value')
        assert next(p) == {'page': 1, 'kwargs': {'param': 'value', 'link': ''}}
        with pytest.raises(StopIteration):
            assert next(p)

    def test_can_speficy_the_route_specifications_used(self):
        from octokit import Octokit
        octokit = Octokit(routes='ghe-2.18')
        assert '/enterprise/2.18' in octokit.issues.create.__doc__
        octokit = Octokit()
        assert '/developer.github.com' in octokit.issues.create.__doc__
        octokit = Octokit(routes='api.github.com')
        assert '/developer.github.com' in octokit.issues.create.__doc__

    def test_check_against_previous_version(self):
        # TODO keep this???
        from octokit import Octokit
        from previous import classes_and_methods
        octokit = Octokit(routes='api.github.com')
        for cls, methods in classes_and_methods.items():
            assert getattr(octokit, cls)
            for method in methods:
                thing = getattr(octokit, cls)
                try:
                    assert getattr(thing, method)
                except AttributeError:
                    print(cls, method)
        # assert False
        # new methods
        # (apps find_org_installation)
        # (apps find_organization_installation)
        # (apps find_repo_installation)
        # (apps find_repository_installation)
        # (apps find_user_installation)
        # (git get_a_reference)
        # (git get_all_references)
        # (git list_refs)
        # (licenses list)
        # (licenses list_all_licenses)
        # (migrations get_a_list_of_organization_migrations)
        # (migrations get_a_list_of_user_migrations)
        # (pulls create_a__pull__request_from_an__issue)
        # (pulls create_a_comment_reply)
        # (pulls create_comment_reply)
        # (pulls create_from_issue)
        # (repos create_a_file)
        # (repos create_file)
        # (repos get_commit_ref_sha)
        # (repos get_the__s_h_a_1_of_a_commit_reference)
        # (repos list_protected_branch_team_restrictions)
        # (repos list_protected_branch_user_restrictions)
        # (repos list_team_restrictions_of_protected_branch)
        # (repos list_user_restrictions_of_protected_branch)
        # (repos update_a_file)
        # (repos update_file)
        # (repos upload_a_release_asset)
        # (repos upload_release_asset)
        # (scim provision_invite_users)
        # (scim update_a_provisioned_organization_membership)
        # (scim update_provisioned_org_membership)
        # (search issues)
