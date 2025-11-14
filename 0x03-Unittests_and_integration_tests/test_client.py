#!/usr/bin/env python3
"""Unit and integration tests for GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        "google",
        "abc",
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json) -> None:
        """Test org property returns expected payload"""
        mock_get_json.return_value = {"org": org_name}
        client = GithubOrgClient(org_name)
        result = client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, {"org": org_name})

    def test_public_repos_url(self) -> None:
        """Test _public_repos_url returns expected URL"""
        with patch("client.GithubOrgClient.org",
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {
                "repos_url": "https://api.github.com/orgs/google/repos"
            }
            client = GithubOrgClient("google")
            result = client._public_repos_url
            self.assertEqual(
                result, "https://api.github.com/orgs/google/repos"
            )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json) -> None:
        """Test public_repos returns expected list of repo names"""
        mock_get_json.return_value = TEST_PAYLOAD[0][1]
        with patch("client.GithubOrgClient._public_repos_url",
                   new_callable=PropertyMock) as mock_url:
            mock_url.return_value = TEST_PAYLOAD[0][0]["repos_url"]
            client = GithubOrgClient("google")
            result = client.public_repos()
            self.assertEqual(result, TEST_PAYLOAD[0][2])
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                TEST_PAYLOAD[0][0]["repos_url"]
            )

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license static method"""
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
    """Integration tests for public_repos method"""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get for integration tests"""
        def side_effect(url, *args, **kwargs):
            base_url = cls.org_payload["repos_url"].replace("/repos", "")
            if url == base_url:
                mock_resp = Mock()
                mock_resp.json.return_value = cls.org_payload
                return mock_resp
            elif url == cls.org_payload["repos_url"]:
                mock_resp = Mock()
                mock_resp.json.return_value = cls.repos_payload
                return mock_resp
            raise ValueError(f"Unexpected URL called: {url}")

        cls.get_patcher = patch("client.requests.get", side_effect=side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop requests.get patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected list of repos"""
        org_name = self.org_payload["repos_url"].split("/")[-2]
        client = GithubOrgClient(org_name)
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filtered by license returns expected repos"""
        org_name = self.org_payload["repos_url"].split("/")[-2]
        client = GithubOrgClient(org_name)
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
