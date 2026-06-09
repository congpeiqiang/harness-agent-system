"""
@File    :  server.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:07
@Desc    :  
"""
from fastmcp import FastMCP
from typing import Dict, Any
import json
from app.mcp_server.fecmall_mcp import (
    FecMallConfig,
    FecMallClient,
    # Auth
    customer_login_submit,
    customer_login,
    # Address
    get_customer_addresses,
    get_address_info,
    change_address_country,
    save_customer_address,
    remove_customer_address,
    # Order
    init_customer_order,
    reorder_customer_order,
    view_customer_order,
    # Product
    search_products,
    get_product_info,
    add_to_cart_from_product,
    add_to_favorite,
    get_product_reviews,
    add_product_review,
    # Category
    get_category_products,
    get_category_info,
    # Cart
    get_cart,
    update_cart_item,
    add_coupon,
    cancel_coupon,
    # Onepage
    get_onepage_info,
    change_onepage_country,
    update_onepage_info,
    # Payment
    paypal_express_start,
    paypal_express_review,
    paypal_express_submit,
    paypal_standard_start,
    paypal_standard_review,
    alipay_standard_start,
    alipay_standard_review,
    checkmoney_start,
    payment_success,
    # Customer Register
    get_register_info,
    submit_register,
    # Customer Password
    forgot_password_init,
    forgot_password_send_code,
    reset_password_init,
    reset_password_submit,
    # Customer Account
    get_customer_info,
    get_account_edit,
    submit_account_edit,
    # Customer Contacts
    get_contacts_info,
    submit_contacts,
    # Customer Favorite
    get_favorite_list,
    remove_favorite,
    # Customer Review
    get_customer_reviews,
)

# 创建FastMCP实例
mcp = FastMCP("FecMall MCP Server")

# 初始化配置和客户端
config = FecMallConfig()
print(f"config: {config}")
client = FecMallClient(config)


# ==================== Auth Tools ====================

@mcp.tool()
def customer_login_submit_tool(email: str, password: str) -> str:
    """
    提交客户登录信息
    Args:
        email: 客户邮箱
        password: 客户密码
    Returns:
        str: 登录响应结果
    """
    try:
        print(f"customer_login_submit_tool-1: {client}, {email}, {password}")
        result = customer_login_submit(client, email, password)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def customer_login_tool(access_token: str) -> str:
    """
    验证客户登录状态
    Args:
        access_token: 访问令牌
    Returns:
        str: 登录状态验证结果
    """
    try:
        result = customer_login(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Address Tools ====================

@mcp.tool()
def get_customer_addresses_tool(access_token: str) -> str:
    """
    获取客户地址列表
    Args:
        access_token: 访问令牌
    Returns:
        str: 地址列表
    """
    try:
        result = get_customer_addresses(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def get_address_info_tool(access_token: str, address_id: str) -> str:
    """
    获取地址详情（用于编辑页面初始化）
    Args:
        access_token: 访问令牌
        address_id: 地址ID
    Returns:
        str: 地址详情
    """
    try:
        result = get_address_info(client, access_token, address_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def change_address_country_tool(access_token: str, country: str) -> str:
    """
    更改地址国家（编辑页联动获取省/州信息）
    Args:
        access_token: 访问令牌
        country: 国家代码
    Returns:
        str: 国家更改结果
    """
    try:
        result = change_address_country(client, access_token, country)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def save_customer_address_tool(access_token: str, address_data: Dict[str, Any]) -> str:
    """
    保存地址（添加新地址或更新已有地址）
    Args:
        access_token: 访问令牌
        address_data: 地址数据，包含：
                      - address_id: 可选，存在则更新，不存在则新增
                      - first_name, last_name, email, telephone
                      - street1, street2, city, state, country, zip
                      - is_default: 是否设为默认地址
    Returns:
        str: 保存结果
    """
    try:
        result = save_customer_address(client, access_token, address_data)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def remove_customer_address_tool(access_token: str, address_id: str) -> str:
    """
    删除客户地址
    Args:
        access_token: 访问令牌
        address_id: 地址ID
    Returns:
        str: 删除地址结果
    """
    try:
        result = remove_customer_address(client, access_token, address_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Order Tools ====================

@mcp.tool()
def init_customer_order_tool(access_token: str) -> str:
    """
    初始化客户订单
    Args:
        access_token: 访问令牌
    Returns:
        str: 订单初始化结果
    """
    try:
        result = init_customer_order(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def reorder_customer_order_tool(access_token: str, order_id: str) -> str:
    """
    重新订购
    Args:
        access_token: 访问令牌
        order_id: 订单ID
    Returns:
        str: 重新订购结果
    """
    try:
        result = reorder_customer_order(client, access_token, order_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def view_customer_order_tool(access_token: str, order_id: str) -> str:
    """
    查看客户订单
    Args:
        access_token: 访问令牌
        order_id: 订单ID
    Returns:
        str: 订单详情
    """
    try:
        result = view_customer_order(client, access_token, order_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Product Tools ====================

@mcp.tool()
def search_products_tool(search_params: Dict[str, Any]) -> str:
    """
    搜索产品
    Args:
        search_params: 搜索参数字典
    Returns:
        str: 搜索结果
    """
    try:
        result = search_products(client, search_params)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def get_product_info_tool(product_id: str) -> str:
    """
    获取产品详情
    Args:
        product_id: 产品ID
    Returns:
        str: 产品详情
    """
    try:
        result = get_product_info(client, product_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def add_to_cart_from_product_tool(access_token: str, product_id: str, qty: int, custom_option: Dict[str, Any] = None) -> str:
    """
    从产品页面添加到购物车
    Args:
        access_token: 访问令牌
        product_id: 产品ID
        qty: 数量
        custom_option: 自定义选项（可选）
    Returns:
        str: 添加结果
    """
    try:
        result = add_to_cart_from_product(client, access_token, product_id, qty, custom_option or {})
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def add_to_favorite_tool(access_token: str, product_id: str) -> str:
    """
    添加产品到收藏
    Args:
        access_token: 访问令牌
        product_id: 产品ID
    Returns:
        str: 添加收藏结果
    """
    try:
        result = add_to_favorite(client, access_token, product_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def get_product_reviews_tool(product_id: str) -> str:
    """
    获取产品评价列表
    Args:
        product_id: 产品ID
    Returns:
        str: 产品评价列表
    """
    try:
        result = get_product_reviews(client, product_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def add_product_review_tool(access_token: str, product_id: str, star: int, summary: str, review_content: str, name: str) -> str:
    """
    添加产品评价
    Args:
        access_token: 访问令牌
        product_id: 产品ID
        star: 评分(1-5)
        summary: 评价摘要
        review_content: 评价内容
        name: 用户名
    Returns:
        str: 评价提交结果
    """
    try:
        result = add_product_review(client, access_token, product_id, star, summary, review_content, name)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Category Tools ====================

@mcp.tool()
def get_category_products_tool(category_id: str, sort_column: str = "", filter_attrs: Dict[str, Any] = None, filter_price: str = "") -> str:
    """
    获取分类下的产品列表
    Args:
        category_id: 分类ID
        sort_column: 排序列
        filter_attrs: 属性筛选
        filter_price: 价格筛选(如"20-30")
    Returns:
        str: 分类产品列表
    """
    try:
        result = get_category_products(client, category_id, sort_column, filter_attrs or {}, filter_price)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def get_category_info_tool(category_id: str) -> str:
    """
    获取分类信息
    Args:
        category_id: 分类ID
    Returns:
        str: 分类信息详情
    """
    try:
        result = get_category_info(client, category_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Cart Tools ====================

@mcp.tool()
def get_cart_tool(access_token: str) -> str:
    """
    获取购物车信息
    Args:
        access_token: 访问令牌
    Returns:
        str: 购物车信息
    """
    try:
        result = get_cart(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def update_cart_item_tool(access_token: str, item_id: str, up_type: str) -> str:
    """
    更新购物车项
    Args:
        access_token: 访问令牌
        item_id: 购物车项ID
        up_type: 更新类型("less_one"/"add_one"/"remove")
    Returns:
        str: 更新结果
    """
    try:
        result = update_cart_item(client, access_token, item_id, up_type)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def add_coupon_tool(access_token: str, coupon_code: str) -> str:
    """
    添加优惠券
    Args:
        access_token: 访问令牌
        coupon_code: 优惠券代码
    Returns:
        str: 添加优惠券结果
    """
    try:
        result = add_coupon(client, access_token, coupon_code)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def cancel_coupon_tool(access_token: str) -> str:
    """
    取消优惠券
    Args:
        access_token: 访问令牌
    Returns:
        str: 取消优惠券结果
    """
    try:
        result = cancel_coupon(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Onepage Tools ====================

@mcp.tool()
def get_onepage_info_tool(access_token: str) -> str:
    """
    获取结账页面信息
    Args:
        access_token: 访问令牌
    Returns:
        str: 结账页面信息
    """
    try:
        result = get_onepage_info(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def change_onepage_country_tool(access_token: str, country: str) -> str:
    """
    更改结账页面国家
    Args:
        access_token: 访问令牌
        country: 国家代码
    Returns:
        str: 国家更改结果
    """
    try:
        result = change_onepage_country(client, access_token, country)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def update_onepage_info_tool(access_token: str, address_data: Dict[str, Any]) -> str:
    """
    更新结账页面信息
    Args:
        access_token: 访问令牌
        address_data: 地址信息（包含address, shipping_method, payment_method等）
    Returns:
        str: 更新结果
    """
    try:
        result = update_onepage_info(client, access_token, address_data)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Payment Tools ====================

@mcp.tool()
def paypal_express_start_tool(access_token: str) -> str:
    """
    启动PayPal快速结账
    Args:
        access_token: 访问令牌
    Returns:
        str: 支付启动结果
    """
    try:
        result = paypal_express_start(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def paypal_express_review_tool(access_token: str) -> str:
    """
    查看PayPal快速结账订单
    Args:
        access_token: 访问令牌
    Returns:
        str: 订单预览信息
    """
    try:
        result = paypal_express_review(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def paypal_express_submit_tool(access_token: str, order_data: Dict[str, Any]) -> str:
    """
    提交PayPal快速结账订单
    Args:
        access_token: 访问令牌
        order_data: 订单数据
    Returns:
        str: 订单提交结果
    """
    try:
        result = paypal_express_submit(client, access_token, order_data)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def paypal_standard_start_tool(access_token: str) -> str:
    """
    启动PayPal标准支付
    Args:
        access_token: 访问令牌
    Returns:
        str: 支付启动结果
    """
    try:
        result = paypal_standard_start(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def paypal_standard_review_tool(access_token: str) -> str:
    """
    查看PayPal标准支付订单
    Args:
        access_token: 访问令牌
    Returns:
        str: 订单预览信息
    """
    try:
        result = paypal_standard_review(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def alipay_standard_start_tool(access_token: str) -> str:
    """
    启动支付宝标准支付
    Args:
        access_token: 访问令牌
    Returns:
        str: 支付启动结果
    """
    try:
        result = alipay_standard_start(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def alipay_standard_review_tool(access_token: str) -> str:
    """
    查看支付宝标准支付订单
    Args:
        access_token: 访问令牌
    Returns:
        str: 订单预览信息
    """
    try:
        result = alipay_standard_review(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def checkmoney_start_tool(access_token: str) -> str:
    """
    启动支票/汇票支付
    Args:
        access_token: 访问令牌
    Returns:
        str: 支付启动结果
    """
    try:
        result = checkmoney_start(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def payment_success_tool(access_token: str) -> str:
    """
    支付成功处理
    Args:
        access_token: 访问令牌
    Returns:
        str: 支付成功处理结果
    """
    try:
        result = payment_success(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Customer Register Tools ====================

@mcp.tool()
def get_register_info_tool() -> str:
    """
    获取注册页面信息
    Returns:
        str: 注册页面信息
    """
    try:
        result = get_register_info(client)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def submit_register_tool(email: str, password: str, firstname: str, lastname: str, captcha: str = "") -> str:
    """
    提交注册信息
    Args:
        email: 邮箱
        password: 密码
        firstname: 名
        lastname: 姓
        captcha: 验证码（可选）
    Returns:
        str: 注册结果
    """
    try:
        result = submit_register(client, email, password, firstname, lastname, captcha)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Customer Password Tools ====================

@mcp.tool()
def forgot_password_init_tool() -> str:
    """
    初始化忘记密码页面
    Returns:
        str: 忘记密码页面信息
    """
    try:
        result = forgot_password_init(client)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def forgot_password_send_code_tool(email: str, captcha: str = "") -> str:
    """
    发送忘记密码验证码
    Args:
        email: 邮箱
        captcha: 验证码（可选）
    Returns:
        str: 发送结果
    """
    try:
        result = forgot_password_send_code(client, email, captcha)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def reset_password_init_tool() -> str:
    """
    初始化重置密码页面
    Returns:
        str: 重置密码页面信息
    """
    try:
        result = reset_password_init(client)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def reset_password_submit_tool(email: str, code: str, new_password: str, confirm_password: str) -> str:
    """
    提交重置密码
    Args:
        email: 邮箱
        code: 验证码
        new_password: 新密码
        confirm_password: 确认密码
    Returns:
        str: 重置结果
    """
    try:
        result = reset_password_submit(client, email, code, new_password, confirm_password)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Customer Account Tools ====================

@mcp.tool()
def get_customer_info_tool(access_token: str) -> str:
    """
    获取客户信息
    Args:
        access_token: 访问令牌
    Returns:
        str: 客户信息
    """
    try:
        result = get_customer_info(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def get_account_edit_tool(access_token: str) -> str:
    """
    获取账户编辑信息
    Args:
        access_token: 访问令牌
    Returns:
        str: 账户编辑信息
    """
    try:
        result = get_account_edit(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def submit_account_edit_tool(access_token: str, firstname: str, lastname: str, current_password: str = "", new_password: str = "") -> str:
    """
    提交账户编辑
    Args:
        access_token: 访问令牌
        firstname: 名
        lastname: 姓
        current_password: 当前密码（可选）
        new_password: 新密码（可选）
    Returns:
        str: 编辑结果
    """
    try:
        result = submit_account_edit(client, access_token, firstname, lastname, current_password, new_password)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Customer Contacts Tools ====================

@mcp.tool()
def get_contacts_info_tool() -> str:
    """
    获取联系表单信息
    Returns:
        str: 联系表单信息
    """
    try:
        result = get_contacts_info(client)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def submit_contacts_tool(name: str, email: str, telephone: str, comment: str, captcha: str = "") -> str:
    """
    提交联系表单
    Args:
        name: 姓名
        email: 邮箱
        telephone: 电话
        comment: 评论内容
        captcha: 验证码（可选）
    Returns:
        str: 提交结果
    """
    try:
        result = submit_contacts(client, name, email, telephone, comment, captcha)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Customer Favorite Tools ====================

@mcp.tool()
def get_favorite_list_tool(access_token: str) -> str:
    """
    获取客户收藏列表
    Args:
        access_token: 访问令牌
    Returns:
        str: 收藏列表
    """
    try:
        result = get_favorite_list(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def remove_favorite_tool(access_token: str, favorite_id: str) -> str:
    """
    删除收藏
    Args:
        access_token: 访问令牌
        favorite_id: 收藏ID
    Returns:
        str: 删除结果
    """
    try:
        result = remove_favorite(client, access_token, favorite_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== Customer Review Tools ====================

@mcp.tool()
def get_customer_reviews_tool(access_token: str) -> str:
    """
    获取客户评价列表
    Args:
        access_token: 访问令牌
    Returns:
        str: 客户评价列表
    """
    try:
        result = get_customer_reviews(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="sse", port=8000, host="0.0.0.0")
