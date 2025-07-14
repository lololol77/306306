import streamlit as st
import requests
import uuid

# ✅ Firebase Realtime Database URL
FIREBASE_BASE = "https://project306-80096-default-rtdb.asia-southeast1.firebasedatabase.app"

# ----------------------------
# 💬 졸업 메시지 남기기
# ----------------------------
def message_input():
    st.header("💌 졸업 메시지 남기기")

    with st.form("message_form"):
        name = st.text_input("이름")
        number = st.text_input("번호 (0~23)")  # 0번 = 담임쌤
        message = st.text_area("하고 싶은 말")
        song = st.text_input("추천 노래 (링크 또는 제목)")

        if st.form_submit_button("저장하기"):
            if name and number and message:
                data = {
                    "name": name,
                    "number": number,
                    "message": message,
                    "song": song
                }
                response = requests.post(f"{FIREBASE_BASE}/messages.json", json=data)
                if response.status_code == 200:
                    st.success("✅ 저장 완료!")
                else:
                    st.error("❌ 저장 실패... 다시 시도해보세요.")
            else:
                st.warning("이름, 번호, 메시지를 모두 입력해주세요.")

# ----------------------------
# 💬 메시지 출력 공통
# ----------------------------
def show_entry(entry):
    st.subheader(f"{entry['number']}번 {entry['name']}")
    st.write(f"💬 {entry['message']}")
    if entry.get("song"):
        if "youtu" in entry["song"]:
            st.video(entry["song"])
        else:
            st.write(f"🎵 추천곡: {entry['song']}")
    st.markdown("---")

# ----------------------------
# 📋 전체 보기
# ----------------------------
def view_messages():
    st.header("📜 전체 친구들의 메시지 보기")
    response = requests.get(f"{FIREBASE_BASE}/messages.json")
    if response.status_code != 200 or not response.json():
        st.info("아직 메시지가 없어요.")
        return

    data = response.json()
    entries = sorted(data.values(), key=lambda x: int(x.get("number", 999)))

    for entry in entries:
        show_entry(entry)

# ----------------------------
# 🔍 번호별 보기
# ----------------------------
def view_by_number(selected_number):
    response = requests.get(f"{FIREBASE_BASE}/messages.json")
    if response.status_code != 200 or not response.json():
        st.info("메시지가 없어요.")
        return

    data = response.json()
    found = False
    for entry in data.values():
        if entry.get("number") == str(selected_number):
            st.header(f"🔍 {selected_number}번 메시지")
            show_entry(entry)
            found = True
            break

    if not found:
        st.warning(f"{selected_number}번 메시지가 아직 없어요.")

# ----------------------------
# 📊 앙케이트 블록 (1개)
# ----------------------------
def poll_block(question, label1, label2):
    st.markdown(f"### ❓ {question}")
    vote = st.radio(f"👉 선택해주세요: {label1} / {label2}", [f"1: {label1}", f"2: {label2}"], key=question)
    vote_number = vote.split(":")[0]
    comment = st.text_area(f"💬 의견 남기기 ({label1} vs {label2})", key=f"comment_{question}")
    submit = st.button(f"📝 제출하기 ({question})", key=f"submit_{question}")

    if submit:
        data = {
            "vote": vote_number,
            "comment": comment
        }
        url = f"{FIREBASE_BASE}/polls/{question}/responses/{uuid.uuid4()}.json"
        try:
            res = requests.put(url, json=data)
            if res.status_code == 200:
                st.success("✅ 의견이 제출되었습니다!")
            else:
                st.error("❌ 제출 실패: Firebase 오류")
        except Exception as e:
            st.error(f"❌ 네트워크 오류: {e}")

    # 결과 출력
    try:
        response = requests.get(f"{FIREBASE_BASE}/polls/{question}/responses.json")
        if response.status_code == 200 and response.json():
            entries = response.json().values()
            votes_1 = sum(1 for e in entries if e.get("vote") == "1")
            votes_2 = sum(1 for e in entries if e.get("vote") == "2")
            st.write(f"📈 {label1}: {votes_1}표 | {label2}: {votes_2}표")
            st.progress(votes_1 / (votes_1 + votes_2 + 1e-5))  # 0으로 나눔 방지

            st.markdown("**💬 친구들 의견**")
            for e in entries:
                if e.get("comment"):
                    st.write(f"👉 {e['comment']}")
        else:
            st.info("아직 투표가 없습니다.")
    except Exception as e:
        st.error(f"❌ Firebase 응답 오류: {e}")

# ----------------------------
# 📊 앙케이트 통합 페이지
# ----------------------------
def poll_page_combined():
    st.header("📊 앙케이트 참여하기")
    poll_block("연금복권 vs 로또", "연금복권", "로또")
    st.markdown("---")
    poll_block("평생 라면 금지 vs 평생 탄산 금지", "라면 못 먹기", "탄산 못 먹기")
    st.markdown("---")
    poll_block("1년 폭염 vs 1년 장마", "1년 내내 폭염", "1년 내내 장마")

# ----------------------------
# 🚀 Streamlit 앱 실행
# ----------------------------
st.set_page_config(page_title="졸업기념 웹사이트", page_icon="🎓")
st.title("🎓 우리 반 졸업기념 웹사이트")

menu_options = (
    ["💌 메시지 남기기", "📜 전체 보기"] +
    [f"{i}번 보기" for i in range(0, 24)] +
    ["📊 앙케이트 참여하기"]
)

menu = st.sidebar.selectbox("📋 메뉴를 선택하세요", menu_options)

if menu == "💌 메시지 남기기":
    message_input()
elif menu == "📜 전체 보기":
    view_messages()
elif menu == "📊 앙케이트 참여하기":
    poll_page_combined()
else:
    selected_number = int(menu.replace("번 보기", ""))
    view_by_number(selected_number)

