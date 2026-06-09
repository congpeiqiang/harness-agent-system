"""
@File    :  __init__.py.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:04
@Desc    :  
"""
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.tools.auth import customer_login_submit, customer_login
from app.mcp_server.fecmall_mcp.tools.address import (
    get_customer_addresses,
    get_address_info,
    change_address_country,
    save_customer_address,
    remove_customer_address
)
from app.mcp_server.fecmall_mcp.tools.order import (
    init_customer_order,
    reorder_customer_order,
    view_customer_order
)
from app.mcp_server.fecmall_mcp.tools.product import search_products
from app.mcp_server.fecmall_mcp.tools.category import (
    get_category_products,
    get_category_info
)
from app.mcp_server.fecmall_mcp.tools.cart import (
    get_cart,
    update_cart_item,
    add_coupon,
    cancel_coupon
)
from app.mcp_server.fecmall_mcp.tools.onepage import (
    get_onepage_info,
    change_onepage_country,
    update_onepage_info
)
from app.mcp_server.fecmall_mcp.tools.payment import (
    paypal_express_start,
    paypal_express_review,
    paypal_express_submit,
    paypal_standard_start,
    paypal_standard_review,
    alipay_standard_start,
    alipay_standard_review,
    checkmoney_start,
    payment_success
)
from app.mcp_server.fecmall_mcp.tools.customer_register import (
    get_register_info,
    submit_register
)
from app.mcp_server.fecmall_mcp.tools.customer_password import (
    forgot_password_init,
    forgot_password_send_code,
    reset_password_init,
    reset_password_submit
)
from app.mcp_server.fecmall_mcp.tools.customer_account import (
    get_customer_info,
    get_account_edit,
    submit_account_edit
)
from app.mcp_server.fecmall_mcp.tools.customer_contacts import (
    get_contacts_info,
    submit_contacts
)
from app.mcp_server.fecmall_mcp.tools.customer_favorite import (
    get_favorite_list,
    remove_favorite
)
from app.mcp_server.fecmall_mcp.tools.customer_review import get_customer_reviews
from app.mcp_server.fecmall_mcp.tools.product_detail import (
    get_product_info,
    add_to_cart_from_product,
    add_to_favorite,
    get_product_reviews,
    add_product_review
)

__all__ = [
    'FecMallConfig',
    'FecMallClient',
    # Auth
    'customer_login_submit',
    'customer_login',
    # Address
    'get_customer_addresses',
    'get_address_info',
    'change_address_country',
    'save_customer_address',
    'remove_customer_address',
    # Order
    'init_customer_order',
    'reorder_customer_order',
    'view_customer_order',
    # Product
    'search_products',
    'get_product_info',
    'add_to_cart_from_product',
    'add_to_favorite',
    'get_product_reviews',
    'add_product_review',
    # Category
    'get_category_products',
    'get_category_info',
    # Cart
    'get_cart',
    'update_cart_item',
    'add_coupon',
    'cancel_coupon',
    # Onepage
    'get_onepage_info',
    'change_onepage_country',
    'update_onepage_info',
    # Payment
    'paypal_express_start',
    'paypal_express_review',
    'paypal_express_submit',
    'paypal_standard_start',
    'paypal_standard_review',
    'alipay_standard_start',
    'alipay_standard_review',
    'checkmoney_start',
    'payment_success',
    # Customer Register
    'get_register_info',
    'submit_register',
    # Customer Password
    'forgot_password_init',
    'forgot_password_send_code',
    'reset_password_init',
    'reset_password_submit',
    # Customer Account
    'get_customer_info',
    'get_account_edit',
    'submit_account_edit',
    # Customer Contacts
    'get_contacts_info',
    'submit_contacts',
    # Customer Favorite
    'get_favorite_list',
    'remove_favorite',
    # Customer Review
    'get_customer_reviews',
]
