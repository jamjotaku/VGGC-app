import os
import json
import requests
import time

# === 設定 ===
API_KEY = os.getenv('DIFY_API_KEY')
BASE_URL = 'https://api.dify.ai/v1'
IMAGE_FOLDER = 'menus'
OUTPUT_FILE = 'catalog.json'

def process_images():
    if not API_KEY:
        print("Error: DIFY_API_KEY is not set.")
        return

    headers = {'Authorization': f'Bearer {API_KEY}'}
    catalog = []

    # 既存のデータを読み込む（追記したい場合）
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            try:
                catalog = json.load(f)
            except:
                catalog = []

    for filename in os.listdir(IMAGE_FOLDER):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        print(f"Processing: {filename}...")
        file_path = os.path.join(IMAGE_FOLDER, filename)
        
        # 1. アップロード
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'image/png')}
            upload_res = requests.post(f'{BASE_URL}/files/upload', headers=headers, files=files)
            file_id = upload_res.json().get('id')

        # 2. 実行（変数名は image を想定）
        data = {
            "inputs": {"image": {"transfer_method": "local_file", "upload_file_id": file_id, "type": "image"}},
            "response_mode": "blocking",
            "user": "github-actions-bot"
        }
        
        run_res = requests.post(f'{BASE_URL}/workflows/run', headers=headers, json=data)
        res_json = run_res.json()
        
        # Outputノードの変数名を final_json としている場合
        raw_output = res_json.get('data', {}).get('outputs', {}).get('final_json', '[]')
        
        try:
            clean_json = raw_output.replace('```json', '').replace('```', '').strip()
            items = json.loads(clean_json)
            # 重複を避けるために既存データと結合（必要に応じて調整）
            catalog.extend(items)
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
        
        time.sleep(1) # API制限対策

    # 保存
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_images()