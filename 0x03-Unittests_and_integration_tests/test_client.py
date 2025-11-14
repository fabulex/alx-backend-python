#!/usr/bin/env python3
"""Unit tests for client module"""

import unittest
from parameterized import parameterized
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient class"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Tests GithubOrgClient.org returns mocked payload and calls get_json once."""
        test_payload = {"repos_url": f"https://api.github.com/orgs/{org_name}/repos"}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, test_payload)
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )

    @parameterized.expand([
        ({"repos_url": "http://repos1"}, "http://repos1"),
        ({"repos_url": "http://repos2"}, "http://repos2"),
    ])
    def test_public_repos_url(self, payload, expected):
        """Tests GithubOrgClient._public_repos_url returns expected repos_url."""
        with patch.object(
            GithubOrgClient, 'org', new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient('test')
            self.assertEqual(client._public_repos_url, expected)


if __name__ == '__main__':
    unittest.main()
