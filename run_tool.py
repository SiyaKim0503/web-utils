import streamlit as st
import os

st.set_page_config(page_title="Web Utils", layout="wide")
st.markdown(
    "<div style='font-size:22px; font-weight:600; margin-bottom: 10px;'>Web Utility 도구 모음</div>",
    unsafe_allow_html=True
)


# 사용할 도구 목록
TOOLS = {
    "📄 JSON 열 추출기": "tools/json_column_extractor/app.py",
    "🔍 형태소 분석기": "tools/morpheme_analyzer/app.py",
    "✨ 어 있 결과 뷰어": "tools/morpheme_chain_highlighter/app.py"  # ← 변경된 항목
}



# 사이드바에서 도구 선택
tool_choice = st.sidebar.radio("사용할 도구를 선택하세요", list(TOOLS.keys()))

# 선택한 도구의 app.py 파일을 실행
tool_path = TOOLS[tool_choice]

if os.path.exists(tool_path):
    with open(tool_path, encoding="utf-8") as f:
        code = f.read()
    exec(code, globals())
else:
    st.error(f"도구 파일을 찾을 수 없습니다: {tool_path}")
