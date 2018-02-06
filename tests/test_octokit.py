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
