import streamlit as st
import firebase_admin
from firebase_admin import credentials, db, storage
import uuid

# ----------------------------
# Firebase 연결
# ----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")  # JSON 파일은 같은 폴더에 두기
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://project306-80096-default-rtdb.asia-southeast1.firebasedatabase.app/',
        'storageBucket': 'project306-80096.appspot.com'
    })

bucket = storage.bucket()

# ----------------------------
# 메시지 입력 페이지
# ----------------------------
def message_input():
    st.header("💌 졸업 메시지와 추천곡 남기기")

    with st.form("message_form", clear_on_submit=True):
        name = st.text_input("이름")
        number = st.text_input("번호 (1~23)")
        message = st.text_area("하고 싶은 말")
        song = st.text_input("추천 노래 (제목 또는 유튜브 링크)")
        photo = st.file_uploader("사진 업로드 (선택)", type=["jpg", "jpeg", "png"])

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

                if photo:
                    # 사진을 Firebase Storage에 업로드하고 URL 저장
                    blob = bucket.blob(f"photos/{key}_{uuid.uuid4()}.jpg")
                    blob.upload_from_file(photo, content_type=photo.type)
                    blob.make_public()
                    data["photo_url"] = blob.public_url

                # 메시지를 Firebase DB에 저장
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

    # 번호 순으로 정렬해서 출력
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
        st.warning(f"{selected_number}번 친구의 메시지가 아직 없어요.")

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
    
    if entry.get("photo_url"):
        st.image(entry["photo_url"], width=300)

    st.markdown("---")

# ----------------------------
# Streamlit 앱 실행
# ----------------------------
st.set_page_config(page_title="졸업기념 웹사이트", page_icon="🎓")

st.title("🎓 우리 반 졸업기념 웹사이트")

menu_options = ["💌 메시지 남기기", "📜 전체 보기"] + [f"{i}번 보기" for i in range(1, 24)]
menu = st.sidebar.selectbox("📋 메뉴를 선택하세요", menu_options)

if menu == "💌 메시지 남기기":
    message_input()
elif menu == "📜 전체 보기":
    view_messages()
else:
    selected_number = int(menu.replace("번 보기", ""))
    view_by_number(selected_number)
