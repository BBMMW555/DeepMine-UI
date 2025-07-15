import sys
from pathlib import Path

# إعداد مسار المشروع
PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

# استيراد مع التهيئة الصحيحة
from core_engine.speech_processing.text_to_speech import (
    FFMPEG_PATH,
    verify_ffmpeg
)

def test_ffmpeg_integration():
    print("\n=== FFmpeg Integration Test ===")
    print(f"FFmpeg Path: {FFMPEG_PATH}")
    
    # اختبار مباشر
    import subprocess
    try:
        result = subprocess.run(
            [str(FFMPEG_PATH), "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("\nFFmpeg Version Info:")
        print(result.stdout.split('\n')[0])
    except subprocess.CalledProcessError as e:
        print(f"\nError running FFmpeg: {e.stderr}")
        return False
    
    # اختبار تكامل pydub
    print("\nTesting pydub integration:")
    pydub_ok = verify_ffmpeg()
    print(f"Pydub configured correctly: {pydub_ok}")
    
    return pydub_ok

if __name__ == "__main__":
    test_ffmpeg_integration()