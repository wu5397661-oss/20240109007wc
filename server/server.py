import subprocess
import requests
import os
import sys
import platform
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# 根据操作系统自动选择 tesseract 路径
if platform.system() == "Windows":
    TESSERACT_EXE = r"D:\CM\Tess\tesseract.exe"
    TESSDATA_DIR = r"D:\CM\Tess\tessdata"
else:
    # Linux / 云服务器
    TESSERACT_EXE = "/usr/bin/tesseract"
    TESSDATA_DIR = "/usr/share/tesseract-ocr/5/tessdata"
    if not os.path.isdir(TESSDATA_DIR):
        # 尝试其他常见路径
        for p in ["/usr/share/tesseract-ocr/4.00/tessdata", "/usr/share/tessdata"]:
            if os.path.isdir(p):
                TESSDATA_DIR = p
                break

OLLAMA_URL = "http://localhost:11434/api/generate"
# 云服务器推荐使用较小的模型以加快速度
MODEL_NAME = "qwen2.5:3b-instruct-q4_K_M"


def get_subprocess_startupinfo():
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo
    return None


app = FastAPI(title="屏幕翻译 - 后端服务")


class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "eng"


@app.get("/")
def root():
    return {"service": "screen-translator-backend", "status": "ok"}


@app.get("/health")
def health():
    tesseract_ok = os.path.isfile(TESSERACT_EXE)
    tessdata_ok = os.path.isdir(TESSDATA_DIR)
    return {
        "tesseract": tesseract_ok,
        "tessdata": tessdata_ok,
        "ollama_url": OLLAMA_URL,
        "model": MODEL_NAME,
    }


@app.post("/ocr")
async def ocr_only(file: UploadFile = File(...)):
    if not os.path.isfile(TESSERACT_EXE):
        raise HTTPException(status_code=500, detail=f"tesseract.exe not found: {TESSERACT_EXE}")

    image_bytes = await file.read()
    temp_image = "_temp_ocr_upload.png"
    with open(temp_image, "wb") as f:
        f.write(image_bytes)

    try:
        cmd = [
            TESSERACT_EXE,
            temp_image,
            "stdout",
            "-l", "eng",
            "--tessdata-dir", TESSDATA_DIR,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, encoding="utf-8",
            startupinfo=get_subprocess_startupinfo(),
        )
        text = result.stdout.strip()
        return {"text": text}
    finally:
        if os.path.exists(temp_image):
            os.remove(temp_image)


@app.post("/translate")
async def translate_image(file: UploadFile = File(...)):
    if not os.path.isfile(TESSERACT_EXE):
        raise HTTPException(status_code=500, detail=f"tesseract.exe not found: {TESSERACT_EXE}")

    image_bytes = await file.read()
    temp_image = "_temp_translate_upload.png"
    with open(temp_image, "wb") as f:
        f.write(image_bytes)

    try:
        cmd = [
            TESSERACT_EXE,
            temp_image,
            "stdout",
            "-l", "eng",
            "--tessdata-dir", TESSDATA_DIR,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, encoding="utf-8",
            startupinfo=get_subprocess_startupinfo(),
        )
        text = result.stdout.strip()

        if not text:
            return {"source_text": "", "translation": "（未识别到文字）"}

        translation = translate_with_ollama(text)
        return {"source_text": text, "translation": translation}
    finally:
        if os.path.exists(temp_image):
            os.remove(temp_image)


@app.post("/translate-text")
def translate_text(req: TranslateRequest):
    if not req.text.strip():
        return {"translation": ""}
    return {"translation": translate_with_ollama(req.text)}


def translate_with_ollama(text: str) -> str:
    prompt = f"请将以下英文翻译成中文：\n\n{text}"
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.Timeout:
        return "翻译超时：模型推理时间过长，请尝试缩短识别的文字长度。"
    except requests.exceptions.ConnectionError:
        return "连接失败：无法连接到 Ollama，请确保 Ollama 服务正在运行！"
    except Exception as e:
        return f"翻译失败: {str(e)}\n请确保 Ollama 正在运行并且模型已安装。"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
