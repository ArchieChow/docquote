import streamlit as st
import json
import requests
import pandas as pd


# ------------------------- 报价计算函数 -------------------------
def calculate_price(cost_price, promotion_rate, tariff_rate, accessories_cost, quantity):
    insurance_fee_rate = 0.03
    profit_margin = 0.3
    exchange_rate = 7.2

    insurance_fee = cost_price * insurance_fee_rate
    promotion = cost_price * promotion_rate
    tariff = cost_price * tariff_rate

    total_cost = cost_price + insurance_fee + promotion + tariff + accessories_cost
    cny_unit_price = total_cost * (1 + profit_margin)
    usd_unit_price = cny_unit_price / exchange_rate
    usd_total_price = usd_unit_price * quantity if quantity > 0 else 0
    usd_unit_kg = quantity * 0.02

    return {
        "总采购成本": round(total_cost, 4),
        "人民币总价": round(cny_unit_price, 4),
        "美元单价": round(usd_unit_price, 4),
        "美元总价": round(usd_total_price, 4),
        "预估重量": round(usd_unit_kg, 4),
    }

# ------------------------- Streamlit 主页面结构 -------------------------
st.set_page_config(page_title="综合报价物流系统", layout="centered")
st.title("📦 综合报价 + 物流工具")

tab1, tab2, tab3 = st.tabs(["🧾 报价计算", "🚚 运费查询", "📍 轨迹查询"])

# ------------------------- Tab 1: 报价系统 -------------------------

with tab1:
    st.subheader("报价计算")
    col1, col2, col3 = st.columns(3)
    with col1:
        cost_price = st.number_input("采购成本 (元)", value=0.0)
        promotion_rate = st.number_input("促销折扣 (%)", value=0.0) / 100
    with col2:
        tariff_rate = st.number_input("关税 (%)", value=0.0) / 100
        accessories_cost = st.number_input("配件成本 (元)", value=0.0)
    with col3:
        quantity = st.number_input("件数", value=0.0)

    if st.button("📊 开始计算"):
        result = calculate_price(cost_price, promotion_rate, tariff_rate, accessories_cost, quantity)
        st.subheader("📈 计算结果：")
        for label, value in result.items():
            st.write(f"**{label}**: {value:.2f}")
    else:
        st.info("请填写所有必填项并点击“开始计算”按钮。")

# ------------------------- Tab 2: 运费查询 -------------------------
with tab2:
    st.subheader("HY 物流运费查询")

    country_map = {
        "美国": "US",
        "加拿大": "CA",
        "德国": "DE",
        "法国": "FR"
    }

    selected_country = st.selectbox("选择目的国家", list(country_map.keys()))
    country_code = country_map[selected_country]
    weight = st.text_input("请输入包裹重量 (kg)", "1")

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
                    usd_fee = round(total_fee / 7.2, 2)
                    result_list.append({
                        "运输方式": d.get("ServiceCnName", ""),
                        "运输时效": d.get("Effectiveness", ""),
                        "计费重量": d.get("ChargeWeight", ""),
                        "总费用 (RMB)": f"{total_fee:.2f}",
                        "总费用 (USD)": f"{usd_fee:.2f}"
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
    st.subheader("HY 快递轨迹查询")
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
                    st.success("查询成功，以下是物流轨迹：")
                    for d in data:
                        for detail in d.get("details", []):
                            st.markdown(f"""
                            - **时间：** {detail.get("track_occur_date", "")}  
                              **地点：** {detail.get("track_location", "")}  
                              **状态：** {detail.get("track_description", "")}
                            """)
            except Exception as e:
                st.error(f"查询失败：{e}")

# ------------------------- 页面底部 -------------------------
st.markdown("---")
st.caption("©2025 浩远物流(当前汇率: 7.2)")
