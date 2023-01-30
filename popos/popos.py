from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import SimpleNamespace
from enum import Enum
from typing import Optional, List, Any, Union

from requests import Response


class SuperbuyResponse:
    state: int
    serverTime: int
    msg: str
    data: Any


class PaginatedResponse:
    Code: int
    CurrentPage: int
    Limit: int
    TotalCount: int
    TotalPage: int
    List: list[Any]


class LoginData:
    """
    For mobile login https://api.superbuy.com/auth/login
    """
    userId: int
    loginToken: str
    accessToken: str
    expireIn: int
    language: str
    userName: str
    nikeName: str
    currencyCode: str


class TaobaoStore:
    name: str
    url: str


class TaobaoItem:
    name: str
    url: str
    promises: list[str]
    price: str
    qty: str
    origPrice: str | None = None
    sel: list[tuple[str, str]] | None = None


class TaobaoAddress:
    place: str
    time: str


class TaobaoDelivery:
    expressName: str
    address: list[TaobaoAddress]
    isSuccess: str
    expressId: str


class TaobaoOrder:
    id: str
    date: str
    store: TaobaoStore
    items: list[TaobaoItem]
    priceTotal: str
    priceDelivery: str
    status: str
    delivery: TaobaoDelivery


class SuperbuyDeliveryCompany:
    id: int
    reg_mail_no: str
    name: str


@dataclass
class CreateOrder:
    diybuyUserRemark: str
    shopId: str
    shopName: str
    goodsList: list[CreateGood]
    goodsPrefix: str = 'TB'
    guaranteeFlag: int = 0


@dataclass
class CreateGood:
    desc: str
    goodsId: str
    inventory: int
    name: str
    num: int
    shopName: str
    shopUrl: str
    skus: str
    totalPrice: float
    url: str
    riskinfor: list = field(default_factory=list)
    prifex: str = "TB"
    protips: str = ''
    remark: str = '自助购物'
    thumb: str = 'https://a-z-animals.com/media/2021/11/sunny-cat-picture-id508030340-1024x535.jpg'
    warehouseId: int = 1
    takeOutInvoice: int = 1
    openPackaging: int = 1
    needCheck: int = 1
    checkedContraband: int = 1
    samplingInspection: int = 0


class Currency(Enum):
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    CNY = "CNY"


class TipList(Enum):
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    TIP_1 = "1. 您提交的商品存在邮寄限制，有一定安检退包、延误的风险和较小的海关查扣风险，您需要自行判断并承担相应结果。"
    TIP_2 = "2. Superbuy会按照用户要求寄出包裹，对用户寄送邮寄限制商品无法承担任何责任，请您谅解。"
    TIP_3 = "由于您的商品属于易折损品，在国际寄送过程中容易对商品造成损坏，建议您在提交包裹时购买包裹加固服务，减少破碎风险。"


class Tips:
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    title: str
    tip_list: List[TipList]


class GoodsPrifex(Enum):
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    EMPTY = ""
    TB = "TB"
    TMALL = "TMALL"


class AppListItem:
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    item_id: int
    item_barcode: str
    goods_code: str
    goods_name: str
    goods_link: str
    order_id: int
    order_no: str
    count: int
    real_count: int
    unit_price: float
    discount: int
    weight: int
    item_remark: str
    item_status: int
    inspector_id: int
    inspector_name: str
    item_type: int
    split_item_id: int
    split_type: int
    delivery_special: int
    goods_pic: str
    sku_name: str
    second_item_status: int
    un_delivery_list: List[int]
    un_insurance: str
    arrival_pic_list: List[str]
    return_apply_status: int
    volume: str
    volume_weight: str
    project_type: int
    goods_prifex: GoodsPrifex
    goods_cat_code: int
    goods_props: None
    merge_weight_list: None
    currency: Currency
    merge_weight: int
    zip_rate: int
    fake_brand: int
    warehouse_id: int
    order_state: None
    additional_service_pic_list: Optional[List[str]]
    has_hd_qc_photo_service: int
    check_contraband: int
    is_returned: int
    can_sub_pkg: bool
    origin_arrived_time: int
    storage_fee_countdown_str: Optional[str]
    storage_fee_accumulation_str: None
    overdue_countdown_str: Optional[str]
    storage_fee_expired_time: int
    storage_expired_time: int
    buyable_service_ext_list: List[BuyableServiceEXTList]
    shipping_experts: int
    experts_hint: None
    item_service_ext_list: None
    out_time_ten_day_status: int
    good_code: str
    good_id: str
    picture_url: str
    is_no_submit_order_for_service_status: int
    undelivery: str
    hd_qc_photo_list: List[str]
    is_additional_all: int
    additional_all_photo_list: List[Any]
    sensitive_product_tips: Union[List[Any], Tips]
    merge_show: bool
    expiration_time: int
    delay_flag: int
    fragile_risk_tips: Optional[Tips]


class OrderState(Enum):
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    CA = "CA"
    EMPTY = ""


class OrderList:
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    order_no: str
    order_type: int
    order_state: OrderState
    source_icon: str
    box_in_storage: int
    box_in_storage_checked: int
    can_apply_sale_after: int
    alone_pack: bool
    merge_weight: bool
    items: List[AppListItem]
    items_count: int
    delay_flag: int
    expiration_desc: str


class WarehouseList:
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    warehouse_id: int
    item_total: int
    name: str
    id: int
    item_count: int


class YearActivityInfo:
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    status: int
    banner_info: Any


class OrderListData:
    """
    For https://front.superbuy.com/package/parcel/app-list
    """
    order_list: List[OrderList]
    sale_after_list: List[Any]
    count: int
    usd_to_cny_rate: float
    is_measuring_distance: int
    total_row: int
    year_activity_info: YearActivityInfo
    warehouse_list: List[WarehouseList]


def jsn(s: str | Response):
    if isinstance(s, Response):
        s = s.text
    return json.loads(s, object_hook=lambda d: SimpleNamespace(**d))
