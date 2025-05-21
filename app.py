import streamlit as st
import random
from collections import deque
from questions import QUESTIONS_IE, QUESTIONS_SN, QUESTIONS_TF, QUESTIONS_JP

# Deskripsi MBTI
MBTI_DESCRIPTIONS = {
    "INTJ": "INTJ (The Mastermind): Analitis, strategis, dan memiliki visi jangka panjang.",
    "INTP": "INTP (The Thinker): Logis, penuh rasa ingin tahu, dan senang mengeksplorasi ide.",
    "ENTJ": "ENTJ (The Commander): Pemimpin alami, tegas, dan berorientasi pada hasil.",
    "ENTP": "ENTP (The Visionary): Inovatif, suka tantangan, dan komunikatif.",
    "INFJ": "INFJ (The Advocate): Idealistik, empatik, dan memiliki kompas moral kuat.",
    "INFP": "INFP (The Mediator): Reflektif, kreatif, dan berorientasi pada nilai.",
    "ENFJ": "ENFJ (The Protagonist): Karismatik, suportif, dan mampu memimpin dengan empati.",
    "ENFP": "ENFP (The Campaigner): Antusias, imajinatif, dan fleksibel.",
    "ISTJ": "ISTJ (The Inspector): Teliti, bertanggung jawab, dan menghargai struktur.",
    "ISFJ": "ISFJ (The Defender): Setia, perhatian, dan suka membantu.",
    "ESTJ": "ESTJ (The Executive): Praktis, tegas, dan suka mengatur.",
    "ESFJ": "ESFJ (The Consul): Sosial, hangat, dan peduli terhadap kebutuhan orang lain.",
    "ISTP": "ISTP (The Virtuoso): Mandiri, logis, dan senang memecahkan masalah teknis.",
    "ISFP": "ISFP (The Adventurer): Sensitif, artistik, dan menyukai kebebasan.",
    "ESTP": "ESTP (The Dynamo): Energik, spontan, dan cepat bertindak.",
    "ESFP": "ESFP (The Entertainer): Ramah, ekspresif, dan menikmati momen.",
}

# Decision tree node class
class MBTINode:
    def __init__(self, dimension=None, trait=None):
        self.dimension = dimension  # 'IE', 'SN', etc.
        self.trait = trait          # 'I', 'E', etc.
        self.children = {}          # key: trait, value: MBTINode

# Build a 4-level tree: IE → SN → TF → JP
def build_mbti_tree():
    root = MBTINode("IE")
    for ie in ['I', 'E']:
        root.children[ie] = MBTINode("SN", ie)
        for sn in ['S', 'N']:
            root.children[ie].children[sn] = MBTINode("TF", sn)
            for tf in ['T', 'F']:
                root.children[ie].children[sn].children[tf] = MBTINode("JP", tf)
                for jp in ['J', 'P']:
                    root.children[ie].children[sn].children[tf].children[jp] = MBTINode(None, jp)
    return root

# Traverse decision tree like BFS and record path
def traverse_tree_bfs(traits_count):
    queue = deque()
    root = build_mbti_tree()
    queue.append((root, []))  # (node, path)
    path_taken = []

    while queue:
        node, path = queue.popleft()

        if node.dimension is None:
            return path_taken, "".join(path + [node.trait])

        # Determine dominant trait
        if node.dimension == "IE":
            choice = "I" if traits_count["I"] >= traits_count["E"] else "E"
        elif node.dimension == "SN":
            choice = "S" if traits_count["S"] >= traits_count["N"] else "N"
        elif node.dimension == "TF":
            choice = "T" if traits_count["T"] >= traits_count["F"] else "F"
        elif node.dimension == "JP":
            choice = "J" if traits_count["J"] >= traits_count["P"] else "P"
        else:
            choice = "?"

        path_taken.append((node.dimension, choice))
        queue.append((node.children[choice], path + [choice]))

    return path_taken, "????"

# App logic
def run_mbti_tree_app():
    st.title("🧠 Tes Kepribadian MBTI dengan Pohon Keputusan")

    name = st.text_input("Nama Anda")
    phone = st.text_input("Nomor HP (08xxxx)")
    num_questions = st.slider("Jumlah Soal", 16, 64, 32, step=4)

    if st.button("Mulai Tes"):
        if not name or not phone:
            st.warning("Mohon isi nama dan nomor HP terlebih dahulu.")
            return

        all_questions = QUESTIONS_IE + QUESTIONS_SN + QUESTIONS_TF + QUESTIONS_JP
        random.seed(1)
        random.shuffle(all_questions)
        questions = all_questions[:num_questions]

        st.session_state.questions = questions
        st.session_state.index = 0
        st.session_state.answers = []
        st.session_state.page = "test"
        st.session_state.name = name
        st.rerun()

    if st.session_state.get("page") == "test":
        questions = st.session_state.questions
        index = st.session_state.index

        if index < len(questions):
            q = questions[index]
            st.subheader(f"Soal {index+1}/{len(questions)}")
            st.write(q["text"])

            options = {
                "Sangat Tidak Setuju": -2,
                "Tidak Setuju": -1,
                "Netral": 0,
                "Setuju": 1,
                "Sangat Setuju": 2,
            }

            # Gunakan radio untuk memilih jawaban
            choice = st.radio("Pilih jawaban Anda:", list(options.keys()), key=f"answer_{index}")

            if st.button("Lanjutkan"):
                trait = q["trait"][0].lower()
                opp = {"i": "e", "e": "i", "s": "n", "n": "s", "t": "f", "f": "t", "j": "p", "p": "j"}

                score = options[choice]
                if score > 0:
                    st.session_state.answers.append((trait, score))
                elif score < 0:
                    st.session_state.answers.append((opp[trait], -score))
                else:
                    # Netral tidak menambah trait apa pun
                    pass

                st.session_state.index += 1

                # Jika sudah habis, pindah ke halaman hasil
                if st.session_state.index >= len(questions):
                    st.session_state.page = "result"

                st.rerun()

    if st.session_state.get("page") == "result":
        answers = st.session_state.answers
        traits = {"i": 0, "e": 0, "s": 0, "n": 0, "t": 0, "f": 0, "j": 0, "p": 0}

        for ans in answers:
            if ans is None:
                continue
            trait, score = ans
            traits[trait] += score

        # Karena tree pakai huruf kapital
        traits_upper = {k.upper(): v for k, v in traits.items()}

        path_taken, mbti = traverse_tree_bfs(traits_upper)

        st.success(f"{st.session_state.name}, hasil MBTI Anda adalah: **{mbti}**")
        
        # Tampilkan deskripsi lengkap
        st.subheader("📝 Deskripsi MBTI")
        desc = MBTI_DESCRIPTIONS.get(mbti, "Deskripsi tidak ditemukan.")
        st.info(desc)
        
        st.subheader("🔍 Jejak Keputusan Anda:")
        for dim, trait in path_taken:
            st.markdown(f"**{dim} → {trait}**")

# Run
if __name__ == "__main__":
    run_mbti_tree_app()
