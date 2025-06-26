from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from googletrans import Translator

from test_01 import IN_DIR, OUT_DIR
from test_02_02 import OUT_2_2, read_text_and_draw_line
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

def create_filled_translation_image(path: Path, translated_results):
    """번역된 텍스트로 채워진 이미지 생성"""
    img = Image.open(path)
    draw = ImageDraw.Draw(img, "RGBA")
    
    # 폰트 파일이 있는지 확인하고 로드
    try:
        font = ImageFont.truetype(str(IN_DIR / "Pretendard-Bold.ttf"), size=60)
    except:
        # 폰트 파일이 없으면 기본 폰트 사용
        font = ImageFont.load_default()
    
    PROB = 0.75
    
    for bbox, original, translated, prob in translated_results:
        box = [(x, y) for x, y in bbox]
        
        # 배경 채우기 (반투명)
        draw.polygon(
            box,
            fill=(255, 0, 0, 100) if prob >= PROB else (0, 255, 0, 100),
        )
        
        # 번역된 텍스트 그리기
        draw.text(xy=box[0], text=translated, fill=(255, 255, 255), font=font)
    
    # 임시 파일로 저장
    output_path = OUT_DIR / "translated_filled.jpg"
    img.save(output_path)
    return output_path

st.title("✌ 인식률 체크 문자 인식 웹 앱")

uploaded = st.file_uploader("인식할 이미지를 선택하세요.")
if uploaded is not None:
    tmp_path = OUT_DIR / f"{Path(__file__).stem}.tmp"
    tmp_path.write_bytes(uploaded.getvalue())

    # 3개의 열로 구성
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("원본 이미지")
        st.image(tmp_path.as_posix())
    
    with col2:
        st.subheader("문자 인식 결과")
        with st.spinner(text="문자를 인식하는 중입니다..."):
            read_text_and_draw_line(tmp_path)
        st.image(OUT_2_2.as_posix())
    
    with col3:
        st.subheader("번역 결과 이미지")
        with st.spinner(text="번역하는 중입니다..."):
            translated_results = read_text_and_translate(tmp_path)
            filled_image_path = create_filled_translation_image(tmp_path, translated_results)
        st.image(filled_image_path.as_posix())
    
    # 번역 결과를 표로 표시
    st.subheader("🌐 번역 결과 상세")
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
