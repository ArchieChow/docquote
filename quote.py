import streamlit as st
import json
import requests
import pandas as pd

# ------------------------- 报价计算函数 -------------------------
def calculate_price(cost_price, promotion_rate, accessories_cost, quantity):
    insurance_fee_rate = 0.03
    profit_margin = 0.43
    exchange_rate = 6.80

    # 成本构成（不含促销）
    insurance_fee = cost_price * insurance_fee_rate
    total_cost = cost_price + insurance_fee + accessories_cost

    # 人民币售价（含利润）
    cny_unit_price = total_cost * (1 + profit_margin)

    # 加促销加价（作用于含利润价格）
    cny_unit_price += cny_unit_price * promotion_rate

    # 美元价格
    usd_unit_price = cny_unit_price / exchange_rate
    usd_total_price = usd_unit_price * quantity if quantity > 0 else 0
    usd_weight_estimate = quantity * 0.02  # 每件0.02kg估重

    return {
        "总采购成本 (¥)": round(total_cost, 4),
        "人民币单价 (¥)": round(cny_unit_price, 4),
        "美元单价 ($)": round(usd_unit_price, 4),
        "美元总价 ($)": round(usd_total_price, 4),
        "预估总净重 (kg)": round(usd_weight_estimate, 2),
    }

# ------------------------- Streamlit 页面结构 -------------------------
st.set_page_config(page_title="综合报价物流系统", layout="centered")
st.title("📦 综合报价 + 物流工具")

tab1, tab2, tab3 = st.tabs(["🧾 报价计算", "🚚 运费查询", "📍 轨迹查询"])

# ------------------------- Tab 1: 报价系统 -------------------------
with tab1:
    st.subheader("📊 报价计算")
    col1, col2 = st.columns(2)
    with col1:
        cost_price = st.number_input("采购成本 (¥)", value=0.000, format="%.3f")
        promotion_rate = st.number_input("促销加价比例 (%)", value=0.000, format="%.3f") / 100
    with col2:
        accessories_cost = st.number_input("配件成本 (¥)", value=0.000, format="%.3f")
        quantity = st.number_input("件数", value=0.000, format="%.3f")

    if st.button("开始计算"):
        result = calculate_price(cost_price, promotion_rate, accessories_cost, quantity)
        st.subheader("📈 计算结果")
        for label, value in result.items():
            st.write(f"**{label}**: {value:.4f}")  # 修改此行为4位小数显示
    else:
        st.info("请填写完整信息后点击“开始计算”。")

# ------------------------- Tab 2: 运费查询 -------------------------
with tab2:
    st.subheader("🚚 HY 物流运费查询")

    country_map = {
        "美国": "US",
        "加拿大": "CA",
        "德国": "DE",
        "法国": "FR",
        "日本": "JP",
        "澳大利亚": "AU",
        "中国香港": "HK",
        "英国": "GB",
        "意大利": "IT",
        "越南": "VN",
        "泰国": "TH",
        "印度": "IN",
        "马来西亚": "MY",
        "菲律宾": "PH",
        "印尼": "ID",
        "韩国": "KR",
        "新加坡": "SG",
        "阿尔巴尼亚": "AL",
        "奥地利": "AT",
        "白俄罗斯": "BY",
        "保加利亚": "BG",
        "比利时": "BE",
        "冰岛": "IS",
        "波兰": "PL",
        "丹麦": "DK",
        "俄罗斯": "RU",
        "芬兰": "FI",
        "荷兰": "NL",
        "立陶宛": "LT",
        "列支敦士登": "LI",
        "卢森堡": "LU",
        "罗马尼亚": "RO",
        "马耳他": "MT",
        "摩尔多瓦": "MD",
        "摩纳哥": "MC",
        "挪威": "NO",
        "葡萄牙": "PT",
        "圣马力诺": "SM",
        "斯洛文尼亚": "SI",
        "乌克兰": "UA",
        "西班牙": "ES",
        "希腊": "GR",
        "匈牙利": "HU",
        "巴基斯坦": "PK",
        "朝鲜": "KP",
        "老挝": "LA",
        "马尔代夫": "MV",
        "蒙古": "MN",
        "孟加拉国": "BD",
        "缅甸": "MM",
        "尼泊尔": "NP",
        "斯里兰卡": "LK",
        "文莱": "BN",
        "乌兹别克斯坦": "UZ",
        "阿富汗": "AF",
        "阿拉伯联合酋长国": "AE",
        "阿曼": "OM",
        "巴林": "BH",
        "格鲁吉亚": "GE",
        "哈萨克斯坦": "KZ",
        "卡塔尔": "QA",
        "科威特": "KW",
        "黎巴嫩": "LB",
        "塞浦路斯": "CY",
        "沙特阿拉伯": "SA",
        "塔吉克斯坦": "TJ",
        "土耳其": "TR",
        "土库曼斯坦": "TM",
        "叙利亚": "SY",
        "亚美尼亚": "AM",
        "伊拉克": "IQ",
        "伊朗": "IR",
        "以色列": "IL",
        "阿根廷": "AR",
        "巴拉圭": "PY",
        "巴西": "BR",
        "厄瓜多尔": "EC",
        "哥伦比亚": "CO",
        "圭亚那": "GY",
        "秘鲁": "PE",
        "苏里南": "SR",
        "委内瑞拉": "VE",
        "乌拉圭": "UY",
        "新西兰": "NZ"
    }

    selected_country = st.selectbox("选择目的国家", list(country_map.keys()))
    country_code = country_map[selected_country]
    weight = st.text_input("请输入包裹重量 (kg)", "1.00")

    if st.button("查询运费"):
        try:
            url = "http://order.hy-express.com/webservice/PublicService.asmx/ServiceInterfaceUTF8"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            payload = {
                "appToken": "3f7e28f91fe9012a8cf511673228d5b6",
                "appKey": "a68b54a8852c481d00ad92625da6a6e8a68b54a8852c481d00ad92625da6a6e8",
                "serviceMethod": "feetrail",
                "paramsJson": json.dumps({"country_code": country_code, "weight": weight})
            }

            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            data = json.loads(response.text).get("data", [])

            if data:
                result_list = []
                for d in data:
                    total_fee = float(d.get("TotalFee", 0))
                    usd_fee = round((total_fee / 6.8) * 1.03, 3)
                    result_list.append({
                        "运输方式": d.get("ServiceCnName", ""),
                        "运输时效": d.get("Effectiveness", ""),
                        "计费重量": d.get("ChargeWeight", ""),
                        "总费用 (¥)": f"{total_fee:.2f}",
                        "总费用 ($)": f"{usd_fee:.2f}"
                    })

                df = pd.DataFrame(result_list)
                st.success("查询成功")
                st.dataframe(df)
            else:
                st.warning("未获取到物流数据。")
        except Exception as e:
            st.error(f"查询失败：{e}")

# ------------------------- Tab 3: 快递轨迹查询 -------------------------
with tab3:
    st.subheader("📍 HY 快递轨迹查询")
    tracking_number = st.text_input("请输入运单号")

    if tracking_number:
        with st.spinner("查询中..."):
            try:
                url = "http://order.hy-express.com/webservice/PublicService.asmx/ServiceInterfaceUTF8"
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                payload = {
                    "appToken": "3f7e28f91fe9012a8cf511673228d5b6",
                    "appKey": "a68b54a8852c481d00ad92625da6a6e8a68b54a8852c481d00ad92625da6a6e8",
                    "serviceMethod": "gettrack",
                    "paramsJson": json.dumps({"tracking_number": tracking_number})
                }

                response = requests.post(url, headers=headers, data=payload)
                response.raise_for_status()
                data = json.loads(response.text).get("data", [])

                if not data:
                    st.warning("未找到运单信息。")
                else:
                    st.success("查询成功，以下为轨迹信息：")
                    for d in data:
                        for detail in d.get("details", []):
                            st.markdown(f"""
                            - **Date：** {detail.get("track_occur_date", "")}  
                              **Location：** {detail.get("track_location", "")}  
                              **Description：** {detail.get("track_description", "")}
                            """)
            except Exception as e:
                st.error(f"查询失败：{e}")

# ------------------------- 页面底部 -------------------------
st.markdown("---")
st.caption("©2025 浩远物流（当前汇率: 6.80）")






