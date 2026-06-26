import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI 에너지 취약가구 탐지 시스템",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 AI 에너지 취약가구 탐지 시스템")
st.markdown("폭염 상황에서 전력 사용량 감소 가구를 탐지하여 위험도를 계산합니다.")

uploaded_file = st.file_uploader("📂 CSV 파일 업로드", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.subheader("📋 업로드 데이터")
    st.dataframe(df)

    # -----------------------
    # 위험도 계산
    # -----------------------

    df["Usage_Drop"] = (
        (df["Expected_Usage"] - df["Actual_Usage"])
        / df["Expected_Usage"]
    ) * 100

    def calculate_score(row):

        score = 0

        # 기온
        if row["Temperature"] >= 35:
            score += 30
        elif row["Temperature"] >= 33:
            score += 20

        # 전력 감소
        if row["Usage_Drop"] >= 40:
            score += 40
        elif row["Usage_Drop"] >= 20:
            score += 20

        # 노후주택
        if row["Building_Age"] >= 30:
            score += 20
        elif row["Building_Age"] >= 20:
            score += 10

        # 취약계층
        if row["Is_Vulnerable"] == 1:
            score += 10

        return min(score,100)

    df["Risk_Score"] = df.apply(calculate_score,axis=1)

    def risk(score):

        if score>=80:
            return "🔴 매우 위험"

        elif score>=60:
            return "🟠 위험"

        elif score>=40:
            return "🟡 주의"

        else:
            return "🟢 안전"

    df["Risk_Level"] = df["Risk_Score"].apply(risk)

    df = df.sort_values(
        by="Risk_Score",
        ascending=False
    )

    df.insert(0,"Priority",range(1,len(df)+1))

    # -----------------------
    # 대시보드
    # -----------------------

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "총 가구",
        len(df)
    )

    c2.metric(
        "최고 위험도",
        int(df["Risk_Score"].max())
    )

    c3.metric(
        "고위험 가구",
        len(df[df["Risk_Score"]>=80])
    )

    st.subheader("🚨 위험도 우선순위")

    st.dataframe(
        df[[
            "Priority",
            "Household_ID",
            "Risk_Score",
            "Risk_Level",
            "Usage_Drop"
        ]]
    )

    st.subheader("📊 위험도 그래프")

    fig = px.bar(
        df.head(20),
        x="Household_ID",
        y="Risk_Score",
        color="Risk_Level"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("📨 위험 알림")

    high = df[df["Risk_Score"]>=80]

    if len(high)==0:
        st.success("고위험 가구가 없습니다.")

    else:

        for _,row in high.iterrows():

            st.error(
                f"""
🚨 {row['Household_ID']}

위험도 : {row['Risk_Score']}

폭염 상황에서 전력 사용량이 감소했습니다.

현장 확인이 필요합니다.
"""
            )

    st.download_button(
        "📥 결과 다운로드",
        df.to_csv(index=False).encode("utf-8-sig"),
        "result.csv",
        "text/csv"
    )

else:

    st.info("CSV 파일을 업로드하세요.")