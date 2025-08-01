from typing import List

from cyjax.resources.resource import Resource
from .dto import TierDto


class Tier(Resource):

    def list(self) -> List[TierDto]:
        """
        Lists all supplier tiers for your group.

        :return: The list of tiers.
        :rtype List[TierDto]:
        """
        return self._get_list(endpoint='/third-party-risk/tier', dto=TierDto)
