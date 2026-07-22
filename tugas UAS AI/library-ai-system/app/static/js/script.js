document.addEventListener('DOMContentLoaded', () => {
    
    // -----------------------------------------------------
    // FITUR TANYA AI (Tampilan Chat Bubble Interaktif)
    // -----------------------------------------------------
    const aiForm = document.getElementById('ai-form');
    let isFirstMessage = true; // Penanda untuk membersihkan isi dummy HTML awal
    
    if (aiForm) {
        aiForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Ambil input teks dari user
            const queryInput = document.getElementById('ai-query');
            const userText = queryInput.value.trim();
            
            if (userText === "") return; // Jangan proses kalau input kosong

            const responseDiv = document.getElementById('ai-response');
            const welcomeState = document.getElementById('welcome-state');

            // 1. Sembunyikan teks sapaan saat chat pertama kali dimulai
            if (welcomeState) {
                welcomeState.style.display = 'none';
            }

            // 2. Tampilkan kontainer chat
            responseDiv.classList.remove('d-none');
            
            // Jika ini pesan pertama, bersihkan dummy HTML bawaan agar area chat bersih
            if (isFirstMessage) {
                responseDiv.innerHTML = '';
                isFirstMessage = false;
            }

            // 3. Tampilkan Bubble Chat User (Kanan)
            tampilkanPesanUser(userText);
            
            // 4. Kosongkan kolom input setelah dikirim
            queryInput.value = '';

            // 5. Tampilkan indikator Loading AI (Kiri)
            const loadingId = tampilkanLoadingAI();

            try {
                // 6. Kirim query ke Backend
                const res = await fetch('/ask-ai', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: userText })
                });
                
                const data = await res.json();
                
                // 7. Hapus indikator loading
                hapusElemen(loadingId);
                
                // 8. Bersihkan <think> & terjemahkan Markdown ke HTML
                let cleanResponse = data.response.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
                cleanResponse = cleanResponse.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
                cleanResponse = cleanResponse.replace(/\*([^*]+)\*/g, '<em>$1</em>');
                cleanResponse = cleanResponse.replace(/\n/g, '<br>');

                // 9. Tampilkan Bubble Chat AI (Kiri)
                tampilkanPesanAI(cleanResponse);
                
            } catch (err) {
                hapusElemen(loadingId);
                tampilkanPesanAI('<span class="text-danger">Gagal menghubungi asisten AI. Pastikan server backend sedang menyala.</span>');
            }
        });
    }

    // =========================================================
    // FUNGSI-FUNGSI BANTUAN UNTUK MEMBUAT TAMPILAN CHAT
    // =========================================================
    
    function tampilkanPesanUser(teks) {
        const container = document.getElementById('ai-response');
        // Bubble User (Warna Gradasi Cyan, Rata Kanan)
        const html = `
            <div class="d-flex justify-content-end mb-4">
                <div class="text-dark p-3 rounded-4 shadow-sm" style="background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); max-width: 80%;">
                    ${teks}
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', html);
        scrollToBottom();
    }

    function tampilkanPesanAI(teks) {
        const container = document.getElementById('ai-response');
        // Bubble AI (Warna Gelap, Rata Kiri, Pakai Ikon Robot)
        const html = `
            <div class="d-flex mb-4">
                <div class="me-3 flex-shrink-0">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fs-5 shadow-sm" style="width: 45px; height: 45px;">🤖</div>
                </div>
                <div class="p-3 rounded-4 shadow-sm w-100 border" style="background-color: #1e293b; border-color: rgba(196, 113, 237, 0.3) !important; color: #e2e8f0; line-height: 1.6;">
                    ${teks}
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', html);
        scrollToBottom();
    }

    function tampilkanLoadingAI() {
        const container = document.getElementById('ai-response');
        const id = 'loading-' + Date.now();
        // Bubble Loading (Mirip Bubble AI tapi isi animasi muter)
        const html = `
            <div id="${id}" class="d-flex mb-4">
                <div class="me-3 flex-shrink-0">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fs-5 shadow-sm" style="width: 45px; height: 45px;">🤖</div>
                </div>
                <div class="p-3 rounded-4 shadow-sm border d-flex align-items-center" style="background-color: #1e293b; border-color: rgba(196, 113, 237, 0.3) !important; width: fit-content;">
                    <div class="spinner-border spinner-border-sm text-info me-2" role="status"></div>
                    <span class="text-muted">AI sedang mengetik...</span>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', html);
        scrollToBottom();
        return id; // Return ID supaya elemennya bisa dihapus pas balasan AI datang
    }

    function hapusElemen(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // Auto-scroll ke pesan paling baru
    function scrollToBottom() {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
});