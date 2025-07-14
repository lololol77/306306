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
        res = requests.put(url, json=data)
        if res.status_code == 200:
            st.success("✅ 의견이 제출되었습니다!")

    # 결과 출력
    response = requests.get(f"{FIREBASE_BASE}/polls/{question}/responses.json")
    if response.status_code == 200 and response.json():
        entries = response.json().values()
        votes_1 = sum(1 for e in entries if e.get("vote") == "1")
        votes_2 = sum(1 for e in entries if e.get("vote") == "2")
        st.write(f"📈 {label1}: {votes_1}표 | {label2}: {votes_2}표")
        st.progress(votes_1 / (votes_1 + votes_2 + 1e-5))  # 간단한 비율 막대

        st.markdown("**💬 친구들 의견**")
        for e in entries:
            if e.get("comment"):
                st.write(f"👉 {e['comment']}")
    else:
        st.info("아직 투표가 없습니다.")

def poll_page_combined():
    st.header("📊 앙케이트 참여하기")

    poll_block("연금복권 vs 로또", "연금복권", "로또")
    st.markdown("---")
    poll_block("평생 라면 금지 vs 평생 탄산 금지", "라면 못 먹기", "탄산 못 먹기")
    st.markdown("---")
    poll_block("1년 폭염 vs 1년 장마", "1년 내내 폭염", "1년 내내 장마")

