import streamlit as st
import streamlit.components.v1 as components
import json
import os
import urllib.parse

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Đọc Sách Điện Tử Giọng Nói - Búp Sen Xanh (Toàn Văn)",
    page_icon="🪷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. TẢI DỮ LIỆU SÁCH TOÀN VĂN TỪ JSON HOẶC TỆP TẢI LÊN
# ---------------------------------------------------------
JSON_FILE_PATH = "bup_sen_xanh_full.json"

@st.cache_data
def load_default_book_data():
    if os.path.exists(JSON_FILE_PATH):
        try:
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Lỗi nạp dữ liệu: {e}")
            return {}
    return {}

BOOK_DATA = load_default_book_data()

# NẾU NGƯỜI DÙNG TẢI TỆP CUSTOM JSON/TXT TRÊN INTERFACE
st.sidebar.title("🪷 Búp Sen Xanh - Toàn Văn")
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Tải Lên Tệp Sách Đầy Đủ")
uploaded_file = st.sidebar.file_uploader(
    "Tải lên tệp sách cá nhân (.json hoặc .txt) để đọc 100% không cắt bớt:",
    type=["json", "txt"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".json"):
            BOOK_DATA = json.load(uploaded_file)
            st.sidebar.success(f"✅ Đã nạp tệp {uploaded_file.name} thành công ({len(BOOK_DATA)} phần)!")
        elif uploaded_file.name.endswith(".txt"):
            content_text = uploaded_file.read().decode("utf-8")
            BOOK_DATA = {
                "custom_full": {
                    "chapter": "Toàn Bộ Cuốn Sách",
                    "part": "Văn Bản Đầy Đủ Từ Tệp Tải Lên",
                    "title": uploaded_file.name,
                    "content": content_text
                }
            }
            st.sidebar.success(f"✅ Đã nạp toàn văn tệp TXT ({len(content_text)} ký tự)!")
    except Exception as e:
        st.sidebar.error(f"⚠️ Không thể đọc tệp: {e}")

# HÀM SINH MÃ QR DỰA TRÊN ĐƯỜNG DẪN WEB VÀ CHAPTER ID
def get_qr_code_url(chapter_id, custom_base_url=""):
    base_url = custom_base_url.strip() if custom_base_url.strip() else "https://bup-sen-xanh-reader.streamlit.app"
    qr_data = f"{base_url}?id={chapter_id}"
    encoded_data = urllib.parse.quote(qr_data)
    return f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={encoded_data}&color=0d5c3a"

# ---------------------------------------------------------
# 3. GIAO DIỆN CHÍNH & CHỨC NĂNG
# ---------------------------------------------------------
st.markdown("""
    <style>
    .main-header { text-align: center; color: #1b4d3e; font-size: 2.2rem; font-weight: bold; margin-bottom: 2px; }
    .sub-header { text-align: center; color: #3b7a57; font-size: 1.05rem; margin-bottom: 20px; }
    .content-card { 
        background-color: #f8fbf9; 
        border-left: 6px solid #2d8a4e; 
        padding: 25px; 
        border-radius: 8px; 
        font-size: 1.1rem; 
        line-height: 1.85; 
        color: #111; 
        max-height: 650px; 
        overflow-y: auto; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .chapter-tag { background-color: #e2f0d9; color: #1b4d3e; padding: 5px 14px; border-radius: 15px; font-weight: bold; font-size: 0.92rem; }
    .qr-card { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🪷 Web Đọc Sách Giọng Nói - Búp Sen Xanh (Toàn Văn 100%)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Đọc Đầy Đủ Không Tóm Tắt | Tích Hợp Mã QR & Điều Khiển Lật Trang Bằng Giọng Nói</div>', unsafe_allow_html=True)

app_mode = st.sidebar.radio("Chọn chức năng:", [
    "📖 Trình Đọc Toàn Văn & Phát Giọng Nói Tự Động",
    "📷 Quét Mã QR Mở Bài Đọc Chi Tiết",
    "🏷️ Quản Lý & Xuất Bộ Mã QR Cho Tất Cả Chương"
])

# ---------------------------------------------------------
# MỤC 1: TRÌNH ĐỌC TOÀN VĂN & PHÁT GIỌNG NÓI TỰ ĐỘNG
# ---------------------------------------------------------
if app_mode == "📖 Trình Đọc Toàn Văn & Phát Giọng Nói Tự Động":
    st.subheader("📖 Đọc Sách & Nghe Giọng Nói Tiếng Việt Chuẩn")
    
    if not BOOK_DATA:
        st.error("⚠️ Không tìm thấy dữ liệu sách. Vui lòng tải tệp `bup_sen_xanh_full.json` ở thanh menu bên trái.")
    else:
        chapter_map = {k: f"{v.get('chapter', '')} - {v.get('part', '')}: {v.get('title', '')}" for k, v in BOOK_DATA.items()}
        selected_id = st.selectbox(
            "Chọn Chương / Phần Muốn Đọc (Đầy Đủ 100% Nội Dung):", 
            list(chapter_map.keys()), 
            format_func=lambda x: chapter_map[x]
        )
        
        data = BOOK_DATA[selected_id]
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown(f"<span class='chapter-tag'>{data.get('chapter', 'Búp Sen Xanh')}</span>", unsafe_allow_html=True)
            st.markdown(f"### {data.get('title', '')}")
            st.caption(f"📍 {data.get('part', '')}")
            
            full_text = data.get("content", "")
            paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]
            formatted_html = "".join([f"<p style='margin-bottom: 14px;'>{p}</p>" for p in paragraphs])
            
            st.markdown(f'<div class="content-card">{formatted_html}</div>', unsafe_allow_html=True)
            st.caption(f"📊 Thống kê: **{len(full_text):,}** ký tự | **{len(paragraphs)}** đoạn văn (Toàn văn gốc không cắt bớt).")
            
        with col_right:
            st.markdown("### 🎙️ Trình Đọc Giọng Nói Chuẩn Tiếng Việt")
            st.info("💡 **Giải pháp chương dài**: Tự động chia nhỏ văn bản thành từng câu/đoạn và đọc nối tiếp liên tục, không bị giới hạn thời gian trình duyệt.")
            
            # Tốc độ đọc
            speech_rate = st.slider("⚡ Tốc độ đọc giọng nói:", min_value=0.7, max_value=1.5, value=0.95, step=0.05)
            
            # Chuẩn bị mảng các đoạn văn cho JS
            js_paragraphs = json.dumps(paragraphs, ensure_ascii=False)
            
            tts_html_template = """
            <div style="background-color: #f0f7f4; padding: 18px; border-radius: 12px; text-align: center; border: 1px solid #c8e6c9;">
                <div style="margin-bottom: 12px; display: flex; justify-content: center; gap: 8px;">
                    <button onclick="playFullText()" style="background-color: #2d8a4e; color: white; border: none; padding: 10px 16px; font-size: 15px; font-weight: bold; border-radius: 6px; cursor: pointer;">
                        ▶️ Đọc Toàn Văn
                    </button>
                    <button onclick="pauseSpeech()" style="background-color: #e69500; color: white; border: none; padding: 10px 14px; font-size: 15px; font-weight: bold; border-radius: 6px; cursor: pointer;">
                        ⏸️ Tạm Dừng
                    </button>
                    <button onclick="stopSpeech()" style="background-color: #c94c4c; color: white; border: none; padding: 10px 14px; font-size: 15px; font-weight: bold; border-radius: 6px; cursor: pointer;">
                        ⏹️ Dừng
                    </button>
                </div>
                
                <div style="background-color: #e0e0e0; border-radius: 10px; height: 12px; width: 100%; margin-bottom: 10px; overflow: hidden;">
                    <div id="progress-bar" style="background-color: #2d8a4e; height: 100%; width: 0%; transition: width 0.3s;"></div>
                </div>
                
                <div id="status" style="font-size: 13.5px; color: #222; font-weight: 500;">Sẵn sàng phát giọng nói...</div>
                
                <hr style="margin: 15px 0; border: 0; border-top: 1px solid #d0d0d0;">
                
                <button id="mic-btn" onclick="toggleRecognition()" style="background-color: #1b4d3e; color: white; border: none; padding: 10px 18px; font-size: 14px; font-weight: bold; border-radius: 20px; cursor: pointer; width: 100%;">
                    🎙️ Bật Nhận Diện Khẩu Lệnh Giọng Nói
                </button>
                <div id="speech-status" style="font-size: 12.5px; color: #555; margin-top: 8px;">Nói "tiếp tục", "quay lại", "đọc", "dừng" để điều khiển.</div>
            </div>

            <script>
            var synth = window.speechSynthesis;
            var paragraphs = __PARAGRAPHS__;
            var currentIndex = 0;
            var isPlaying = false;
            var rate = __RATE__;
            var recognition = null;
            var isListening = false;

            function playFullText() {
                if (!('speechSynthesis' in window)) {
                    alert('Trình duyệt không hỗ trợ đọc giọng nói Web Speech API.');
                    return;
                }
                if (synth.paused) {
                    synth.resume();
                    isPlaying = true;
                    document.getElementById('status').innerText = '🔊 Tiếp tục phát...';
                    return;
                }
                synth.cancel();
                currentIndex = 0;
                isPlaying = true;
                readCurrentParagraph();
            }

            function readCurrentParagraph() {
                if (!isPlaying || currentIndex >= paragraphs.length) {
                    if (currentIndex >= paragraphs.length) {
                        document.getElementById('status').innerText = '✅ Đã đọc xong 100% nội dung chương!';
                        document.getElementById('progress-bar').style.width = '100%';
                        isPlaying = false;
                    }
                    return;
                }

                var text = paragraphs[currentIndex];
                var utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'vi-VN';
                utterance.rate = rate;

                var percent = Math.round(((currentIndex + 1) / paragraphs.length) * 100);
                document.getElementById('progress-bar').style.width = percent + '%';
                document.getElementById('status').innerText = '🔊 Đang đọc đoạn ' + (currentIndex + 1) + '/' + paragraphs.length + ' (' + percent + '%)';

                utterance.onend = function() {
                    currentIndex++;
                    if (isPlaying) readCurrentParagraph();
                };

                utterance.onerror = function(e) {
                    console.error(e);
                    currentIndex++;
                    if (isPlaying) readCurrentParagraph();
                };

                synth.speak(utterance);
            }

            function pauseSpeech() {
                if (synth.speaking && !synth.paused) {
                    synth.pause();
                    document.getElementById('status').innerText = '⏸️ Đã tạm dừng giọng đọc.';
                }
            }

            function stopSpeech() {
                isPlaying = false;
                synth.cancel();
                currentIndex = 0;
                document.getElementById('progress-bar').style.width = '0%';
                document.getElementById('status').innerText = '⏹️ Đã dừng phát.';
            }

            // NHẬN DIỆN KHẨU LỆNH TIẾNG VIỆT
            function initRecognition() {
                var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {
                    alert('Trình duyệt không hỗ trợ nhận diện giọng nói qua Micro.');
                    return null;
                }
                var rec = new SpeechRecognition();
                rec.lang = 'vi-VN';
                rec.continuous = true;

                rec.onresult = function(event) {
                    var last = event.results.length - 1;
                    var cmd = event.results[last][0].transcript.trim().toLowerCase();
                    document.getElementById('speech-status').innerText = '🎙️ Đã nghe khẩu lệnh: "' + cmd + '"';

                    if (cmd.includes('đọc') || cmd.includes('phát') || cmd.includes('bắt đầu')) {
                        playFullText();
                    } else if (cmd.includes('dừng') || cmd.includes('tắt') || cmd.includes('ngừng')) {
                        stopSpeech();
                    } else if (cmd.includes('tạm dừng')) {
                        pauseSpeech();
                    }
                };

                rec.onerror = function(e) {
                    document.getElementById('speech-status').innerText = '⚠️ Lỗi Micro: ' + e.error;
                };

                return rec;
            }

            function toggleRecognition() {
                if (!recognition) recognition = initRecognition();
                if (!recognition) return;

                var btn = document.getElementById('mic-btn');
                if (isListening) {
                    isListening = false;
                    recognition.stop();
                    btn.innerText = '🎙️ Bật Nhận Diện Khẩu Lệnh Giọng Nói';
                    btn.style.backgroundColor = '#1b4d3e';
                    document.getElementById('speech-status').innerText = 'Micro đã tắt.';
                } else {
                    try {
                        recognition.start();
                        isListening = true;
                        btn.innerText = '🔴 Đang Lắng Nghe... (Bấm để tắt)';
                        btn.style.backgroundColor = '#c94c4c';
                        document.getElementById('speech-status').innerText = 'Đang lắng nghe khẩu lệnh tiếng Việt...';
                    } catch(e) {
                        console.error(e);
                    }
                }
            }
            </script>
            """
            
            final_tts_html = tts_html_template.replace("__PARAGRAPHS__", js_paragraphs).replace("__RATE__", str(speech_rate))
            components.html(final_tts_html, height=270)
            
            st.divider()
            st.markdown("#### 📱 Mã QR Đi Tới Chương Này")
            qr_img_url = get_qr_code_url(selected_id)
            st.image(qr_img_url, width=170, caption=f"Mã QR ID: {selected_id}")

# ---------------------------------------------------------
# MỤC 2: QUÉT MÃ QR MỞ BÀI ĐỌC CHI TIẾT
# ---------------------------------------------------------
elif app_mode == "📷 Quét Mã QR Mở Bài Đọc Chi Tiết":
    st.subheader("📷 Giả Lập / Quét Mã QR Mở Đúng Nội Dung Chương Sách")
    st.write("Nhập đường dẫn URL từ mã QR hoặc nhập trực tiếp mã ID chương sách (ví dụ: `c1_p1`, `c2_p1`, `c3_p5`) để tải toàn văn bài đọc:")
    
    user_qr_input = st.text_input(
        "Mã ID hoặc URL Quét Được từ Mã QR:", 
        value="c1_p1"
    )
    
    key = user_qr_input.split("id=")[-1] if "id=" in user_qr_input else user_qr_input.strip()
    
    if key in BOOK_DATA:
        item = BOOK_DATA[key]
        st.success(f"🎯 Đã tìm thấy bài đọc toàn văn cho mã ID: `{key}`")
        st.markdown(f"## {item.get('title', '')}")
        st.caption(f"📍 {item.get('chapter', '')} - {item.get('part', '')}")
        
        full_text = item.get("content", "")
        formatted_html = "".join([f"<p style='margin-bottom: 12px;'>{p}</p>" for p in full_text.split("\n") if p.strip()])
        st.markdown(f'<div class="content-card">{formatted_html}</div>', unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Chưa tìm thấy mã ID `{key}`. Danh sách ID hợp lệ hiện có trong CSDL: `{', '.join(list(BOOK_DATA.keys())[:10])}...`")

# ---------------------------------------------------------
# MỤC 3: QUẢN LÝ TẤT CẢ MÃ QR
# ---------------------------------------------------------
elif app_mode == "🏷️ Quản Lý & Xuất Bộ Mã QR Cho Tất Cả Chương":
    st.subheader("🏷️ Bộ Mã QR Chuẩn Cho Trọn Bộ 31 Phần Tác Phẩm Búp Sen Xanh")
    st.write("Bạn có thể cấu hình tên miền chính thức của web để bộ mã QR tạo ra dẫn trực tiếp tới ứng dụng thật của bạn:")
    
    custom_domain = st.text_input(
        "Nhập URL WebApp chính thức của bạn (Ví dụ: `https://ten-cua-ban.streamlit.app`):", 
        value="https://bup-sen-xanh-reader.streamlit.app"
    )
    
    st.caption("Danh sách mã QR in ấn dành cho 31 phần sách giấy:")
    
    cols = st.columns(3)
    for idx, (k, v) in enumerate(BOOK_DATA.items()):
        with cols[idx % 3]:
            qr_url = get_qr_code_url(k, custom_domain)
            st.markdown('<div class="qr-card">', unsafe_allow_html=True)
            st.markdown(f"**{v.get('part', k)}**")
            st.caption(v.get('title', ''))
            st.image(qr_url, width=150)
            st.code(f"ID: {k}")
            st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption("Ứng dụng Đọc Sách Điện Tử Giọng Nói & Quét Mã QR Toàn Văn | Tác phẩm Búp Sen Xanh (Sơn Tùng)")
