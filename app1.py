import streamlit as st
import openai
from PIL import Image
import requests
import json
import os
from io import BytesIO
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔐 관리자 비밀번호 설정
ADMIN_PASSWORD = "0000"


# 페이지 설정
st.set_page_config(page_title="오름 건축사사무소", page_icon="🏛️", layout="wide")

# 세션 상태 초기화
# 상태 초기화
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Works"
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "ai_applications" not in st.session_state:
    st.session_state.ai_applications = []


# 🔍 URL 파라미터에서 관리자 여부 확인
query_params = st.query_params
is_admin_url = "admin" in query_params  # ?admin 이 존재하면 True

# 🔐 관리자 로그인 (URL로 접근 시에만 보임)
if is_admin_url and not st.session_state.admin_logged_in:
    st.title("🔐 관리자 로그인")
    pwd = st.text_input("관리자 비밀번호를 입력하세요:", type="password")
    if st.button("로그인"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("관리자 로그인 완료되었습니다.")
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# 프로젝트 선택 URL 파라미터 처리
selected_title = query_params.get("selected", [None])[0]
if selected_title:
    match = next((p for p in projects if p["title"] == selected_title), None)
    if match:
        st.session_state.selected_project_gallery = match
        st.rerun()

# 제목 출력
st.markdown("<h1 style='text-align:center;'>오름 건축사사무소</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>우리는 뛰어난 건축 설계와 감리를 제공합니다.</h3>", unsafe_allow_html=True)

# CSS 스타일 정의 (🔧 버튼 크기 문제 해결 포함)
st.markdown("""
<style>
    div[data-testid="column"] { display: flex; justify-content: center; }
    button { font-size: 16px !important; padding: 10px 16px !important; min-height: 40px !important; border-radius: 6px !important; }
    button > div { display: flex; justify-content: center; align-items: center; }
    div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button {
        width: 100% !important; font-size: 16px !important; padding: 10px 16px !important; min-height: 42px !important;
    }
    .active-tab { background-color: #4287f5 !important; color: white !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)



# 메뉴 탭 구성
tabs = ["About", "Works", "AI Architecture", "News", "Contact"]
if st.session_state.admin_logged_in:
    tabs.append("Admin")

cols = st.columns(len(tabs))
for i, tab in enumerate(tabs):
    with cols[i]:
        if st.button(tab, use_container_width=True, key=f"tab_button_{i}_{tab}"):
            previous_tab = st.session_state.current_tab
            st.session_state.current_tab = tab
            if tab == "Works":
                st.session_state.selected_project = None


# 선택된 탭 강조 JS
st.markdown(f"""
<script>
    const buttons = window.parent.document.querySelectorAll('button[data-testid="baseButton"]');
    buttons.forEach(btn => {{
        if (btn.innerText === "{st.session_state.current_tab}") {{
            btn.classList.add('active-tab');
        }}
    }});
</script>
""", unsafe_allow_html=True)

# 데이터 로딩
try:
    with open("projects.json", "r", encoding="utf-8") as f:
        projects = json.load(f)
except FileNotFoundError:
    projects = []

try:
    with open("news_data.json", "r", encoding="utf-8") as f:
        news_data = json.load(f)
except FileNotFoundError:
    news_data = []


# ----------------------------------------
# About 탭: 회사소개, 연혁, 멤버
# ----------------------------------------

if st.session_state.current_tab == "About":
    about_subtabs = st.tabs(["회사소개", "회사연혁", "회사멤버"])

    # 1. 회사 소개
    with about_subtabs[0]:
        st.image("로고파일.jpg", width=300)
        st.markdown("""
**오름 건축사사무소는**  
**2024년 6월에 시작한 젊은 건축사사무소입니다.**

비록 짧은 설립 역사이지만,  
우리는 건축설계를 시작으로  
건축법원감정과 전문건설(석공사)까지,  
건축 전반을 아우르는 실무를 경험하며  
하나의 건축물이 세상에 서기까지의 모든 흐름을  
직접 부딪히며 배워왔습니다.

이러한 실전 경험은 설계 도면 너머의 현실을 읽게 했고,  
건축주가 마주하는 수많은 의사결정의 순간마다  
더 실질적인 해답을 제시할 수 있는 기반이 되었습니다.  
좋은 경험을 통해 토지구매 단계에서부터 건축주와 함께 건강한 집짓기를 실천하고,  
축적된 데이터를 통한 합리적 건축설계를 통해 건축 전과정을 함께 하려 합니다.

**오름 건축사사무소**는  
디자인과 기능, 법적 타당성과 시공 현실성까지 함께 고민하며  
단순히 ‘도면을 그리는 회사’가 아닌  
‘건축 전 과정을 함께 고민하는 동반자’가 되고자 합니다.

**오름 건축사사무소**  
**홍성혁 대표 건축사 올림**
        """, unsafe_allow_html=True)

    # 2. 히스토리
    with about_subtabs[1]:
        st.image("로고파일.jpg", width=300)
        st.markdown("### 설립 이후 주요 연혁 (오름 건축사사무소)")
        st.markdown("""
- **2024년 6월**: 오름 건축사사무소 설립  
- **2024년 6월**: 구리시 아천동 소유권이전등기 및 손해배상 법원감정  
- **2024년 7월**: 서울 방이동 근린생활시설 리모델링 설계 감리  
- **2025년 2월**: 남양주 별내도서관 휴게실 개선설계  
- **2025년 2월**: 인천 송도수소충전소 설계  
- **2025년 4월**: 서울 강서공판장 전산화 설계  
- **2025년 6월**: 남양주 오남도서관 홀 개선설계
        """)

        st.markdown("### 설립 이전 주요 실무 프로젝트 (공동대표로 참여)")
        st.markdown("""
- **2021년~2024년**: 해체허가·신고 등 다수 수행  
- **2021년 09월**: 대한법무사협회 용도변경 (공동대표로 참여)  
- **2021년 09월**: 천안 교천리 단독주택 신축 (공동대표로 참여)  
- **2021년 10월**: 오산 수청동 단독주택 신축 (공동대표로 참여)  
- **2021년 11월**: 동두천 상패동 오피스텔 신축설계 (공동대표로 참여)  
- **2021년 12월**: 충남 논산 안심리 단독주택 신축 (공동대표로 참여)  
- **2022년 01월**: 경기도 광주 퇴촌 단독주택 신축 (공동대표로 참여)  
- **2022년 01월**: 부여군 북촌리 단독주택 신축 (공동대표로 참여)  
- **2022년 03월**: 제천시 옥전리 단독주택 신축 (공동대표로 참여)  
- **2022년 04월**: 양지리 공장 신축설계 (공동대표로 참여)  
- **2022년 09월**: 오남리 종교시설(교회) 증축설계 (공동대표로 참여)  
- **2022년 10월**: 도농고 공간기획설계 (공동대표로 참여)  
- **2023년 02월**: 다산동 신해센트럴타워 용도변경 (공동대표로 참여)  
- **2023년 03월**: 오남리 근생 감리 (공동대표로 참여)  
- **2023년 06월**: 화도근린공원 화장실 가설건축물 신고 (공동대표로 참여)  
- **2023년 06월**: 청평고등학교 외벽 및 창호 개선설계 (공동대표로 참여)  
- **2023년 07월**: 성수동 갤러리아포레 용도변경 (공동대표로 참여)  
- **2024년 01월**: 가평군 북면·현리 사택 개선공사설계 (공동대표로 참여)  
- **2024년 01월**: 용인 강남앤플러스 용도변경 (공동대표로 참여)  
- **2024년 03월**: 오남도서관 시설보수공사 (공동대표로 참여)  
- **2024년 03월**: 율석리 해체감리 (공동대표로 참여)  
- **2024년 06월**: 인천 계양구 작전동 용도변경 (공동대표로 참여)  
- **2024년 08월**: 호암초 외 1교(의정부서초) 화장실 및 옥상방수 개선설계 (공동대표로 참여)  
- **2024년 10월**: 내각리 부유식 건축물 제안 (공동대표로 참여)  
- **2024년 11월**: 메리츠 금융연구소 도면전산화 (공동대표로 참여)
        """)

    # 3. 멤버 소개
    with about_subtabs[2]:
        member_cols = st.columns(4)
        with about_subtabs[2]:
            member_cols = st.columns(4)

    # 1번 멤버: 홍성혁
    with member_cols[0]:
        st.image("프로필(남자).PNG", caption="Hong Sung Hyuk", width=400)
        st.markdown("**Hong Sung Hyuk**  \n*CEO, Principal Architect*")
        st.markdown("""
건축사(KIRA)  
대한건축사협회 정회원  
춘천지방법원 법원 감정인  

前 (주)가인건축사사무소  
前 서한건축사사무소 (감정)  
前 (주)메카피아 (석공사)  

現 오름 건축사사무소 대표
""")

    # 2번 멤버: 이보경
    with member_cols[1]:
        st.image("프로필(여자).PNG", caption="Lee Bo Kyoung", width=400)
        st.markdown("**Lee Bo Kyoung**  \n*Design Director*")
        st.markdown("""
공인중개사  
건축기사  

現 오름 건축사사무소 실장
""")

    # 3번 멤버: 빈자리
    with member_cols[2]:
        st.empty()

    # 4번 멤버: 빈자리
    with member_cols[3]:
        st.empty()



# 🔄 프로젝트 정보 불러오기
try:
    with open("projects.json", "r", encoding="utf-8") as f:
        projects = json.load(f)
except FileNotFoundError:
    projects = []



# Works 탭
from PIL import Image, ImageOps
import streamlit as st

if st.session_state.current_tab == "Works":
    selected_title = query_params.get("selected", [None])[0]
    if selected_title:
        match = next((p for p in projects if p["title"] == selected_title), None)
        if match:
            st.session_state.selected_project = match
            st.rerun()
    st.subheader("Works")

    if st.session_state.selected_project:
        project = st.session_state.selected_project
        st.markdown(f"### {project['title']}")

        # ✅ 대표 이미지 고정 크기로 출력 (project['image'] 사용)
        try:
            img = Image.open(project["image"])
            img = ImageOps.fit(img, (600, 600), method=Image.Resampling.LANCZOS)
            st.image(img, caption="대표 이미지", width=600)
        except:
            st.warning("대표 이미지를 불러올 수 없습니다.")

        # ✅ 상세 정보 출력
        st.markdown(f"""
        <div style='font-size: 14px; color: #333; padding-top: 20px; line-height: 1.8;'>
            <b>대지위치:</b> {project['location']}<br>
            <b>규모:</b> {project['scale']}<br>
            <b>용도:</b> {project['usage']}<br>
            <b>건폐율:</b> {project['coverage']}<br>
            <b>용적률:</b> {project['floor_ratio']}<br>
            <b>설명:</b> {project['desc']}
        </div>
        """, unsafe_allow_html=True)

        # ✅ 설명과 추가 이미지 사이 여백
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

        # ✅ 추가 이미지 3열 정렬
        if project["images"]:
            st.markdown("#### 📸 추가 이미지")
            for i in range(0, len(project["images"]), 3):
                cols = st.columns(3)
                for col, img_path in zip(cols, project["images"][i:i+3]):
                    with col:
                        try:
                            img = Image.open(img_path)
                            thumb = ImageOps.fit(img, (400, 400), method=Image.Resampling.LANCZOS)
                            col.image(thumb, caption="상세 이미지", use_container_width=True)
                        except:
                            col.warning(f"{img_path} 불러오기 실패")

        # ✅ 목록으로 돌아가기 버튼
        if st.button("← 목록으로 돌아가기"):
            st.session_state.selected_project = None
            st.rerun()

    else:
        categories = ["주거시설", "상업시설", "공공시설"]
        tabs = st.tabs(categories)

        for category, tab in zip(categories, tabs):
            with tab:
                filtered_projects = [p for p in projects if p["category"] == category]

                for i in range(0, len(filtered_projects), 4):
                    cols = st.columns(4)

                    for idx, (col, project) in enumerate(zip(cols, filtered_projects[i:i+4])):
                        with col:
                            unique_key = f"{category}_{project['title']}_{i}_{idx}"

                            try:
                                img = Image.open(project['image'])
                                fixed_size = (450, 450)
                                img = ImageOps.fit(img, fixed_size, method=Image.Resampling.LANCZOS)
                                st.image(img)
                            except Exception as e:
                                st.warning(f"이미지를 불러오는 데 문제가 발생했습니다: {e}")

                            st.markdown(f"<div style='text-align: center; font-weight: bold; margin-bottom: 5px;'>{project['title']}</div>", unsafe_allow_html=True)
                            st.markdown(f"""
                                <div style='font-size: 12px; color: #555; line-height: 1.6;'>
                                    <b>대지위치:</b> {project['location']}<br>
                                    <b>규모:</b> {project['scale']}<br>
                                    <b>용도:</b> {project['usage']}<br>
                                    <b>건폐율:</b> {project['coverage']}<br>
                                    <b>용적률:</b> {project['floor_ratio']}<br>
                                    <b>설명:</b> {project['desc']}
                                </div>
                            """, unsafe_allow_html=True)

                            with st.container():
                                st.markdown("""
                                    <style>
                                    div.stButton > button {
                                    width: 100%;
                                        height: 3em;
                                        font-size: 18px;
                                        border-radius: 8px;
                                    }
                                    </style>
                                """, unsafe_allow_html=True)
                                if st.button("상세보기", key=unique_key):
                                    st.session_state.selected_project = project
                                    st.rerun()



if st.session_state.get("current_tab") == "AI Architecture":
    st.subheader("AI Architecture")

    # 상태 초기화
    if "user_submitted" not in st.session_state:
        st.session_state.user_submitted = False

    if "ai_applications" not in st.session_state:
        st.session_state.ai_applications = []

    # 서브탭 구성
    ai_subtabs = st.tabs(["AI건축설계신청", "AI건축 Q&A", "AI 설계 예시 생성"])

    # -----------------------------------
    # 1. 신청 폼 탭
    # -----------------------------------
    with ai_subtabs[0]:
        st.markdown("<h3 style='text-align: center;'>AI 건축 설계 신청 </h3>", unsafe_allow_html=True)
        col = st.columns([1, 1.2, 1])[1]

        with col:
            name = st.text_input("성함")
            phone = st.text_input("연락처")
            email = st.text_input("이메일")
            land_owned = st.radio("토지를 보유하고 계신가요?", ("보유", "미보유"), horizontal=True)
            land_address = ""
            if land_owned == "보유":
                land_address = st.text_input("🏡 토지 주소를 입력하세요")
            scale = st.text_input("건축의 규모 (예: 30평, 100㎡ 등)")
            budget = st.text_input("예정 건축예산 (공사비/설계비 등)")
            requirements = st.text_area("설계 요구사항 또는 요청하고 싶은 사항")

            # 신청 버튼은 이 탭에서만 출력
            if st.button("신청 정보 제출"):
                if name and phone and email:
                    submission = {
                        "성함": name,
                        "연락처": phone,
                        "이메일": email,
                        "토지보유": land_owned,
                        "토지주소": land_address,
                        "규모": scale,
                        "예산": budget,
                        "요구사항": requirements,
                        "신청일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    try:
                        with open("ai_applications.json", "r", encoding="utf-8") as f:
                            data = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        data = []

                    data.append(submission)

                    with open("ai_applications.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    st.session_state.user_submitted = True
                    st.success("감사합니다. AI 건축 설계 신청 정보가 접수되었습니다.")
                else:
                    st.warning("성함, 연락처, 이메일은 필수 입력 항목입니다.")



    # -----------------------------------
    # 신청하지 않은 사용자는 아래 탭 접근 제한
    # -----------------------------------
    if not st.session_state.user_submitted:
        with ai_subtabs[1]:
            st.warning("⚠️ AI건축 Q&A는 AI건축 설계신청 제출 후 이용하실 수 있습니다.")
            st.info("""
                🏗️ **AI건축 설계신청 후에는 다음 기능들을 이용하실 수 있습니다.**

                - 📝 GPT-4 기반 건축 질의응답  
                - 📝 설계 키워드 기반 이미지 생성  
                - 📝 토지 정보 기반 AI 설계 제안 생성  
            """, icon="ℹ️")

        with ai_subtabs[2]:
            st.warning("⚠️ AI 설계 예시는 AI건축 설계신청 제출 후 이용하실 수 있습니다.")
            st.info("""
                🏗️ **AI건축 설계신청 후에는 다음 기능들을 이용하실 수 있습니다.**

                - 📝 GPT-4 기반 건축 질의응답  
                - 📝 설계 키워드 기반 이미지 생성  
                - 📝 토지 정보 기반 AI 설계 제안 생성  
            """, icon="ℹ️")
        st.stop()
    # -----------------------------------
    # 2. AI건축 Q&A
    # -----------------------------------
    with ai_subtabs[1]:
        st.markdown("### 💬 AI건축 Q&A (GPT-4)")
        question = st.text_area("건축 관련 질문을 입력하세요:")
        if st.button("질문하기", key="qna_button"):
            if question.strip():
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": question}],
                    max_tokens=300
                )
                st.success(response['choices'][0]['message']['content'].strip())

    # -----------------------------------
    # 3. AI 설계 예시 이미지 생성
    # -----------------------------------
    with ai_subtabs[2]:
        st.markdown("### 🏗️ AI 설계 예시 이미지 생성")
        keyword = st.text_input("설계 키워드 입력 (예: 모던 단독주택, 자연친화 도서관 등)")
        if keyword:
            try:
                prompt = f"architecture design {keyword} with floor plan and elevation"
                response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
                img_url = response['data'][0]['url']
                img = Image.open(BytesIO(requests.get(img_url).content))
                st.image(img, caption="AI 설계 예시", use_container_width=True)
            except Exception as e:
                st.error(f"이미지 생성 오류: {e}")


# -----------------------------------
# News 탭
# -----------------------------------
NEWS_DATA_FILE = "news_data.json"

# 뉴스 데이터 로드
if os.path.exists(NEWS_DATA_FILE):
    with open(NEWS_DATA_FILE, "r", encoding="utf-8") as f:
        news_data = json.load(f)
else:
    news_data = []

NEWS_CATEGORIES = [
    "OREUM NEWS",
    "OREUM VLOG",
    "건축일반상식",
    "건축공사관리",
    "부동산관련정보",
    "건축이모저모"
]

if st.session_state.current_tab == "News":
    st.markdown("## 📰 OREUM 뉴스")

    if "selected_post" not in st.session_state:
        st.session_state.selected_post = None

    tabs = st.tabs(NEWS_CATEGORIES)

    for category, tab in zip(NEWS_CATEGORIES, tabs):
        with tab:
            filtered_posts = [n for n in news_data if n.get("category") == category]

            # ✅ 상세 보기 화면일 경우
            if (
                st.session_state.selected_post is not None and
                st.session_state.selected_post.get("category") == category
            ):
                post = st.session_state.selected_post
                st.markdown(f"### 📰 {post['title']}")
                st.markdown(f"📅 {post['date']} &nbsp;&nbsp;&nbsp; 📂 {post['category']}", unsafe_allow_html=True)

                if post.get("thumbnail") and os.path.exists(post["thumbnail"]):
                    st.image(post["thumbnail"], width=300)

                st.markdown(post.get("content", ""), unsafe_allow_html=True)

                if st.button("🔙 목록으로 돌아가기", key=f"back_{category}"):
                    st.session_state.selected_post = None
                    st.rerun()

            # ✅ 목록 화면일 경우
            else:
                if not filtered_posts:
                    st.info("등록된 뉴스가 없습니다.")
                else:
                    cols = st.columns(6)
                    for idx, post in enumerate(reversed(filtered_posts)):
                        with cols[idx % 6]:
                            img_path = post.get("thumbnail", "로고파일.jpg")
                            if not os.path.exists(img_path):
                                img_path = "로고파일.jpg"
                            st.image(img_path, use_container_width=True)
                            st.markdown(
                                f"<div style='text-align:center; font-size:14px; margin-top:8px;'><b>{post['title'][:20]}</b><br><span style='font-size:12px; color:gray;'>{post['date']}</span></div>",
                                unsafe_allow_html=True
                            )
                            if st.button("글 내용보기", key=f"view_{category}_{idx}"):
                                st.session_state.selected_post = post
                                st.rerun()








# Contact 탭
if st.session_state.current_tab == "Contact":
    st.subheader("Contact")
    st.write("- 주소: 경기도 남양주시 다산순환로20 A동416호 (다산동, 현대프리미어캠퍼스)")
    st.write("- 전화: 031-566-8256")
    st.write("- 팩스: 031-566-8257")
    st.write("- 이메일: oreum0815@naver.com")
    st.markdown("""
<iframe
  src="https://www.google.com/maps?q=현대프리미어캠퍼스+남양주&z=18&output=embed"
  width="50%" height="600" style="border:0;" allowfullscreen loading="lazy">
</iframe>

""", unsafe_allow_html=True)



# ---------------------------------------
# ADMIN 탭 (3개 소탭: 워크 관리 / 게시판 관리 / 신청 관리)
# ---------------------------------------
if st.session_state.get("current_tab") == "Admin":
    st.markdown("## 🔐 관리자 페이지")
    admin_subtabs = st.tabs(["🏗️ 워크관리", "📝 News게시판관리", "📋 AI설계 신청관리"])

    # ---------------------------------------
    # 1. 워크 관리 탭
    # ---------------------------------------
    with admin_subtabs[0]:
        st.markdown("### 🏗️ 워크(프로젝트) 관리")
        col1, col2 = st.columns([1.3, 2])

        # 좌측: 등록/수정 폼
        with col1:
            st.markdown("#### 📁 새 프로젝트 등록/수정")
            edit_index = st.session_state.get("edit_project_index", -1)
            edit_mode = (edit_index >= 0 and edit_index < len(projects))
            project_to_edit = projects[edit_index] if edit_mode else {}

            with st.form("project_form"):
                title = st.text_input("제목", value=project_to_edit.get("title", ""))
                category = st.selectbox("카테고리", ["주거시설", "상업시설", "공공시설"],
                                        index=["주거시설", "상업시설", "공공시설"].index(project_to_edit.get("category", "주거시설")))
                location = st.text_input("위치", value=project_to_edit.get("location", ""))
                scale = st.text_input("규모", value=project_to_edit.get("scale", ""))
                usage = st.text_input("용도", value=project_to_edit.get("usage", ""))
                coverage = st.text_input("건폐율", value=project_to_edit.get("coverage", ""))
                floor_ratio = st.text_input("용적률", value=project_to_edit.get("floor_ratio", ""))
                desc = st.text_area("설명", value=project_to_edit.get("desc", ""))
                thumb_file = st.file_uploader("대표 이미지 (선택)", type=["jpg", "png"])
                detail_files = st.file_uploader("상세 이미지 (여러 개 가능)", accept_multiple_files=True)
                submitted = st.form_submit_button("저장")

                if submitted:
                    if title:
                        os.makedirs("project_images", exist_ok=True)
                        thumb_path = os.path.join("project_images", thumb_file.name) if thumb_file else project_to_edit.get("image", "")
                        if thumb_file:
                            with open(thumb_path, "wb") as f:
                                f.write(thumb_file.getbuffer())
                        detail_paths = []
                        if detail_files:
                            for file in detail_files:
                                file_path = os.path.join("project_images", file.name)
                                with open(file_path, "wb") as f:
                                    f.write(file.getbuffer())
                                detail_paths.append(file_path)
                        else:
                            detail_paths = project_to_edit.get("images", [])

                        new_project = {
                            "title": title,
                            "category": category,
                            "location": location,
                            "scale": scale,
                            "usage": usage,
                            "coverage": coverage,
                            "floor_ratio": floor_ratio,
                            "desc": desc,
                            "image": thumb_path,
                            "images": detail_paths
                        }

                        if edit_mode:
                            projects[edit_index] = new_project
                            st.success("수정 완료")
                        else:
                            projects.append(new_project)
                            st.success("등록 완료")

                        with open("projects.json", "w", encoding="utf-8") as f:
                            json.dump(projects, f, ensure_ascii=False, indent=2)
                        st.session_state.edit_project_index = -1
                        st.rerun()
                    else:
                        st.warning("제목은 필수입니다.")

        # 우측: 목록 (카테고리별 탭 + 페이지네이션)
        with col2:
            st.markdown("#### 📅 프로젝트 목록")
            category_tabs = st.tabs(["주거시설", "상업시설", "공공시설"])
            category_names = ["주거시설", "상업시설", "공공시설"]

            for cat_name, tab in zip(category_names, category_tabs):
                with tab:
                    filtered_projects = [p for p in projects if p.get("category") == cat_name]
                    projects_per_page = 20
                    total_projects = len(filtered_projects)
                    total_pages = (total_projects - 1) // projects_per_page + 1 if total_projects > 0 else 1
                    page = st.session_state.get(f"{cat_name}_page", 1)
                    page_buttons = st.columns(total_pages)
                    for i in range(total_pages):
                        with page_buttons[i]:
                            if i + 1 == page:
                                st.markdown(f"""
                                    <div style='background-color:#204066; color:white; padding:8px 16px; border-radius:6px; text-align:center;'>
                                        <b>{i+1}</b>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                if st.button(f"{i+1}", key=f"{cat_name}_page_btn_{i+1}"):
                                    st.session_state[f"{cat_name}_page"] = i + 1
                                    st.rerun()
                    start = (page - 1) * projects_per_page
                    end = start + projects_per_page
                    paged_projects = filtered_projects[start:end]

                    for idx, proj in enumerate(paged_projects, start=start + 1):
                        cols = st.columns([1, 2, 2, 2, 0.8, 0.8])
                        cols[0].markdown(f"**{idx}**")
                        cols[1].markdown(f"**{proj['title']}**")
                        cols[2].write(proj["category"])
                        cols[3].write(proj["location"])

                        if cols[4].button("✏", key=f"edit_{cat_name}_{idx}"):
                            real_index = projects.index(proj)
                            st.session_state.edit_project_index = real_index
                            st.rerun()

                        if cols[5].button("❌", key=f"delete_{cat_name}_{idx}"):
                            real_index = projects.index(proj)
                            del projects[real_index]
                            with open("projects.json", "w", encoding="utf-8") as f:
                                json.dump(projects, f, ensure_ascii=False, indent=2)
                            st.success(f"{proj['title']} 삭제됨")
                            st.rerun()



# ---------------------------------------
# 2. 뉴스 게시판 관리 탭
# ---------------------------------------
    with admin_subtabs[1]:
        st.markdown("### 📰 뉴스 게시판 관리")
        col1, col2 = st.columns([1.3, 2])

    # 좌측: 작성/수정
    with col1:
        st.markdown("#### ✏️ 게시글 작성/수정")

        edit_index = st.session_state.get("edit_news_index", -1)
        edit_mode = 0 <= edit_index < len(news_data)
        post = news_data[edit_index] if edit_mode else {}

        selected_category = st.selectbox("카테고리 선택", NEWS_CATEGORIES, index=NEWS_CATEGORIES.index(post.get("category", NEWS_CATEGORIES[0])))

        title = st.text_input("제목", value=post.get("title", ""))
        # ✅ 세션 값 우선 적용
        content = st.session_state.get(f"content_inserted_{selected_category}", post.get("content", ""))
        content = st.text_area("본문 (마크다운 + 이미지 지원)", value=content, height=300)

        thumbnail_file = st.file_uploader("썸네일 이미지", type=["jpg", "png"])

        st.markdown("##### 📸 본문 이미지 업로드 및 삽입")
        detail_images = st.file_uploader("본문용 이미지 업로드", type=["jpg", "png"], accept_multiple_files=True, key="body_images")

        image_folder = "news_images"
        os.makedirs(image_folder, exist_ok=True)

        for img_file in detail_images:
            img_path = os.path.join(image_folder, img_file.name)
            with open(img_path, "wb") as f:
                f.write(img_file.getbuffer())

            if st.button(f"🖼 본문에 삽입: {img_file.name}", key=f"insert_{img_file.name}_{selected_category}"):
                current = content
                md_line = f"\n\n![{img_file.name}]({img_path})\n\n"
                st.session_state[f"content_inserted_{selected_category}"] = current + md_line
                st.rerun()

        # ✅ 최종 저장할 본문
        final_content = st.session_state.get(f"content_inserted_{selected_category}") or content

        if st.button("작성 완료"):
            if not title or not final_content:
                st.warning("제목과 본문은 필수 항목입니다.")
            else:
                thumb_path = post.get("thumbnail", "로고파일.jpg")
                if thumbnail_file:
                    thumb_path = os.path.join(image_folder, thumbnail_file.name)
                    with open(thumb_path, "wb") as f:
                        f.write(thumbnail_file.getbuffer())

                new_post = {
                    "category": selected_category,
                    "title": title,
                    "content": final_content,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "thumbnail": thumb_path
                }

                

                if edit_mode:
                    news_data[edit_index] = new_post
                    st.success("게시글이 수정되었습니다.")
                else:
                    news_data.append(new_post)
                    st.success("게시글이 등록되었습니다.")

                with open(NEWS_DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(news_data, f, ensure_ascii=False, indent=2)

                st.session_state.edit_news_index = -1
                st.session_state[f"content_inserted_{selected_category}"] = ""
                st.rerun()

    # 우측: 카테고리별 게시글 목록
    with col2:
        with col2:
            st.markdown("#### 📋 게시글 목록")
            news_tabs = st.tabs(NEWS_CATEGORIES)

        for cat, tab in zip(NEWS_CATEGORIES, news_tabs):
            with tab:
                filtered_posts = [n for n in news_data if n["category"] == cat]

                if not filtered_posts:
                    st.info("게시글이 없습니다.")
                else:
                    for idx, post in enumerate(reversed(filtered_posts)):
                        post_index = news_data.index(post)
                        cols = st.columns([4, 1, 1])
                        cols[0].markdown(f"**{post['title']}** ({post['date']})")

                        if cols[1].button("✏ 수정", key=f"edit_{cat}_{idx}"):
                            st.session_state.edit_news_index = post_index
                            st.session_state[f"content_inserted_{cat}"] = post["content"]
                            st.rerun()

                        if cols[2].button("❌ 삭제", key=f"delete_{cat}_{idx}"):
                            del news_data[post_index]
                            with open(NEWS_DATA_FILE, "w", encoding="utf-8") as f:
                                json.dump(news_data, f, ensure_ascii=False, indent=2)
                            st.success("삭제되었습니다.")
                            st.rerun()




    # ---------------------------------------
    # 3. AI 설계 신청 관리 탭
    # ---------------------------------------
    with admin_subtabs[2]:
        st.markdown("### 📋 AI 설계 신청 내역")

        data_path = "ai_applications.json"
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                try:
                    applications = json.load(f)
                except json.JSONDecodeError:
                    applications = []
        else:
            applications = []

        if not applications:
            st.info("신청된 내역이 없습니다.")
        else:
            for i, app in enumerate(applications):
                with st.container():
                    st.markdown(f"""
                    **신청자 {i+1}**
                    - 성함: {app["성함"]}
                    - 연락처: {app["연락처"]}
                    - 이메일: {app["이메일"]}
                    - 토지 보유: {app["토지보유"]}
                    - 토지 주소: {app.get("토지주소", "미입력")}
                    - 건축 규모: {app["규모"]}
                    - 예정예산: {app["예산"]}
                    - 설계 요구사항: {app["요구사항"]}
                    """)
                    if st.button(f"❌ 신청자 {i+1} 삭제", key=f"delete_app_{i}"):
                        del applications[i]
                        with open(data_path, "w", encoding="utf-8") as f:
                            json.dump(applications, f, ensure_ascii=False, indent=4)
                        st.success("신청 정보가 삭제되었습니다.")
                        st.rerun()




    # ---------------------------------------
    # 공통 푸터 (저작권 및 연락처)
    # ---------------------------------------
st.markdown("""
<hr>
<div style='text-align: center; font-size: 0.95em;'>
    <strong>오름 건축사사무소</strong><br>
    오름이 제공하는 건축은 바르고 건강합니다.<br><br>
    (T) 031-566-8256 / (F) 031-566-8257<br>
    oreum0815@naver.com<br><br>
    <span style='color: gray;'>ⓒ 2024 Oreum Architects. All rights reserved.<br>
    Designed by Oreum Architects.</span>
</div>
""", unsafe_allow_html=True)