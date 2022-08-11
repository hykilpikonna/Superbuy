"""
For https://api.superbuy.com/gateway/orderpkg/list/{userid}/1/{limit}
"""
from typing import List, Any


class GatewayOrderItem:
    item_id: int
    item_barcode: str
    goods_name: str
    goods_link: str
    property: str
    user_remark: str
    real_count: int
    unit_price: float
    goods_pic: str
    status_id: int
    ordered_time: int
    warehouse_id: int
    warehouse_name: str
    item_type: int
    goods_code: str
    sku: str
    recharge_type: int
    rebate_status: int
    buyable_service_ext_list: List[Any]
    open_packaging: int
    refund: int
    additional_all_photo_list: List[Any]
    status_name: str
    additional_service_video_url: None
    has_hd_qc_video_service: int


class GatewayOrderOpList:
    name: str
    code: int
    level: int


class GatewayOrder:
    order_pkg_type: int
    order_pkg_no: str
    order_pkg_id: int
    status_id: int
    status_name: str
    shop_source: str
    op_list: List[GatewayOrderOpList]
    items: List[GatewayOrderItem]
    purchaser_name: str
    purchaser_avatar: str
    order_state: str
    purchaser_id: str
    spu_code: str
    currency: str
    order_status: int
    source_icon: str
    source_type: int
    mall_delivery_name: str
    total_price: float
    total_freight: int
    pay_price: float
    paypal_check: bool
    order_can_delete: bool
    have_rebate_goods: bool
    order_add_service: List[Any]
    currency_symbol: str
    total_refund: int
    consultation_flag: bool
