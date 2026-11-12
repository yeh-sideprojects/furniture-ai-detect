from pydantic import BaseModel,Field,ValidationError
from typing import Literal

class Dimension(BaseModel):
    score:int = Field(le=3,ge=0)
    note:str

class Defect(BaseModel):
    type:str
    location:str
    view:int = Field(le=5,ge=1)

class Dimensions(BaseModel):
    structure:Dimension
    surface_wear:Dimension
    water_damage:Dimension

class InspectResult(BaseModel):
    overall:Literal["pass","review","reject"]
    confidence:float=Field(le=1,ge=0)
    dimensions:Dimensions
    defects:list[Defect] #宣告defects這個屬性接收的資料一定要是串列並且此串列裡面每個值都要符合 Defect 這個類別的規定
    reason:str
    need_retake:bool
    retake_hint:str

# ========== 測試function ==========

def try_parse(model,json_text):
    try:
        d = model.model_validate_json(json_text)
        # print("succeed",d.model_dump())#這邊出來是dict
        print("succeed",d.model_dump_json(indent=2))#這邊出來直接是json
    except ValidationError as e:
        print(f"error:{e}")

# ========== 測試 ==========

# print("----- Dimension -----")
# try_parse(Dimension, '{"score": 1, "note": "桌面有輕微刮痕"}')
# try_parse(Dimension, '{"score": 5, "note": "桌面有輕微刮痕"}')
# try_parse(Dimension, '{"score": "很嚴重", "note": "桌面有輕微刮痕"}')

# print("----- Defect -----")
# try_parse(Defect, '{"type": "scratch", "location": "左前桌角", "view": 2}')
# try_parse(Defect, '{"type": "scratch", "location": "左前桌角", "view": "2"}')
# try_parse(Defect, '{"type": "scratch", "location": "左前桌角", "view": 2.5}')
# try_parse(Defect, '{"type": "scratch", "location": "左前桌角", "view": 0}')
# try_parse(Defect, '{"type": "scratch", "view": 2}')
good = '''
  {
    "overall": "review",
    "confidence": 0.85,
    "dimensions": {
      "structure":    {"score": 0, "note": "結構完整"},
      "surface_wear": {"score": 2, "note": "桌角有明顯磨損"},
      "water_damage": {"score": 0, "note": "沒有受潮跡象"}
    },
    "defects": [
      {"type": "scratch", "location": "左前桌角", "view": 2}
    ],
    "reason": "桌角磨損明顯，建議人工確認",
    "need_retake": false,
    "retake_hint": ""
  }
  '''

bad1 = '''
  {
    "overall": "ok",
    "confidence": 0.85,
    "dimensions": {
      "structure":    {"score": 0, "note": "結構完整"},
      "surface_wear": {"score": 2, "note": "桌角有明顯磨損"},
      "water_damage": {"score": 0, "note": "沒有受潮跡象"}
    },
    "defects": [
      {"type": "scratch", "location": "左前桌角", "view": 2}
    ],
    "reason": "桌角磨損明顯，建議人工確認",
    "need_retake": false,
    "retake_hint": ""
  }
  '''
bad2 = '''
  {
    "overall": "review",
    "confidence": 0.85,
    "dimensions": {
      "structure":    {"score": 0, "note": "結構完整"},
      "surface_wear": {"score": 2, "note": "桌角有明顯磨損"}
      
    },
    "defects": [
      {"type": "scratch", "location": "左前桌角", "view": 2}
    ],
    "reason": "桌角磨損明顯，建議人工確認",
    "need_retake": false,
    "retake_hint": ""
  }
  '''
bad3 = '''
  {
    "overall": "review",
    "confidence": 0.85,
    "dimensions": {
      "structure":    {"score": 0, "note": "結構完整"},
      "surface_wear": {"score": 2, "note": "桌角有明顯磨損"},
      "water_damage": {"score": 0, "note": "沒有受潮跡象"}
    },
    "defects": [
      {"type": "scratch", "location": "左前桌角", "view": 9}
    ],
    "reason": "桌角磨損明顯，建議人工確認",
    "need_retake": false,
    "retake_hint": ""
  }
  '''



if __name__ == "__main__":

  print("----- InspectResult -----")
  try_parse(InspectResult, good)
  try_parse(InspectResult, bad1)
  try_parse(InspectResult, bad2)
  try_parse(InspectResult, bad3)
 

