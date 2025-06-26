from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from googletrans import Translator

from test_01 import OUT_DIR
from test_02_02 import OUT_2_3, read_text_and_draw_line
from test_02_01 import read_text

def read_text_and_translate(path: Path):
    """OCR 결과를 번역하여 반환"""
    translator = Translator()
    parsed = read_text(path)
    translated_results = []
    
    for bbox, text, prob in parsed:
        try:
            translated = translator.translate(text, dest='ko').text
            translated_results.append((bbox, text, translated, prob))
        except:
            translated_results.append((bbox, text, text, prob))  # 번역 실패시 원문 유지
    
    return translated_results

st.title("✌ 인식률 체크 문자 인식 웹 앱")

uploaded = st.file_uploader("인식할 이미지를 선택하세요.")
if uploaded is not None:
    tmp_path = OUT_DIR / f"{Path(__file__).stem}.tmp"
    tmp_path.write_bytes(uploaded.getvalue())

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("원본 이미지")
        st.image(tmp_path.as_posix())
    with col_right:
        st.subheader("문자 인식 결과")
        with st.spinner(text="문자를 인식하는 중입니다..."):
            read_text_and_draw_line(tmp_path)
        st.image(OUT_2_3.as_posix())
    
    # 번역 결과를 표로 표시
    st.subheader("🌐 번역 결과")
    with st.spinner(text="번역하는 중입니다..."):
        translated_results = read_text_and_translate(tmp_path)
        
        # 표 형태로 결과 표시
        import pandas as pd
        df_data = []
        for i, (bbox, original, translated, prob) in enumerate(translated_results):
            df_data.append({
                "순번": i+1,
                "원문": original,
                "번역": translated,
                "신뢰도": f"{prob:.2f}"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)