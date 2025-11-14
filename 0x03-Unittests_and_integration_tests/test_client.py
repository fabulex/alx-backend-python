#!/usr/bin/env python3
"""A unittest for GithubOrgClient"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient class"""

    @parameterized.expand([
        "google",
        "abc",
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json) -> None:
        """Tests org method of GithubOrgClient
            - Mocks get_json to return a specific payload
            - Asserts that get_json is called with the expected URL
            - Asserts that the org method returns the expected payload
        """
        # Set the mock to return a specific value
        mock_get_json.return_value = {"org": org_name}

        # Create an instance of GithubOrgClient
        client = GithubOrgClient(org_name)

        # Call the org property (because of @memoize, it's a property)
        result = client.org

        # Assert that get_json was called with the correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}")

        # Assert that the result is as expected
        self.assertEqual(result, {"org": org_name})

    def test_public_repos_url(self) -> None:
        """Tests _public_repos_url property of GithubOrgClient
            - Mocks the org property to return a specific payload
            - Asserts that _public_repos_url returns the expected URL
        """
        # memoize makes org a property, so we patch it as a PropertyMock
        with patch("client.GithubOrgClient.org",
                   new_callable=PropertyMock) as mock_org:
            # Set the mock to return a specific value
            mock_org.return_value = {
                "repos_url": "https://api.github.com/orgs/google/repos"
            }

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("google")

            # Access the _public_repos_url property
            result = client._public_repos_url

            # Assert that the result is as expected
            self.assertEqual(result,
                             "https://api.github.com/orgs/google/repos")

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json) -> None:
        """Tests public_repos method of GithubOrgClient
            - Mocks the get_json function to return a specific payload
            - Mocks the repos_payload property to return a specific payload
            - Asserts that public_repos returns the expected list of repo names

            public_repos() calls repos_payload, which calls get_json with
            _public_repos_url. That's why we mock everything
        """
        # Mock get_json (used by repos_payload) to avoid making a real API call
        mock_get_json.return_value = TEST_PAYLOAD[0][1]

        # Mock _public_repos_url property because it is used in repos_payload
        with patch("client.GithubOrgClient._public_repos_url",
                   new_callable=PropertyMock) as mock_publc_repos_url:
            # Set the mock to return a specific repos_url
            # "https://api.github.com/orgs/google/repos"
            mock_publc_repos_url.return_value = TEST_PAYLOAD[0][0]["repos_url"]

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("google")

            # Call the public_repos method
            # It should use the result of the mocked get_json
            # and return the list of repo names
            result = client.public_repos()

            # Assert that the result is as expected
            self.assertEqual(result, TEST_PAYLOAD[0][2])

            mock_publc_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                TEST_PAYLOAD[0][0]["repos_url"])

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Tests has_license static method of GithubOrgClient"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for public_repos method of GithubOrgClient"""

    @classmethod
    def setUpClass(self):
        """Set up for the integration tests"""

        def side_effect(url):
            """Side effect function for mocking requests.get from utils.py
                Returns a Mock object with a .json() method that returns
                the appropriate payload based on the URL
            """
            # Matches ORG_URL so we can mock GithubOrgClient.org property
            base_url = self.org_payload["repos_url"].replace("/repos", "")

            mock_resp = Mock()

            # Hanldes requests made by GithubOrgClient.org
            # to ORG_URL: https://api.github.com/orgs/{org}
            if url == base_url:
                mock_resp.json.return_value = self.org_payload
                return mock_resp
            # Handles requests made by GithubOrgClient.repos_payload
            # to _public_repos_url: https://api.github.com/orgs/{org}/repos
            elif url == self.org_payload["repos_url"]:
                mock_resp.json.return_value = self.repos_payload
                return mock_resp

            raise ValueError(f"Wrong URL called: {url}")

        # Patch requests.get for all tests in this class
        self.get_patcher = patch("requests.get")
        mock_get = self.get_patcher.start()
        mock_get.side_effect = side_effect

    def test_public_repos(self):
        """Tests public_repos method of GithubOrgClient"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Tests public_repos method of GithubOrgClient with a license key"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )

    @classmethod
    def tearDownClass(self):
        """Tear down for the integration tests"""
        self.get_patcher.stop()


if __name__ == "__main__":
    unittest.main()
