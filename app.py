import base64
import streamlit as st
from io import BytesIO
from openai import OpenAI

client = OpenAI()

audio = st.audio_input('Record your voice:')

if audio and st.button("Send a Message"):
    # 1) 음성 → 텍스트
    transcript = client.audio.transcriptions.create(
        model='whisper-1',
        file=audio
    )
    st.chat_message('user').write(transcript.text)

    # 2) 답변 생성
    resp = client.chat.completions.create(
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=200,
        messages=[{'role': 'user', 'content': transcript.text}]
    )
    reply_text = resp.choices[0].message.content
    st.chat_message('ai').write(reply_text)

    # 3) TTS (메모리로 받기)
    buf = BytesIO()
    with client.audio.speech.with_streaming_response.create(
        model='tts-1',
        voice='alloy',
        input=reply_text
    ) as tts_stream:
        for chunk in tts_stream.iter_bytes():
            buf.write(chunk)

    # 4) HTML <audio> (컨트롤 없음, JS 없음, 자동재생 시도)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    st.html(f'''
             <audio autoplay style="display:none">
                 <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
             </audio>
             ''')
