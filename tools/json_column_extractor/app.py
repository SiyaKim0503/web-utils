import streamlit as st
import pandas as pd
import json
import io

st.title("📂 JSON 필드 경로 기반 추출기 (중첩 구조 + 경로 지정 + 파일명 설정)")

uploaded_file = st.file_uploader("JSON 파일을 업로드하세요", type=["json"])

# 경로 추출 함수
def extract_paths(obj, parent_key=""):
    paths = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            paths.extend(extract_paths(v, full_key))
    elif isinstance(obj, list):
        if obj and isinstance(obj[0], dict):
            paths.extend(extract_paths(obj[0], f"{parent_key}[*]"))
        else:
            paths.append(parent_key)
    else:
        paths.append(parent_key)
    return paths

# 선택된 경로에서 값 추출 함수
def extract_values(obj, path):
    parts = path.split(".")
    results = []

    def recurse(o, p, acc):
        if not p:
            results.append(acc)
            return
        key = p[0]
        rest = p[1:]
        if key.endswith("[*]"):
            k = key[:-3]
            items = o.get(k, [])
            if isinstance(items, list):
                for item in items:
                    recurse(item, rest, acc.copy())
        else:
            if isinstance(o, dict) and key in o:
                recurse(o[key], rest, acc + [o[key]] if not rest else acc)
            else:
                recurse({}, rest, acc)

    recurse(obj, parts, [])
    return [r for r in results if r]

if uploaded_file:
    try:
        json_data = json.load(uploaded_file)

        st.subheader("🧭 JSON 구조 탐색")
        path_list = extract_paths(json_data)
        selected_paths = st.multiselect("추출할 필드를 선택하세요", path_list)

        if selected_paths:
            all_rows = []
            longest = 0
            temp_columns = []

            for path in selected_paths:
                values = extract_values(json_data, path)
                flat_values = [v[0] if isinstance(v, list) and v else None for v in values]
                if len(flat_values) > longest:
                    longest = len(flat_values)
                all_rows.append(flat_values)
                temp_columns.append(path)

            # 길이 맞추기
            data = {}
            for col, vals in zip(temp_columns, all_rows):
                if len(vals) < longest:
                    vals += [None] * (longest - len(vals))
                data[col] = vals

            df = pd.DataFrame(data)
            st.subheader("🔍 추출 결과 미리보기")
            st.dataframe(df)

            # 파일 저장 옵션
            file_name_input = st.text_input("저장할 파일 이름 (확장자는 자동으로 붙습니다)", value="selected_fields")
            file_format = st.selectbox("파일 형식 선택", options=["CSV", "TSV"])
            buffer = io.StringIO()

            if file_format == "CSV":
                df.to_csv(buffer, index=False)
                mime = "text/csv"
                ext = "csv"
            else:
                df.to_csv(buffer, index=False, sep="\t")
                mime = "text/tab-separated-values"
                ext = "tsv"

            st.download_button(
                label="💾 다운로드",
                data=buffer.getvalue(),
                file_name=f"{file_name_input.strip() or 'output'}.{ext}",
                mime=mime,
            )

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
