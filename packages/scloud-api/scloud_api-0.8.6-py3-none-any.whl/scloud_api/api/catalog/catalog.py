import urllib.parse

from scloud_api.base import Client, ApiResponse


class Catalog(Client):
    def list_items(self, filters=None) -> ApiResponse:
        """
        Fetch catalog info for multiple products.

        Endpoint:
            GET /api/Catalog

        Query Parameters:
        -----------------
        - model.sKU (str, optional): List of product IDs (comma-separated or multiple query params).
        - model.displayShadows (int, optional): Shadow display filter.
            - 0 = Non_Shadow_Only
            - 1 = Shadow_Only
            - 2 = Shadow_Parent
            - 3 = Not_Shadow_or_Shadow_Parent
        - model.selectedKits (int, optional): Kit filter.
            - 0 = Not_a_Kit_Parent_or_Component
            - 1 = Kit_Parent
            - 2 = Kit_Component
            - 3 = Not_a_Kit_Parent
            - 4 = Not_a_Kit_Component
        - model.activeStatus (int, optional): Active status.
            - 0 = No
            - 1 = Yes
            - -1 = All
        - model.poID (list[int], optional): List of purchase order IDs.
        - model.companyID (list[int], optional): List of company IDs.
        - model.vendorID (list[int], optional): List of vendor IDs.
        - model.defaultVendorID (list[int], optional): List of default vendor IDs.
        - model.vendorSKU (list[str], optional): List of vendor SKUs.
        - model.brandIds (list[int], optional): List of brand IDs.
        - model.warehouse (list[int], optional): List of warehouse IDs.
        - model.uPC (str, optional): Universal Product Code.
        - model.physicalQtyFrom (int, optional): Minimum physical quantity.
        - model.physicalQtyTo (int, optional): Maximum physical quantity.
        - model.kitType (int, optional): Inventory kit type.
            - 0 = Independent
            - 1 = MainComponent
            - 2 = AllComponents
        - model.productGroupFilterType (int, optional): Product group filter operator.
            - 0 = NotInProductGroup
            - 1 = InProductGroup
            - -1 = All
        - model.productGroup (str, optional): Product Group ID.
        - model.lastAggregateFrom (str, optional): Start creation datetime (mm/dd/yyyy hh:mm).
        - model.lastAggregateTo (str, optional): End creation datetime (mm/dd/yyyy hh:mm).
        - model.lastUpdatedFrom (str, optional): Start update datetime (mm/dd/yyyy hh:mm).
        - model.lastUpdatedTo (str, optional): End update datetime (mm/dd/yyyy hh:mm).
        - model.keyword (str, optional): Keyword search term.
        - model.pageNumber (int, optional): Page number for pagination.
        - model.pageSize (int, optional): Page size for pagination.

        Returns:
        --------
        JSON object representing catalog data.
        """

        return self._request(path="/api/Catalog", method="GET", data=filters)