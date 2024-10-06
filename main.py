from io import BytesIO
from PIL import Image
import numpy as np
from flask import Flask, render_template, request, jsonify
import base64

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_file(file, quality=40):
    buffer = BytesIO()
    file.save(buffer, format='JPEG', quality=quality)
    return buffer, Image.open(buffer)

def analyze_file(original):
    compressed_buffer, compressed = compress_file(original)        
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
        
    return compressed_buffer, max_zone, noise_level

def process_files(files):
    results = []
    for file in files:
        if file and allowed_file(file.filename):
            image = Image.open(file.stream)
            compressed_buffer, max_zone, noise_level = analyze_file(image)
            img_str = base64.b64encode(compressed_buffer.getvalue()).decode()
            results.append((file.filename, max_zone, noise_level, img_str))
    return results

def generate_html_from_files(results):
    html_content = '''
        <div class="image-grid">
    '''
    
    for filename, max_zone, noise_level, img_str in results:
        html_content += f'''
        <div class="image-container">
            <div class="image-info">
                <strong>{filename}</strong><br>
                Номер зоны: {max_zone}<br>
                Уровень помех: {noise_level:.2f}%
            </div>
            <img src="data:image;base64,{img_str}" alt="{filename}">
        </div>
        '''
    
    html_content += '''
        </div>
    '''
    
    return html_content

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('files')
        results = process_files(files)
        html_content = generate_html_from_files(results)
        return jsonify({'html_content': html_content}) 
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)