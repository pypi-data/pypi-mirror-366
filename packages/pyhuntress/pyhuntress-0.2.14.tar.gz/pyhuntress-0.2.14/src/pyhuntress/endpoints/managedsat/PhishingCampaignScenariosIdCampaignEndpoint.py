from pyhuntress.endpoints.base.huntress_endpoint import HuntressEndpoint
from pyhuntress.interfaces import (
    IGettable,
)
from pyhuntress.models.managedsat import SATPhishingCampaigns
from pyhuntress.types import (
    JSON,
    HuntressSATRequestParams,
)


class PhishingCampaignScenariosIdCampaignEndpoint(
    HuntressEndpoint,
    IGettable[SATPhishingCampaigns, HuntressSATRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        HuntressEndpoint.__init__(self, client, "campaign", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, SATPhishingCampaigns)

    def get(
        self,
        data: JSON | None = None,
        params: HuntressSATRequestParams | None = None,
    ) -> SATPhishingCampaigns:
        
        """
        Performs a GET request against the /phishing-campaign-scenarios/{id}/campaign endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            SATPhishingCampaigns: The parsed response data.
        """
        return self._parse_one(
            SATPhishingCampaigns,
            super()._make_request("GET", data=data, params=params).json().get('data', {}),
        )
