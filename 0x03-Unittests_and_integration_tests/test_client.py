#!/usr/bin/env python3
"""Test GithubOrgClient class"""
from typing import Dict
import unittest
from unittest.mock import Mock, PropertyMock, patch, MagicMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test that `GithubOrgClient` is working"""

    @parameterized.expand(
        [
            ("google", {"login": "google"}),
            ("abc", {"login": "abc"}),
        ]
    )
    @patch('client.get_json')
    def test_org(
        self, org: str, expected_result: Dict, mock_get_json: MagicMock
    ) -> None:
        """Test that `GithubOrgClient.org` returns the correct value"""
        mock_get_json.return_value = expected_result
        client = GithubOrgClient(org)
        result = client.org
        self.assertEqual(result, expected_result)
        expected_arg = "https://api.github.com/orgs/{}".format(org)
        mock_get_json.assert_called_once_with(expected_arg)

    def test_public_repos_url(self):
        """Mock `GithubOrgClient._public_repos_url` property"""
        with patch(
            'client.GithubOrgClient.org', new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {
                "login": "google",
                "id": 99999,
                "repos_url": "https://example.com/google_repos",
            }
            client = GithubOrgClient('google')
            self.assertEqual(
                client._public_repos_url, "https://example.com/google_repos"
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: MagicMock):
        """Test `GithubOrgClient.public_repos`"""
        mock_get_json.return_value = [{"name": "truth"}, {"name": "flutter"}]
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock,
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = (
                "https://example.com/google_repos"
            )
            client = GithubOrgClient('google')
            self.assertEqual(client.public_repos(), ["truth", "flutter"])

    @parameterized.expand(
        [
            ({"license": {"key": "my_license"}}, "my_license", True),
            ({"license": {"key": "other_license"}}, "my_license", False),
        ]
    )
    def test_has_license(
        self, repo: Dict[str, Dict], license_key: str, expected: bool
    ) -> None:
        """Test that `GithubOrgClient.has_license` returns
        whether a repo has license or not
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD,
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Perform integration testing on `GithubOrgClient`"""

    @classmethod
    def setUpClass(cls) -> None:
        """Setup this test fixture"""
        super().setUpClass()
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def get_side_effect(url):
            """side_effect to mock the return of get"""
            if url[22:] == '/orgs/google':
                return Mock(json=lambda: cls.org_payload)
            elif url[22:] == '/orgs/google/repos':
                return Mock(json=lambda: cls.repos_payload)

        cls.mock_get.side_effect = get_side_effect

    def test_public_repos(self):
        """Test `GithubOrgClient.public_repos`"""
        client = GithubOrgClient('google')
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test `GithubOrgClient.public_repos` with a license argument"""
        client = GithubOrgClient('google')
        self.assertEqual(client.public_repos('apache-2.0'), self.apache2_repos)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.get_patcher.stop()
        super().tearDownClass()
