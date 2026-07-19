document.addEventListener('DOMContentLoaded', () => {
    const aiForm = document.getElementById('ai-form');
    
    if (aiForm) {
        aiForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('ai-query').value;
            const responseDiv = document.getElementById('ai-response');
            const responseText = document.getElementById('ai-text');
            const loading = document.getElementById('ai-loading');

            // Reset dan tampilkan loading
            responseDiv.classList.remove('d-none');
            responseText.innerHTML = '';
            loading.classList.remove('d-none');

            try {
                const res = await fetch('/ask-ai', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await res.json();
                
                loading.classList.add('d-none');
                // Mengubah newline menjadi <br> agar rapi di HTML
                responseText.innerHTML = data.response.replace(/\n/g, '<br>');
                
            } catch (err) {
                loading.classList.add('d-none');
                responseText.innerHTML = '<span class="text-danger">Gagal menghubungi asisten AI. Pastikan server Ollama sedang menyala.</span>';
            }
        });
    }
});