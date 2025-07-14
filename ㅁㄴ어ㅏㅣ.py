import streamlit as st
import requests

# Firebase Realtime Database URL
FIREBASE_URL = "https://project306-80096-default-rtdb.asia-southeast1.firebasedatabase.app/messages.json"

# ----------------------------
# 메시지 입력
# ----------------------------
def message_input():
    st.header("💌 졸업 메시지 남기기")

    with st.form("message_form"):
        name = st.text_input("이름")
        number = st.text_input("번호 (0~23)")  # 0번은 담임쌤
        message = st.text_area("하고 싶은 말")
        song = st.text_input("추천 노래 (제목 또는 유튜브 링크)")

        if st.form_submit_button("저장하기"):
            if name and number and message:
                data = {
                    "name": name,
                    "number": number,
                    "message": message,
                    "song": song
                }
                response = requests.post(FIREBASE_URL, json=data)
                if response.status_code == 200:
                    st.success("✅ 저장 완료! 친구들과 함께 볼 수 있어요.")
                else:
                    st.error("❌ 저장 실패... 다시 시도해보세요.")
            else:
                st.warning("이름, 번호, 메시지는 꼭 입력해야 해요.")

# ----------------------------
# 출력 공통
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
# 전체 보기
# ----------------------------
def view_messages():
    st.header("📜 전체 친구들의 메시지 보기")

    response = requests.get(FIREBASE_URL)
    if response.status_code != 200 or not response.json():
        st.info("아직 메시지가 없어요.")
        return

    data = response.json()
    entries = sorted(data.values(), key=lambda x: int(x.get("number", 999)))

    for entry in entries:
        show_entry(entry)

# ----------------------------
# 번호별 보기
# ----------------------------
def view_by_number(selected_number):
    response = requests.get(FIREBASE_URL)
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
# Streamlit 실행
# ----------------------------
st.set_page_config(page_title="졸업기념 웹사이트", page_icon="🎓")
st.title("🎓 우리 반 졸업기념 웹사이트")

menu_options = ["💌 메시지 남기기", "📜 전체 보기"] + [f"{i}번 보기" for i in range(0, 24)]
menu = st.sidebar.selectbox("📋 메뉴를 선택하세요", menu_options)

if menu == "💌 메시지 남기기":
    message_input()
elif menu == "📜 전체 보기":
    view_messages()
else:
    selected_number = int(menu.replace("번 보기", ""))
    view_by_number(selected_number)
