import streamlit as st
import pandas as pd
import re

st.title("어 있 결과 뷰어 (st.dataframe + 텍스트 색상 강조)")

# 사용자 안내 문구 추가: 데이터
st.info("""
    💡 **데이터 업로드:** \n
    기존에 공유 드린 "matched_sentences".tsv" 파일을 업로드하세요.
""")

# 사용자 안내 문구 추가: 표
st.info("""
    💡 **테이블 사용법:** \n
    표 안에 들어가는 내용이 길 경우 내용이 보이지 않을 수 있습니다. \n
    전체 내용을 보려면 해당 셀 너비를 수동으로 드래그하여 변경하거나 \n
    해당 셀을 **클릭**하세요.
""")

uploaded_file = st.file_uploader("TSV 파일 업로드", type=["tsv"])

# 파일이 업로드된 경우 처리 시작
if uploaded_file:
    # TSV 파일 읽기
    df = pd.read_csv(uploaded_file, sep="\t")

    # 필수 열 확인
    if "matched_sent" not in df.columns:
        st.error("❌ 파일에 'matched_sent' 열이 없습니다.")
    else:
        # 결과 저장용 리스트 초기화
        results = []

        # 데이터 처리: DataFrame 행 반복
        for i, row in df.iterrows():
            # 문장 추출 및 토큰화
            sent = str(row["matched_sent"]).strip()
            tokens = sent.split()

            try:
                # 1. '어:EC 있:VX' 패턴 인덱스 찾기
                oi_idx = next(
                    i for i in range(len(tokens) - 1)
                    if tokens[i] == "어:EC" and tokens[i + 1] == "있:VX"
                )

                # 2. '에서:JKB' 패턴 인덱스 찾기 ('어 있' 패턴 이전에서)
                eseo_idx_candidates = [i for i, t in enumerate(tokens[:oi_idx]) if t == "에서:JKB"]
                if not eseo_idx_candidates:
                    continue # '에서:JKB' 없으면 다음 행으로
                eseo_idx = eseo_idx_candidates[-1] # 가장 마지막 '에서:JKB' 사용

                # --- 3. 컨텍스트 및 주요 토큰 추출 ---

                # 3-1. '에서' 앞 토큰 ('pre_eseo_token') 추출
                pre_eseo_token = tokens[eseo_idx - 1] if eseo_idx > 0 else ""

                # 3-2. Left Context 추출: 문장 시작부터 '에서' 앞 토큰 직전까지
                #      (수정: '에서' 앞 토큰이 Left Context에 중복 포함되지 않도록)
                left_context_end_idx = max(0, eseo_idx - 1) # 음수 인덱스 방지
                left_context = " ".join(tokens[0:left_context_end_idx])

                # 3-3. '에서' 토큰
                eseo_token = "에서:JKB"

                # 3-4. '어 있' 앞 토큰 처리 (XSV/XSA 고려) 및 중간 구간 계산용 인덱스
                pre_oi_start_idx = oi_idx # '어 있' 앞 어휘 시작 기본값
                pre_oi_display_token = "" # '어 있' 앞 표시용 토큰
                if oi_idx > 0:
                    pre_oi_token_raw = tokens[oi_idx - 1]
                    if ":" in pre_oi_token_raw: # 태그 존재 여부 확인
                        morph, tag = pre_oi_token_raw.rsplit(":", 1)
                        if tag in ["XSV", "XSA"] and oi_idx - 2 >= 0: # XSV/XSA 태그이고 앞에 토큰이 더 있다면
                            pre_oi_start_idx = oi_idx - 1 # 중간구간 계산 시 XSV/XSA 앞 토큰 미포함
                            pre_oi_display_token = tokens[oi_idx - 2] + " " + pre_oi_token_raw # 표시용 토큰은 결합
                        else:
                            pre_oi_display_token = pre_oi_token_raw # 일반 토큰
                    else:
                        pre_oi_display_token = pre_oi_token_raw # 태그 없는 토큰 대비
                
                # 3-5. 중간 구간: '에서' 다음부터 '어 있 앞' 시작 전까지
                middle_end_idx = pre_oi_start_idx
                
                # 중복 제거: '중간 구간'의 마지막 토큰과 '어 있 앞' 첫 토큰이 같다면 제거
                if middle_end_idx - 1 >= eseo_idx + 1:
                    middle_last_token = tokens[middle_end_idx - 1]
                    if pre_oi_display_token.startswith(middle_last_token):
                        middle_end_idx -= 1 # 중복 제거

                middle_context = " ".join(tokens[eseo_idx + 1 : middle_end_idx])

                # 3-6. '어 있' 토큰
                oi_token = "어:EC 있:VX"

                # 3-7. Right Context 추출 ('어 있' 패턴 다음부터 최대 5개 토큰)
                right_context = " ".join(tokens[oi_idx + 2 : oi_idx + 7])

                # --- 4. 결과 저장 ---
                results.append({
                    "Left Context": left_context,
                    "'에서' 앞": pre_eseo_token,
                    "'에서'": eseo_token,
                    "중간 구간": middle_context,
                    "'어 있' 앞": pre_oi_display_token,
                    "'어 있'": oi_token,
                    "Right Context": right_context,
                })

            except StopIteration: # 'next' 함수에서 패턴 못찾음
                continue
            except Exception as e: # 기타 예외 처리
                # st.warning(f"처리 중 오류 발생 (행 {i}): {e}") # 디버깅 필요시 주석 해제
                continue
        # --- 데이터 처리 완료 ---

        # 결과 유무 확인 및 테이블 표시
        if results:
            st.success(f"✅ 패턴이 감지된 문장 수: {len(results)}개")
            results_df = pd.DataFrame(results)

            # --- Pandas Styler 설정 (텍스트 색상 변경 및 줄바꿈) ---

            def apply_text_color_and_style(column_series, text_color=None, text_align='left'):
                """지정된 열에 텍스트 색상 및 기본 스타일(줄바꿈, 정렬) 적용"""
                # 기본 스타일: 줄바꿈, 지정된 정렬
                base_style = f'white-space: normal !important; word-wrap: break-word !important; text-align: {text_align};'
                styles = []
                for _ in column_series:
                    style = base_style
                    # 텍스트 색상이 지정된 경우, 색상 및 굵은 글씨 추가
                    if text_color:
                        style += f' color: {text_color}; font-weight: bold;'
                    styles.append(style)
                return styles

            # 스타일 적용 객체 생성
            styled_df = results_df.style

            # 각 열에 스타일 적용 (apply 사용, axis=0)
            # 하이라이트가 없는 열 (기본 스타일만 적용)
            styled_df = styled_df.apply(apply_text_color_and_style, text_align='left', subset=["Left Context", "중간 구간", "Right Context"], axis=0)

            # 하이라이트가 있는 열 (텍스트 색상 + 기본 스타일 적용)
            # 색상 이름 또는 Hex 코드 사용 가능
            styled_df = styled_df.apply(apply_text_color_and_style, text_color='#3f51b5', text_align='center', subset=["'에서' 앞"], axis=0) # 파란색 계열
            styled_df = styled_df.apply(apply_text_color_and_style, text_color='#d32f2f', text_align='center', subset=["'에서'"], axis=0) # 빨간색 계열
            styled_df = styled_df.apply(apply_text_color_and_style, text_color='#388e3c', text_align='center', subset=["'어 있' 앞"], axis=0) # 초록색 계열
            styled_df = styled_df.apply(apply_text_color_and_style, text_color='#d32f2f', text_align='center', subset=["'어 있'"], axis=0) # 빨간색 계열


            # st.dataframe으로 최종 테이블 표시
            st.dataframe(styled_df, use_container_width=True)

        else:
            # 결과 없는 경우 메시지 표시
            st.info("해당 패턴을 포함한 문장을 찾을 수 없습니다.")

# 파일 업로드 안된 경우 (초기 상태) - 별도 메시지 없음
# else:
#     st.write("TSV 파일을 업로드해주세요.")