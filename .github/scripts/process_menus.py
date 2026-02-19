import os
import json
import requests
import time
import shutil  # ファイル移動用のライブラリを追加

# === 設定 ===
API_KEY = os.getenv('DIFY_API_KEY')
BASE_URL = 'https://api.dify.ai/v1'
IMAGE_FOLDER = 'menus'
PROCESSED_FOLDER = os.path.join(IMAGE_FOLDER, 'processed')  # 終了済みフォルダ
OUTPUT_FILE = 'catalog.json'

def process_images():
    if not API_KEY:
        print("Error: DIFY_API_KEY is not set.")
        return

    # 終了済みフォルダがなければ作成
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

    headers = {'Authorization': f'Bearer {API_KEY}'}
    
    # 既存データの読み込み
    catalog = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            try:
                catalog = json.load(f)
            except:
                catalog = []

    # 画像を1枚ずつ処理
    files_to_process = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files_to_process:
        print("No new images to process.")
        return

    for filename in files_to_process:
        print(f"Processing: {filename}...")
        file_path = os.path.join(IMAGE_FOLDER, filename)
        
        try:
            # 1. Difyへアップロード
            with open(file_path, 'rb') as f:
                upload_res = requests.post(f'{BASE_URL}/files/upload', headers=headers, files={'file': (filename, f, 'image/png')})
                file_id = upload_res.json().get('id')

            # 2. ワークフロー実行
            data = {
                "inputs": {"image": {"transfer_method": "local_file", "upload_file_id": file_id, "type": "image"}},
                "response_mode": "blocking",
                "user": "github-actions-bot"
            }
            run_res = requests.post(f'{BASE_URL}/workflows/run', headers=headers, json=data)
            raw_output = run_res.json().get('data', {}).get('outputs', {}).get('final_json', '[]')
            
            # JSON解析と結合
            clean_json = raw_output.replace('```json', '').replace('```', '').strip()
            new_items = json.loads(clean_json)
            catalog.extend(new_items)

            # === 【追加機能】解析が終わった画像を移動 ===
            dest_path = os.path.join(PROCESSED_FOLDER, filename)
            shutil.move(file_path, dest_path)
            print(f"Successfully moved {filename} to processed folder.")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
        
        time.sleep(1)

    # 最終的なJSONを保存
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_images()
