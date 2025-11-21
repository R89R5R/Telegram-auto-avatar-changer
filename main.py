import asyncio
import os
import shutil
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from PIL import Image
import imghdr
import random 

api_id = your api id 
api_hash = 'your api hsah' #https://my.telegram.org/apps
phone_number = 'your phone number'

source_folder = 'source'
processed_folder = 'processed'
error_folder = 'error'

for folder in [processed_folder, error_folder]:
    os.makedirs(folder, exist_ok=True)

def prepare_image_for_telegram(file_path):
    try:
        with Image.open(file_path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
              
            max_size = 800
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            prepared_path = file_path + ".prepared.jpg"
            img.save(prepared_path, "JPEG", quality=90, optimize=True)
            
            return prepared_path
            
    except Exception as e:
        print(f"Ошибка подготовки изображения: {e}")
        return None

async def change_avatar_simple():
    client = TelegramClient('avatar_session', api_id, api_hash)
    await client.start(phone=phone_number)
    
    print("=== Avatar Changer Started ===")
    print(f"Source: {source_folder}")
    print(f"Processed: {processed_folder}")
    print(f"Errors: {error_folder}")
    print("=" * 30)

    processed_count = 0
    error_count = 0

    while True:
        avatar_files = [f for f in os.listdir(source_folder) 
                       if os.path.isfile(os.path.join(source_folder, f))]
        
        if not avatar_files:
            print("\n=== Все аватарки обработаны! ===")
            break

        current_file = avatar_files[0]
        source_path = os.path.join(source_folder, current_file)
        
        if current_file.endswith('.prepared.jpg'):
            os.remove(source_path)
            continue
        
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Обрабатываю: {current_file}")
            
            prepared_path = prepare_image_for_telegram(source_path)
            if not prepared_path:
                raise Exception("Не удалось подготовить изображение")
            
            print("Загружаю в Telegram...")
            
            uploaded_file = await client.upload_file(prepared_path)
            
            await client(UploadProfilePhotoRequest(file=uploaded_file))
            
            os.remove(prepared_path)
            
            destination_path = os.path.join(processed_folder, current_file)
            shutil.move(source_path, destination_path)
            
            processed_count += 1
            print(f"Успешно установлено! (№{processed_count})")
            
            delay_hours = 1
            next_change = datetime.now().timestamp() + (delay_hours * 3600)
            next_time = datetime.fromtimestamp(next_change).strftime('%H:%M:%S')
            
            print(f"Следующая смена в {next_time}")
            await asyncio.sleep(delay_hours * random.randint(1500, 4000))
            
        except Exception as e:
            error_count += 1
            print(f"Ошибка установки: {e}")
            
            prepared_path = source_path + ".prepared.jpg"
            if os.path.exists(prepared_path):
                os.remove(prepared_path)
            
            error_path = os.path.join(error_folder, current_file)
            shutil.move(source_path, error_path)
            
            print(f"Файл перемещен в папку ошибок (Всего ошибок: {error_count})")
            
            await asyncio.sleep(60)

    print(f"\n=== Итоги ===")
    print(f"Успешно: {processed_count}")
    print(f"Ошибок: {error_count}")
    
    await client.disconnect()

asyncio.run(change_avatar_simple())
