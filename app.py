import streamlit as st
import random
from collections import deque
from questions import QUESTIONS_IE, QUESTIONS_SN, QUESTIONS_TF, QUESTIONS_JP

# Deskripsi MBTI
MBTI_DESCRIPTIONS = {
    "INTJ": "INTJ (The Mastermind): Pendiam, nyaman bekerja sendiri, dan sangat baik dalam memecahkan masalah. Mereka memiliki pemikiran strategis dan cenderung berpikir secara intuitif dan praktis. Karier ideal: musisi, penasihat keuangan, marketing manager, fotografer.",
    "INTP": "INTP (The Thinker): Sangat logis, suka pola, dan cepat memahami perbedaan. Kreatif dan fokus mencari solusi tepat. Karier ideal: web developer, komposer, konsultan pemasaran, produser, penulis, dosen.",
    "ENTJ": "ENTJ (The Commander): Pemimpin alami, fokus pada logika dan efisiensi. Mereka menyukai tantangan dan bertanggung jawab atas hasil. Karier ideal: administrator bisnis, manajer konstruksi, astronom.",
    "ENTP": "ENTP (The Visionary): Cerdas secara logis dan lebih tertarik pada ide besar daripada rutinitas. Menyukai pemecahan masalah dan pekerjaan konseptual. Karier ideal: pengacara, system analyst, financial planner, ilmuwan.",
    "INFJ": "INFJ (The Advocate): Seorang idealis dan pemikir mendalam yang dipenuhi ide dan imajinasi. Karier ideal: psikolog, konselor, penulis, ilmuwan.",
    "INFP": "INFP (The Mediator): Pendiam, suka menyendiri di tempat tenang, dan berorientasi pada pembelajaran serta perubahan dunia. Karier ideal: fotografer, seniman, artis, profesional kesehatan mental, copywriter.",
    "ENFJ": "ENFJ (The Protagonist): Ekstrovert yang idealis dan sangat etis. Mereka tahu cara berhubungan dengan orang lain dan ingin membuat dunia lebih baik. Karier ideal: HR, public relations, sales, art director.",
    "ENFP": "ENFP (The Campaigner): Individualis yang kreatif dan suka kebebasan berekspresi. Karier ideal: reporter, musisi, pekerja sosial, editor.",
    "ISTJ": "ISTJ (The Inspector): Pendiam, logis, dan nyaman bekerja sendiri atau dalam tim kecil. Menyukai struktur dan tanggung jawab. Karier ideal: dokter gigi, akuntan, business analyst, programmer.",
    "ISFJ": "ISFJ (The Defender): Baik hati, peka terhadap orang lain, dan menghargai keharmonisan. Karier ideal: guru TK, research analyst, staf keuangan, manajer administrasi.",
    "ESTJ": "ESTJ (The Executive): Terorganisir, jujur, dan percaya pada norma sosial. Karier ideal: hakim, coach, petugas keuangan.",
    "ESFJ": "ESFJ (The Consul): Supel dan suka berinteraksi dengan orang lain. Ingin membuat orang bahagia dan menciptakan tatanan sosial. Karier ideal: kurator museum, medical researcher, pekerja sosial.",
    "ISTP": "ISTP (The Virtuoso): Rasional dan logis, namun juga bisa spontan. Menyukai tugas teknis dan cepat mencari solusi. Karier ideal: teknisi, insinyur, polisi, pekerja konstruksi, ahli forensik.",
    "ISFP": "ISFP (The Adventurer): Terlihat hangat dan ramah, senang bereksplorasi dan menikmati pengalaman baru. Karier ideal: manajer media sosial, arkeolog, pekerja sosial, desainer.",
    "ESTP": "ESTP (The Dynamo): Energik, logis, dan suka kebebasan. Mereka menggunakan data untuk pengambilan keputusan. Karier ideal: sutradara, project coordinator, pengusaha.",
    "ESFP": "ESFP (The Entertainer): Suka berada di depan publik, hangat, dan senang berbagi pengetahuan. Karier ideal: event planner, tour guide, pramugari."
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
            return path_taken, "".join(path)

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
