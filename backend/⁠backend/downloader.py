import yt_dlp
import os
import asyncio
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

class VideoDownloader:
    def __init__(self):
        self.quality_map = {
            "4k": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "audio": "bestaudio/best"
        }
    
    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            pct = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A')
            print(f"⏳ {pct} | السرعة: {speed}")
    
    def download(self, url: str, quality: str = "4k", platform: str = "auto"):
        """تحميل فيديو بأعلى جودة"""
        output_template = str(DOWNLOAD_DIR / "%(title)s_%(height)sp.%(ext)s")
        
        ydl_opts = {
            'format': self.quality_map.get(quality, self.quality_map["4k"]),
            'outtmpl': output_template,
            'progress_hooks': [self._progress_hook],
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'quiet': False,
            'no_warnings': True,
            'concurrent_fragment_downloads': 8,  # تحميل سريع
            'retries': 10,
            'fragment_retries': 10,
            'buffersize': 1024 * 1024,
            'http_chunk_size': 10485760,  # 10MB chunks
        }
        
        # إعدادات خاصة لكل منصة
        if platform == "tiktok":
            ydl_opts['format'] = 'best'
            ydl_opts['no_watermark'] = True
        elif platform == "instagram":
            ydl_opts['format'] = 'best'
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # التحقق من الصيغة النهائية
                if not os.path.exists(filename):
                    filename = filename.rsplit('.', 1)[0] + '.mp4'
                return {
                    "success": True,
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "thumbnail": info.get('thumbnail'),
                    "file": filename,
                    "resolution": info.get('height', 'N/A')
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def download_image(self, url: str):
        """تحميل صورة بأعلى جودة"""
        import requests
        from PIL import Image
        from io import BytesIO
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, stream=True, timeout=30)
        r.raise_for_status()
        
        img = Image.open(BytesIO(r.content))
        filename = DOWNLOAD_DIR / f"img_{int(asyncio.get_event_loop().time())}.png"
        img.save(filename, "PNG", quality=100)
        
        return {"success": True, "file": str(filename), "size": img.size}


# دالة الاستخراج من روابط متعددة
async def extract_media(url: str, quality: str = "4k"):
    dl = VideoDownloader()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, dl.download, url, quality)
