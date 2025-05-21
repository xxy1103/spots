import os
import sys
import json
from werkzeug.utils import secure_filename
import random
from module.diary_class import diaryManager
from module.Spot_class import spotManager

with open("data\scenic_spots\spots.json", "r", encoding="utf-8") as f:
    spots_json = json.load(f)

spots = spots_json["spots"]

for spot in spots:
    sum_score = 0
    count = spot["reviews"]["total"]
    diarys_id = spot["reviews"]["diary_ids"]
    for diary_id in diarys_id:
        diary = diaryManager.getDiary(diary_id)
        if diary:
            sum_score += diary["scoreToSpot"]

        spot["score"] = round(sum_score / count, 1) if count > 0 else 0


with open("data\scenic_spots\spots.json", "w", encoding="utf-8") as f:
    json.dump(spots_json, f, ensure_ascii=False, indent=4)
        

           



    