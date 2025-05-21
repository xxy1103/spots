import os
import sys
import json
from werkzeug.utils import secure_filename


path = "data/scenic_spots"
with open("data/diaries/diaries.json", "r", encoding="utf-8") as f:
    diaries_json = json.load(f)

diaries = diaries_json["diaries"]
for diary in diaries:
    spot_id = diary["spot_id"]
    os.makedirs(os.path.join(path, f"spot_{spot_id}", "images"), exist_ok=True)
    os.makedirs(os.path.join(path, f"spot_{spot_id}", "videos"), exist_ok=True)
    img_list = diary["img_list"]
    new_img_list = []
    for img in img_list:
        try:
            with open(img, "rb") as f:
                img_data = f.read()
            img_name = secure_filename(os.path.basename(img))
            with open(os.path.join(path, f"spot_{spot_id}", "images", img_name), "wb") as img_f:
                img_f.write(img_data)
            new_img_list.append(path + f"spot_{spot_id}/images/{img_name}")
        except Exception as e:
            print(f"Error processing image {img}: {e}")
            continue
        diary["img_list"] = new_img_list

with open("data/diaries/diaries.json", "w", encoding="utf-8") as f:
    json.dump(diaries_json, f, ensure_ascii=False, indent=4)


    
# for i in os.listdir(path):
#     current_path = os.path.join(path, i)
#     if os.path.isdir(current_path):
#         spots_Id = i.split("_")[1]
#         spots_Id = int(spots_Id)
#         reviews_path = os.path.join(current_path, "reviews")
#         if os.path.isdir(reviews_path):
#            images_path = os.path.join(current_path, "images")
#            videos_path = os.path.join(current_path, "videos")
#            os.makedirs(images_path, exist_ok=True)
#            os.makedirs(videos_path, exist_ok=True)
           



    