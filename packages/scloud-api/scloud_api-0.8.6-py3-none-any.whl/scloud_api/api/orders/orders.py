import urllib.parse

from scloud_api.base import Client, ApiResponse

class Orders(Client):
    def get_orders(self, filters=None, pageSize=10, pageNum=1) -> ApiResponse:
        """
        get_orders(self, filters=None) -> ApiResponse
        Fetch metadata for a list of sales orders.

        Endpoint:
            GET /api/Orders

        Query Parameters:
        -----------------
        - model.orderIDs (list[int], optional): List of order IDs.
        - model.companyID (list[int], optional): List of company IDs.
        - model.companyGroupID (list[int], optional): List of company group IDs.
        - model.orderStatus (list[int], optional): Status of the orders. Valid values:
            1 = ShoppingCart, 2 = InProcess, 3 = Completed, 100 = ProblemOrder,
            200 = OnHold, 300 = Quote, 999 = Void, -1 = Canceled
        - model.dateRange (int, optional): Predefined date filters:
            1 = Today, 2 = ThisWeek, 3 = LastWeek, 4 = Last31Days, 5 = Last60Days, 6 = Last120Days,
            7 = ThisCalendarYear, 8 = PreviousCalendarYear, 9 = AllDates, 10 = Last7Days, 11 = Last3Days,
            12 = Last24Hours, 17 = OlderThan1BusinessDay, 18 = OlderThan2BusinessDay, 19 = OlderThan3BusinessDay,
            20 = Yesterday, 21 = Last90Days, 22 = LastMonth, 23 = Last12Months, 24 = OlderThan24Hours,
            25 = Tomorrow, 26 = Next3Days, 27 = Next7Days, 28 = MonthToDate, 29 = OlderThan6Months,
            30 = OlderThan5Days, 31 = OlderThan30Days, 32 = This_Month, 33 = OlderThan7Days,
            34 = OlderThan14Days, 35 = Last21Days, 101 = Last14Days, 180 = Last180Days
        - model.shipDateRange (int, optional): Same values as model.dateRange.
        - model.updatedFromDateRange (int, optional): Same values as model.dateRange.
        - model.createdOnDateRange (int, optional): Same values as model.dateRange.
        - model.shippingStatus (int, optional): Shipping status:
            0 = Unknown, 1 = Unshipped, 2 = PartiallyShipped, 3 = FullyShipped, 4 = ReadyForPickup
        - model.trackingNumber (str, optional): Tracking number.
        - model.serialNumber (str, optional): Serial number.
        - model.paymentDateRange (int, optional): Same values as model.dateRange.
        - model.sKU (str, optional): Product SKU.
        - model.aSIN (str, optional): Amazon ASIN.
        - model.createdOnFrom / model.createdOnTo (str, optional): Creation datetime range (mm/dd/yyyy hh:mm).
        - model.lastUpdatedFrom / model.lastUpdatedTo (str, optional): Update datetime range.
        - model.channel (list[int], optional): List of channel IDs. Full list: 0–80 (e.g., 0 = Local_Store, 4 = Amazon, 17 = FBA, etc.).
        - model.orderSubType (int, optional): Subtype of order:
            0 = None, 1 = Sample, 2 = Charity, 3 = eBayNow, 4 = eBayLocalPickup, 5 = Same_Day_Delivery,
            6 = GS, 7 = Prime, 8 = FBA_Exchange, 9 = Amazon_Business, 10 = Amazon_Business_Prime,
            11 = Second_Day, 12 = Wish_Express, 13 = SBN, 15 = Amazon_Global_Express,
            16 = InStorePickUp, 17 = Fulfilled_By_TikTok
        - model.orderSourceOrderIDList (list[str], optional): List of external source order IDs.
        - model.qBExported / model.exported / model.hasParentOrder (int, optional): Status filters (0 = No, 1 = Yes, -1 = All).
        - model.paymentStatus (list[int], optional): Payment status:
            10 = NoPayment, 11 = NoPaymentOrPartialPayment, 20 = Authorized, 30 = Charged,
            40 = Uncleared, 50 = PartialRefund, 60 = FullRefund, 61 = PartialOrFullRefund,
            70 = PartiallyPaid, 71 = ChargedOrPartialRefund, 80 = EbayPaid, 81 = EbayPaidOrPartialPayment,
            99 = PaymentError, 711 = ChargedOrPartialPaid, 713 = ChargedOrAuthorized, -1 = ALL
        - model.dropShipStatus (int, optional): Dropship status:
            0 = None, 1 = Pending, 2 = Requested, 3 = Acknowledged,
            4 = Processed, 5 = PartialProcessed, 6 = Cancelled, 7 = Invalid
        - model.dropshipPoNumbers (list[int], optional): Dropship PO numbers.
        - model.warehouseID (list[int], optional): Warehouse IDs.
        - model.userID (list[int], optional): Customer/user IDs.
        - model.shipFromDate / model.shipToDate (str, optional): Shipping datetime range.
        - model.orderFromDate / model.orderToDate (str, optional): Order datetime range.
        - model.orderBy (int, optional): Sort field:
            0 = OrderID, 1 = OrderDate, 2 = OrderStatus, 3 = ShipDate, 4 = ShippingStatus
        - model.isAscending (bool, optional): Sort direction.
        - model.keyword (str, optional): Free text keyword search.
        - model.picklistID (str, optional): Picklist ID.
        - model.replacementOrder / model.isSettled (int, optional): Status flags (0 = No, 1 = Yes, -1 = All).
        - model.usersGroup (list[int], optional): Customer group IDs.
        - model.pageNumber / model.pageSize (int, optional): Pagination parameters.

        Returns:
        --------
        JSON object containing a list of sales order metadata.
        """
        filters['model.pageNumber'] = pageNum
        filters['model.pageSize'] = pageSize
        return self._request(path="/api/Orders", method="GET", data=filters)

    def set_exported(self, order_ids, exported=True) -> ApiResponse:
        data = {
            "Orders": order_ids,
            "Exported": exported,
        }
        return self._request(path="/api/Orders/SetExported", method="PUT", data=data)

    def set_custom_column(self, order_id, column_name, column_value) -> ApiResponse:
        data = {
            "ColumnName": column_name,
            "Value": column_value,
        }
        return self._request(f"/api/Orders/{order_id}/CustomColumns", "PUT", data=data)

    def set_custom_columns(self, order_id, columns) -> ApiResponse:
        return self._request(f"/api/Orders/{order_id}/CustomColumns/Multiple", "PUT", data=columns)