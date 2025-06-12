import streamlit as st
import pandas as pd
from io import BytesIO

# 📁 엑셀 파일 경로
EXCEL_PATH = "통합 문서1.xlsx"

# 📤 엑셀을 바이너리로 저장하는 함수
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# 📥 엑셀 불러오기
df = pd.read_excel(EXCEL_PATH, engine='openpyxl')

# ✅ Streamlit 앱 설정
st.set_page_config(layout="wide")
st.title("📊 정책 문서 라벨링 웹앱")

label_cols = ['1차', '2차', '3차']
text_columns = ['Policy Name', 'date', 'title', 'content', 'url', 'docID', 'site name', 'Issue Keyword', 'Responsible ministry']

# 🔍 현재 작업 단계 선택
stage = st.selectbox("🛠 현재 작업 단계를 선택하세요", options=label_cols)
stage_index = label_cols.index(stage)

# 🎯 이전 단계 완료된 데이터만 필터링
if stage_index == 0:
    stage_df = df
else:
    prev_conditions = [(df[label_cols[i]].isin(['Y', 'N', 'M'])) for i in range(stage_index)]
    stage_df = df.loc[pd.concat(prev_conditions, axis=1).all(axis=1)]

# 🔢 현재 문서 인덱스 관리
if "index" not in st.session_state:
    st.session_state.index = 0

filtered_df = stage_df.reset_index()
if st.session_state.index >= len(filtered_df):
    st.success(f"✅ {stage} 라벨링이 완료되었습니다.")

    if stage == '3차':
        final_data = convert_df_to_excel(df)
        st.download_button(
            label="⬇️ 최종 파일 다운로드",
            data=final_data,
            file_name="라벨링_최종완료_web.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        interim_data = convert_df_to_excel(df)
        st.download_button(
            label="💾 중간 저장 파일 다운로드",
            data=interim_data,
            file_name="라벨링_중간저장_web.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    row_idx = filtered_df.at[st.session_state.index, 'index']
    row = df.loc[row_idx]

    st.subheader(f"🧾 현재 문서: {st.session_state.index + 1} / {len(filtered_df)}")

    with st.expander("📋 문서 상세 보기"):
        for col in text_columns:
            if col == 'url':
                if pd.notna(row[col]):
                    st.markdown(f"**{col}**: [바로가기]({row[col]})", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{col}**: -")
            elif col == 'content':
                st.markdown(f"**{col}**: {row[col][:700]}{'...' if len(str(row[col])) > 700 else ''}")
            else:
                st.markdown(f"**{col}**: {row[col]}")

    st.markdown("---")
    st.subheader("🔖 라벨 입력")

    # ✅ 현재 단계만 입력 가능
    for i, col in enumerate(label_cols):
        if i < stage_index:
            st.markdown(f"**{col}**: {row[col] if pd.notna(row[col]) else '-'}")
        elif i == stage_index:
            selected = st.radio(f"{col} 라벨 선택", ['-', 'Y', 'N', 'M'], horizontal=True, key=col)
            if selected != '-':
                df.at[row_idx, col] = selected

    # ▶ 버튼 제어
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("➡️ 다음 문서로 이동"):
            st.session_state.index += 1

    with col2:
        if st.button("💾 중간 저장"):
            interim_data = convert_df_to_excel(df)
            st.download_button(
                label="중간 저장 파일 다운로드",
                data=interim_data,
                file_name="라벨링_중간저장_web.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("중간 저장 완료되었습니다!")
