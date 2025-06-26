from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import requests
import time

from test_01 import IN_DIR, OUT_DIR
from test_02_02 import OUT_2_2, read_text_and_draw_line
from test_02_01 import read_text

def translate_with_mymemory(text, source_lang='en', target_lang='ko'):
    """MyMemory API를 사용한 번역"""
    url = "https://api.mymemory.translated.net/get"
    params = {
        'q': text,
        'langpair': f'{source_lang}|{target_lang}'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['responseStatus'] == 200:
                return data['responseData']['translatedText']
        return text  # 번역 실패시 원문 반환
    except Exception as e:
        print(f"번역 오류: {e}")
        return text

def read_text_and_translate(path: Path):
    """OCR 결과를 번역하여 반환"""
    parsed = read_text(path)
    translated_results = []
    
    for bbox, text, prob in parsed:
        # 텍스트가 비어있거나 너무 짧으면 번역하지 않음
        if len(text.strip()) < 2:
            translated_results.append((bbox, text, text, prob))
            continue
            
        # MyMemory API 사용 (요청 간격 조절)
        translated = translate_with_mymemory(text, 'en', 'ko')
        translated_results.append((bbox, text, translated, prob))
        
        # API 요청 제한을 위한 짧은 대기
        time.sleep(0.1)
    
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
        try:
            # Windows의 경우 맑은 고딕 사용
            font = ImageFont.truetype("malgun.ttf", size=60)
        except:
            # 기본 폰트 사용
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
        try:
            draw.text(xy=box[0], text=translated, fill=(255, 255, 255), font=font)
        except:
            # 폰트 문제가 있을 경우 기본 폰트로 재시도
            draw.text(xy=box[0], text=translated, fill=(255, 255, 255))
    
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