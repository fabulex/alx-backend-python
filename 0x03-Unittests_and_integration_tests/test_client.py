#!/usr/bin/env python3
"""Integration tests for GithubOrgClient class"""

import unittest
from parameterized import parameterized_class
from unittest.mock import Mock, patch
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


@parameterized_class(
    ["org_payload", "repos_payload", "expected_repos", "apache2_repos"],
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Set up patch for requests.get with dynamic side_effect."""
        def side_effect(url, *args, **kwargs):
            """Return a Mock response based on URL matching."""
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
        """Stop the patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected list of repos."""
        client = GithubOrgClient(self.org_payload["repos_url"].split("/")[-1])
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter returns expected list."""
        client = GithubOrgClient(self.org_payload["repos_url"].split("/")[-1])
        result = client.public_repos("apache-2.0")
        self.assertEqual(result, self.apache2_repos)
