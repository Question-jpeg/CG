import os
from io import BytesIO
from PIL import Image
import numpy as np

IMAGES_FOLDER_PATH = 'images'
OUTPUT_FOLDER_PATH = 'output'

def compress_image(image_path, quality=40):
    with Image.open(image_path) as img:
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality)
    return Image.open(buffer)

def analyze_image(original_path):
    with Image.open(original_path) as original:
        compressed = compress_image(original_path)        
        difference = np.abs(np.array(original) - np.array(compressed))
        
        width, height = original.size
        cell_width, cell_height = width // 4, height // 4
        
        max_diff = 0
        max_zone = 0
        
        for i in range(4):
            for j in range(4):
                zone = difference[i*cell_height:(i+1)*cell_height, j*cell_width:(j+1)*cell_width]
                zone_diff = np.sum(zone)
                if zone_diff > max_diff:
                    max_diff = zone_diff
                    max_zone = i * 4 + j + 1
        
        max_possible_diff = 255 * 3 * width * height
        noise_level = (max_diff / max_possible_diff) * 100
        
    return max_zone, noise_level

def process_images():
    results = []
    for filename in os.listdir(IMAGES_FOLDER_PATH):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(IMAGES_FOLDER_PATH, filename)
            max_zone, noise_level = analyze_image(image_path)
            results.append((filename, max_zone, noise_level))
    return results

def generate_html(results):
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Анализ помех сжатых изображений</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            h1 { text-align: center; }
            .image-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .image-container { position: relative; overflow: hidden; }
            .image-info { 
                position: absolute; 
                top: 0; 
                left: 0; 
                background: rgba(255, 255, 255, 0.8); 
                padding: 10px; 
                width: 100%; 
                box-sizing: border-box;
            }
            img { width: 100%; height: auto; display: block; }
        </style>
    </head>
    <body>
        <h1>Анализ помех сжатых изображений</h1>
        <div class="image-grid">
    '''
    
    for filename, max_zone, noise_level in results:
        src = f'../{IMAGES_FOLDER_PATH}/{filename}'
        html_content += f'''
        <div class="image-container">
            <div class="image-info">
                <strong>{filename}</strong><br>
                Номер зоны: {max_zone}<br>
                Уровень помех: {noise_level:.2f}%
            </div>
            <img src="{src}" alt="{filename}">
        </div>
        '''
    
    html_content += '''
        </div>
    </body>
    </html>
    '''
    
    with open(f'{OUTPUT_FOLDER_PATH}/results.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():    
    results = process_images()
    generate_html(results)
    print("Анализ завершён. Результаты сохранены в output/results.html")

if __name__ == '__main__':
    main()