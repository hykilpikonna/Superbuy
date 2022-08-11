"""
For https://api.superbuy.com/gateway/orderpkg/list/{userid}/1/{limit}
"""
from typing import List, Any


class GatewayOrderItem:
    ItemId: int
    ItemBarcode: str
    GoodsName: str
    GoodsLink: str
    Property: str
    UserRemark: str
    RealCount: int
    UnitPrice: float
    GoodsPic: str
    StatusId: int
    OrderedTime: int
    WarehouseId: int
    WarehouseName: str
    ItemType: int
    goodsCode: str
    sku: str
    rechargeType: int
    rebateStatus: int
    buyableServiceExtList: List[Any]
    openPackaging: int
    refund: int
    additionalAllPhotoList: List[Any]
    StatusName: str
    additionalServiceVideoUrl: None
    hasHdQcVideoService: int


class GatewayOrderOpList:
    Name: str
    Code: int
    Level: int


class GatewayOrder:
    OrderPkgType: int
    OrderPkgNo: str
    OrderPkgId: int
    StatusId: int
    StatusName: str
    ShopSource: str
    OpList: List[GatewayOrderOpList]
    Items: List[GatewayOrderItem]
    purchaserName: str
    purchaserAvatar: str
    orderState: str
    purchaserId: str
    spuCode: str
    currency: str
    orderStatus: int
    sourceIcon: str
    sourceType: int
    MallDeliveryName: str
    TotalPrice: float
    TotalFreight: int
    PayPrice: float
    paypalCheck: bool
    orderCanDelete: bool
    haveRebateGoods: bool
    orderAddService: List[Any]
    currencySymbol: str
    totalRefund: int
    consultationFlag: bool
