import streamlit as st
import random
import re
from collections import deque
from questions import QUESTIONS_IE, QUESTIONS_SN, QUESTIONS_TF, QUESTIONS_JP

# Deskripsi MBTI
MBTI_DESCRIPTIONS = {
    "INTJ": "INTJ (The Mastermind): Kamu adalah tipe yang suka berpikir mendalam dan strategis. Lebih nyaman sendiri karena di dalam kepalamu udah penuh rencana dan solusi. Kamu jago banget melihat pola, bikin strategi, dan menyelesaikan masalah rumit. Nggak suka basa-basi, kamu lebih suka hasil nyata. Karier ideal kamu: musisi, penasihat keuangan, marketing manager, fotografer.",
    "INTP": "INTP (The Thinker): Kamu adalah pemikir logis yang suka banget menganalisis segala hal. Otakmu jalan terus, selalu cari tahu kenapa sesuatu bisa terjadi. Kamu kreatif, imajinatif, dan sering punya ide-ide out of the box. Cocok banget kerja di bidang yang menantang intelektualmu. Karier ideal kamu: web developer, komposer, konsultan pemasaran, produser, penulis, dosen.",
    "ENTJ": "ENTJ (The Commander): Kamu lahir sebagai pemimpin. Kamu suka ngatur, merancang rencana, dan memastikan semuanya berjalan efisien. Tantangan adalah makanan harianmu, dan kamu nggak takut buat ambil tanggung jawab besar. Karier ideal kamu: administrator bisnis, manajer konstruksi, astronom.",
    "ENTP": "ENTP (The Visionary): Kamu itu penuh ide liar dan suka banget eksplor hal-hal baru. Logika jalan, tapi kamu juga senang diskusi yang seru dan menantang. Bosenan sama rutinitas, kamu butuh kerjaan yang fleksibel dan penuh tantangan intelektual. Karier ideal kamu: pengacara, system analyst, financial planner, ilmuwan.",
    "INFJ": "INFJ (The Advocate): Kamu tipe idealis dan pemikir yang dalam banget. Punya visi yang kuat dan sering berpikir soal gimana caranya bikin dunia jadi lebih baik. Kamu juga peka dan penuh empati. Karier ideal kamu: psikolog, konselor, penulis, ilmuwan.",
    "INFP": "INFP (The Mediator): Kamu pendiam tapi dunia dalam kepalamu penuh warna. Kamu suka merenung, punya nilai-nilai kuat, dan selalu ingin bikin perubahan positif. Kamu cocok di tempat yang tenang dan kreatif. Karier ideal kamu: fotografer, seniman, artis, profesional kesehatan mental, copywriter.",
    "ENFJ": "ENFJ (The Protagonist): Kamu punya kharisma alami dan selalu ingin bantu orang lain. Kamu suka terlibat dalam hubungan sosial dan bisa jadi inspirasi buat banyak orang. Energi kamu bikin lingkungan sekitarmu terasa hangat. Karier ideal kamu: HR, public relations, sales, art director.",
    "ENFP": "ENFP (The Campaigner): Kamu itu spontan, antusias, dan suka banget berekspresi. Kebebasan adalah hal yang kamu jaga banget. Kamu suka lingkungan yang dinamis dan penuh kreativitas. Karier ideal kamu: reporter, musisi, pekerja sosial, editor.",
    "ISTJ": "ISTJ (The Inspector): Kamu orangnya rapi, terorganisir, dan bisa diandalkan. Kamu suka sistem yang jelas dan kerja dengan aturan. Buat kamu, tanggung jawab itu bukan beban, tapi komitmen. Karier ideal kamu: dokter gigi, akuntan, business analyst, programmer.",
    "ISFJ": "ISFJ (The Defender): Kamu itu tipe yang perhatian banget sama orang lain. Kamu nggak suka konflik, lebih suka harmoni dan kerja di balik layar untuk bantu semuanya berjalan lancar. Karier ideal kamu: guru TK, research analyst, staf keuangan, manajer administrasi.",
    "ESTJ": "ESTJ (The Executive): Kamu tipe yang to the point dan suka segala sesuatu yang jelas. Kamu percaya sama sistem, tradisi, dan nilai-nilai yang kokoh. Pekerjaan yang butuh struktur dan kepemimpinan cocok banget buat kamu. Karier ideal kamu: hakim, coach, petugas keuangan.",
    "ESFJ": "ESFJ (The Consul): Kamu itu ramah, perhatian, dan suka banget membantu orang lain. Kamu senang saat semua orang di sekitarmu bahagia dan nyaman. Karier ideal kamu: kurator museum, medical researcher, pekerja sosial.",
    "ISTP": "ISTP (The Virtuoso): Kamu logis tapi juga spontan, suka tantangan teknis dan nyari solusi dari hal rumit. Kamu nggak suka banyak aturan, lebih senang kebebasan dan fleksibilitas. Karier ideal kamu: teknisi, insinyur, polisi, pekerja konstruksi, ahli forensik.",
    "ISFP": "ISFP (The Adventurer): Kamu hangat, lembut, dan punya jiwa seni yang tinggi. Kamu suka kebebasan buat berekspresi dan menikmati hal-hal baru. Nggak suka diatur, lebih suka ngikutin kata hati. Karier ideal kamu: manajer media sosial, arkeolog, pekerja sosial, desainer.",
    "ESTP": "ESTP (The Dynamo): Kamu penuh energi dan suka aksi. Kamu realistis, jago ambil keputusan cepat, dan senang ngadepin tantangan langsung. Dunia nyata adalah tempat bermainmu. Karier ideal kamu: sutradara, project coordinator, pengusaha.",
    "ESFP": "ESFP (The Entertainer): Kamu suka tampil, suka bersosialisasi, dan punya energi positif yang menular. Kamu senang jadi pusat perhatian dan berbagi kebahagiaan sama orang lain. Karier ideal kamu: event planner, tour guide, pramugari."
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
    st.title("🧠 Tes Kepribadian MBTI")

    name = st.text_input("Nama Kamu")
    phone = st.text_input("Nomor HP (08xxxx)")

    # Validasi format nomor telepon
    phone_valid = re.match(r'^08\d{8,11}$', phone) is not None

    if not phone_valid and phone:
        st.error("Nomor HP harus dimulai dengan '08' dan memiliki 10-13 digit angka.")

    num_questions = st.slider("Jumlah Soal", 16, 64, 32, step=4)

    if st.button("Mulai Tes"):
        if not name or not phone:
            st.warning("Mohon isi nama dan nomor HP terlebih dahulu.")
            return
        if not phone_valid:
            st.warning("Format nomor HP tidak valid. Harus dimulai dengan '08' dan berisi 10-13 digit.")
            return

        all_questions = QUESTIONS_IE + QUESTIONS_SN + QUESTIONS_TF + QUESTIONS_JP
        random.seed(1)
        random.shuffle(all_questions)
        per_dim = num_questions // 4
        questions = random.sample(QUESTIONS_IE, per_dim) + \
                    random.sample(QUESTIONS_SN, per_dim) + \
                    random.sample(QUESTIONS_TF, per_dim) + \
                    random.sample(QUESTIONS_JP, per_dim)
        random.shuffle(questions)  # Baru diacak seluruhnya

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

        st.success(f"{st.session_state.name}, hasil MBTI Kamu adalah: **{mbti}**")
        
        # Tampilkan deskripsi lengkap
        st.subheader("📝 Deskripsi MBTI")
        desc = MBTI_DESCRIPTIONS.get(mbti, "Deskripsi tidak ditemukan.")
        st.info(desc)
        
        trait_labels = {
            "I": "Introvert", "E": "Extrovert",
            "S": "Sensing", "N": "Intuition",
            "T": "Thinking", "F": "Feeling",
            "J": "Judging", "P": "Perceiving"
        }

        dimension_labels = {
            "IE": "Introvert (I) / Extrovert (E)",
            "SN": "Sensing (S) / Intuition (N)",
            "TF": "Thinking (T) / Feeling (F)",
            "JP": "Judging (J) / Perceiving (P)"
        }

        st.subheader("🔍 Jejak Keputusan Kamu:")
        for dim, trait in path_taken:
            full_trait = trait_labels.get(trait, trait)
            dim_label = dimension_labels.get(dim, dim)
            st.markdown(f"**{dim_label} → {full_trait}**")


# Run
if __name__ == "__main__":
    run_mbti_tree_app()
