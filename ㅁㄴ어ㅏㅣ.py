import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import uuid

# ----------------------------
# Firebase 연결
# ----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://project306-80096-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# ----------------------------
# 메시지 입력 페이지
# ----------------------------
def message_input():
    st.header("💌 졸업 메시지와 추천곡 남기기")

    with st.form("message_form", clear_on_submit=True):
        name = st.text_input("이름")
        number = st.text_input("번호 (0~23)")  # ✅ 0번 포함
        message = st.text_area("하고 싶은 말")
        song = st.text_input("추천 노래 (제목 또는 유튜브 링크)")

        submitted = st.form_submit_button("저장하기")
        if submitted:
            if name and number and message:
                key = f"{number}_{name}"
                data = {
                    "name": name,
                    "number": number,
                    "message": message,
                    "song": song
                }

                ref = db.reference(f"/messages/{key}")
                ref.set(data)
                st.success("✅ 저장 완료! 친구들에게 보여질 거예요.")
            else:
                st.warning("이름, 번호, 메시지를 모두 입력해주세요.")

# ----------------------------
# 전체 메시지 보기
# ----------------------------
def view_messages():
    st.header("📜 전체 친구들의 메시지 보기")

    ref = db.reference("/messages")
    messages = ref.get()

    if not messages:
        st.info("아직 메시지가 없어요.")
        return

    sorted_keys = sorted(messages.keys(), key=lambda x: int(x.split('_')[0]))
    for key in sorted_keys:
        show_entry(messages[key])

# ----------------------------
# 번호별 메시지 보기
# ----------------------------
def view_by_number(selected_number):
    ref = db.reference("/messages")
    messages = ref.get()

    if not messages:
        st.info("메시지가 없어요.")
        return

    found = False
    for key, entry in messages.items():
        if entry.get("number") == str(selected_number):
            st.header(f"🔍 {selected_number}번 친구의 메시지")
            show_entry(entry)
            found = True
            break

    if not found:
        st.warning(f"{selected_number}번 메시지가 아직 없어요.")

# ----------------------------
# 메시지 출력 공통 함수
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
# Streamlit 앱 실행
# ----------------------------
st.set_page_config(page_title="졸업기념 웹사이트", page_icon="🎓")
st.title("🎓 우리 반 졸업기념 웹사이트")

# ✅ 0번 포함 메뉴 (0~23)
menu_options = ["💌 메시지 남기기", "📜 전체 보기"] + [f"{i}번 보기" for i in range(0, 24)]
menu = st.sidebar.selectbox("📋 메뉴를 선택하세요", menu_options)

if menu == "💌 메시지 남기기":
    message_input()
elif menu == "📜 전체 보기":
    view_messages()
else:
    selected_number = int(menu.replace("번 보기", ""))
    view_by_number(selected_number)
