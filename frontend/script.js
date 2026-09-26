async function download() {
    const url = document.getElementById('urlInput').value.trim();
    const quality = document.querySelector('input[name="quality"]:checked').value;
    const enhance = document.getElementById('enhance').checked;
    const btn = document.getElementById('dlBtn');
    const status = document.getElementById('status');
    const result = document.getElementById('result');
    
    if (!url) { status.textContent = '⚠️ أدخل رابط'; return; }
    
    btn.disabled = true;
    status.textContent = '⏳ جاري التحميل...';
    result.innerHTML = '';
    
    try {
        const res = await fetch('http://localhost:8000/api/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url, quality, enhance})
        });
        const data = await res.json();
        
        if (!res.ok) throw new Error(data.detail || 'فشل التحميل');
        
        status.textContent = '✅ تم التحميل!';
        result.innerHTML = `
            <h3>${data.title || 'الملف جاهز'}</h3>
            <p>الجودة: ${data.resolution}p</p>
            <a href="http://localhost:8000${data.download_url}" download>⬇️ تحميل الملف</a>
        `;
    } catch (e) {
        status.textContent = '❌ ' + e.message;
    } finally {
        btn.disabled = false;
    }
}
