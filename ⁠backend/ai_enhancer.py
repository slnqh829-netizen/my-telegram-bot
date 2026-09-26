import cv2
import numpy as np
from PIL import Image, ImageEnhance

class AIEnhancer:
    """تحسين الجودة باستخدام تقنيات AI/كلاسيكية"""
    
    @staticmethod
    def upscale_image(input_path: str, output_path: str, scale: int = 4):
        """رفع دقة الصورة بـ Real-ESRGAN (بديل خفيف)"""
        img = cv2.imread(input_path)
        # استخدام Lanczos + sharpening كبديل سريع
        h, w = img.shape[:2]
        upscaled = cv2.resize(img, (w*scale, h*scale), 
                              interpolation=cv2.INTER_LANCZOS4)
        
        # Sharpen filter
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(upscaled, -1, kernel)
        
        cv2.imwrite(output_path, sharpened, 
                    [cv2.IMWRITE_JPEG_QUALITY, 100])
        return output_path
    
    @staticmethod
    def enhance_video(input_path: str, output_path: str):
        """تحسين إضاءة وتباين الفيديو"""
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # تحسين
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge((l, a, b))
            frame = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            out.write(frame)
        
        cap.release()
        out.release()
        return output_path
