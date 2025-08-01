#  CYjAX Limited
from unittest.mock import MagicMock

import responses

from cyjax.resources.third_party_risk import Tier, TierDto


class TestTier:

    def test_list_tiers_api_call(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = Tier(api_key='test')
        resource._api_client = api_client_mock

        resource.list()

        api_client_mock.send.assert_called_once_with(method='get', endpoint='third-party-risk/tier', params=None)

    @responses.activate
    def test_list_tiers_when_no_tiers(self):
        resource = Tier(api_key='test')

        responses.add(responses.GET, resource._api_client.get_api_url() + '/third-party-risk/tier',
                      json=[],
                      status=200)

        response = resource.list()

        assert isinstance(response, list) is True
        assert len(response) == 0

    @responses.activate
    def test_list_tiers(self):
        resource = Tier(api_key='test')

        responses.add(responses.GET, resource._api_client.get_api_url() + '/third-party-risk/tier',
                      json=[
                          {
                              'id': 1,
                              'name': 'Tier 1',
                              'description': 'High level suppliers',
                              'suppliers': 70
                          },
                          {
                              'id': 2,
                              'name': 'Tier 2',
                              'description': 'Medium level suppliers',
                              'suppliers': 70
                          },
                          {
                              'id': 3,
                              'name': 'Tier 3',
                              'description': 'Low level suppliers',
                              'suppliers': 0
                          },
                      ],
                      status=200)

        response = resource.list()

        assert isinstance(response, list) is True
        assert len(response) == 3

        assert isinstance(response[0], TierDto) is True
        assert isinstance(response[1], TierDto) is True
        assert isinstance(response[2], TierDto) is True

        assert 1 == response[0].id
        assert 2 == response[1].id
        assert 3 == response[2].id
