import streamlit as st
from kiwipiepy import Kiwi

st.title("📝 한국어 형태소 분석기 (Kiwi 기반)")

with st.expander("📌 사용 방법 안내"):
    st.markdown("""
**이 앱은 `kiwi` 한국어 형태소 분석기를 활용하여 제작되었습니다.**  
텍스트 파일(.txt, UTF-8 인코딩)을 업로드하면 문장별로 형태소 분석을 수행하고 결과를 보여줍니다.

**예시 입력 형식 (텍스트 파일)**:

오늘 날씨가 좋다. 기계는 언어를 어떻게 이해할까?

**출력 형식 (분석 결과)**:

오늘/NNG 날씨/NNG 가/JKS 좋/VA 다/EF ./SF 기계/NNG 는/JX 언어/NNG 를/JKO 어떻게/MAG 이해/NNG 하/XSV ㄹ까/EF ./SF

- 분석 결과는 최대 20줄까지만 화면에 미리 보여지며,
- 전체 결과는 다운로드 버튼을 통해 받을 수 있습니다.
""")

kiwi = Kiwi()

uploaded_file = st.file_uploader("📂 텍스트 파일 업로드 (.txt, UTF-8 인코딩)", type=["txt"])
analyze_clicked = st.button("🔍 분석 시작")

if uploaded_file is not None and analyze_clicked:
    try:
        text = uploaded_file.read().decode("utf-8")
        lines = text.splitlines()
        
        result_lines = []
        for line in lines:
            if line.strip() == "":
                continue
            tokens = kiwi.tokenize(line)
            analyzed = " ".join(f"{t.form}/{t.tag}" for t in tokens)
            result_lines.append(analyzed)

        result_text = "\n".join(result_lines)
        
        # 화면에는 최대 20줄까지만 보여주기
        preview_lines = result_lines[:20]
        preview_text = "\n".join(preview_lines)
        
        st.subheader("🔎 분석 결과 (미리보기: 최대 20줄)")
        st.text_area("형태소 분석 결과 미리보기", preview_text, height=300)
        
        st.download_button("📥 전체 결과 다운로드", result_text, file_name="kiwi_result.txt")
    
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
elif uploaded_file and not analyze_clicked:
    st.info("👆 텍스트 파일을 업로드한 후, '🔍 분석 시작' 버튼을 눌러주세요.")
