import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
from schema import InspectResult
from rules import decide

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    images: list[str]

def run_gemini_analysis(image_bytes_list: list[bytes]):
    api_key = os.getenv("GEMINI_API_KEY")
    api_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if not api_key:
        raise HTTPException(status_code=500, detail="找不到 GEMINI_API_KEY，請在 Render 的 Environment 設定")

    try:
        client = genai.Client(api_key=api_key)
        prompt = Path("prompt.txt").read_text(encoding="utf-8")
        image_names = ["desktop.jpg", "corner_1.jpg", "corner_2.jpg", "corner_3.jpg", "corner_4.jpg"]

        content = [prompt]
        for i, (name, img_bytes) in enumerate(zip(image_names, image_bytes_list), start=1):
            content.append(f"照片{i}:{name}")
            content.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))

        response = client.models.generate_content(
            model=api_model,
            contents=content,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InspectResult,
            ),
        )
        result = InspectResult.model_validate_json(response.text)
        data = result.model_dump()
        data["final_decision"] = decide(result)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini 分析錯誤: {str(e)}")

@app.post("/analyze")
def analyze_furniture(req: AnalyzeRequest):
    if len(req.images) != 5:
        raise HTTPException(status_code=400, detail="需要完整 5 張照片")

    image_bytes_list = []
    for b64_str in req.images:
        if not b64_str or not isinstance(b64_str, str):
            raise HTTPException(status_code=400, detail="有照片為空白，請重新拍攝或選取")
        if "," in b64_str:
            b64_str = b64_str.split(",", 1)[1]
        image_bytes_list.append(base64.b64decode(b64_str))

    return run_gemini_analysis(image_bytes_list)

@app.get("/analyze-test-images")
def analyze_test_images():
    image_names = ["desktop.jpg", "corner_1.jpg", "corner_2.jpg", "corner_3.jpg", "corner_4.jpg"]
    image_bytes_list = []
    images_b64 = []

    for name in image_names:
        img_path = Path("test/images") / name
        if not img_path.exists():
            img_path = Path(name)
        if not img_path.exists():
            raise HTTPException(status_code=404, detail=f"找不到測試圖片 {name}")
        raw = img_path.read_bytes()
        image_bytes_list.append(raw)
        images_b64.append("data:image/jpeg;base64," + base64.b64encode(raw).decode("utf-8"))

    result_data = run_gemini_analysis(image_bytes_list)
    result_data["preview_images"] = images_b64
    return result_data

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
