from pyhuntress.endpoints.base.huntress_endpoint import HuntressEndpoint
from pyhuntress.endpoints.siem.ReportsIdEndpoint import ReportsIdEndpoint
from pyhuntress.interfaces import (
    IGettable,
    IPaginateable,
)
from pyhuntress.models.siem import SIEMReports
from pyhuntress.responses.paginated_response import PaginatedResponse
from pyhuntress.types import (
    JSON,
    HuntressSIEMRequestParams,
)


class ReportsEndpoint(
    HuntressEndpoint,
    IGettable[SIEMReports, HuntressSIEMRequestParams],
    IPaginateable[SIEMReports, HuntressSIEMRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        HuntressEndpoint.__init__(self, client, "reports", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, SIEMReports)
        IPaginateable.__init__(self, SIEMReports)

    def id(self, id: int) -> ReportsIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized ReportsIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            ReportsIdEndpoint: The initialized ReportsIdEndpoint object.
        """
        child = ReportsIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child

    def paginated(
        self,
        page: int,
        limit: int,
        params: HuntressSIEMRequestParams | None = None,
    ) -> PaginatedResponse[SIEMReports]:
        """
        Performs a GET request against the /reports endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            limit (int): The number of results to return per page.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[SIEMReports]: The initialized PaginatedResponse object.
        """
        if params:
            params["page"] = page
            params["limit"] = limit
        else:
            params = {"page": page, "limit": limit}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            SIEMReports,
            self,
            "reports",
            page,
            limit,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: HuntressSIEMRequestParams | None = None,
    ) -> SIEMReports:
        """
        Performs a GET request against the /reports endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            SIEMAuthInformation: The parsed response data.
        """
        return self._parse_many(
            SIEMReports,
            super()._make_request("GET", data=data, params=params).json().get('reports', {}),
        )
