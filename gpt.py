
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def build_prompt(left_txt, right_txt):
    return f"""
[왼손 분석]
{left_txt}

[오른손 분석]
{right_txt}

위 내용을 기반으로 다음 다섯 항목에 대해 감성적으로 분석해줘 (1000자 이내):

1. 손끝 구조 설명
2. 감정/성향 분석
3. 닮은 나무 (Why / What / How)
4. 감성 메시지 한 문장
5. 나무뿌리 이미지 묘사
"""

def call_gpt_mini(prompt):
    res = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 감성 지문 분석가야."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    return res.choices[0].message.content
