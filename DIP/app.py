import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import base64
import uuid
import json

# Import custom modules
from modules.basic_operations import BasicOperations
from modules.advanced_operations import AdvancedOperations
from modules.morphological_operations import MorphologicalOperations
from modules.segmentation import SegmentationOperations

app = Flask(__name__)
app.secret_key = "smartdip_secret_key"
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize operation modules
basic_ops = BasicOperations()
advanced_ops = AdvancedOperations()
morphological_ops = MorphologicalOperations()
segmentation_ops = SegmentationOperations()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle image upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate unique ID for the image
        unique_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        saved_filename = f"{name}_{unique_id}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)
        
        # Read image with OpenCV
        img = cv2.imread(filepath)
        if img is None:
            os.remove(filepath)
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Convert to base64 for JSON response
        _, buffer = cv2.imencode(ext, img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True, 
            'filename': saved_filename,
            'image': img_base64,
            'width': img.shape[1],
            'height': img.shape[0]
        })
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/process', methods=['POST'])
def process_image():
    """Process an image with requested operations"""
    data = request.json
    
    if not data or 'filename' not in data or 'operations' not in data:
        return jsonify({'error': 'Invalid request data'}), 400
    
    filename = data['filename']
    operations = data['operations']
    
    # Load the image
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image not found'}), 404
    
    img = cv2.imread(image_path)
    if img is None:
        return jsonify({'error': 'Could not read image'}), 400
    
    results = []
    current_img = img.copy()
    
    # Apply each operation in sequence
    for op in operations:
        op_type = op.get('type')
        params = op.get('params', {})
        
        try:
            # Apply the appropriate operation based on type
            if op_type in dir(basic_ops):
                processed, description = getattr(basic_ops, op_type)(current_img, **params)
            elif op_type in dir(advanced_ops):
                processed, description = getattr(advanced_ops, op_type)(current_img, **params)
            elif op_type in dir(morphological_ops):
                processed, description = getattr(morphological_ops, op_type)(current_img, **params)
            elif op_type in dir(segmentation_ops):
                processed, description = getattr(segmentation_ops, op_type)(current_img, **params)
            else:
                return jsonify({'error': f'Unknown operation: {op_type}'}), 400
            
            # Convert to base64 for JSON response
            _, buffer = cv2.imencode('.png', processed)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Store result
            results.append({
                'operation': op_type,
                'image': img_base64,
                'description': description,
                'width': processed.shape[1],
                'height': processed.shape[0]
            })
            
            # Update current image for next operation
            current_img = processed
            
        except Exception as e:
            return jsonify({'error': f'Error in operation {op_type}: {str(e)}'}), 500
    
    return jsonify({
        'success': True,
        'results': results
    })

@app.route('/save_processed', methods=['POST'])
def save_processed():
    """Save a processed image result"""
    data = request.json
    
    if not data or 'image' not in data or 'operation' not in data:
        return jsonify({'error': 'Invalid request data'}), 400
    
    image_data = data['image']
    operation = data['operation']
    
    try:
        # Decode base64 image
        img_data = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        filename = f"{operation}_{unique_id}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        return jsonify({
            'success': True, 
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Error saving image: {str(e)}'}), 500

@app.route('/get_available_operations', methods=['GET'])
def get_available_operations():
    """Return list of all operations available"""
    operations = {
        'basic': [method for method in dir(basic_ops) if not method.startswith('_')],
        'advanced': [method for method in dir(advanced_ops) if not method.startswith('_')],
        'morphological': [method for method in dir(morphological_ops) if not method.startswith('_')],
        'segmentation': [method for method in dir(segmentation_ops) if not method.startswith('_')]
    }
    
    # Include descriptions and parameter information for each operation
    operation_details = {}
    
    for category, ops in operations.items():
        for op in ops:
            if category == 'basic':
                module = basic_ops
            elif category == 'advanced':
                module = advanced_ops
            elif category == 'morphological':
                module = morphological_ops
            elif category == 'segmentation':
                module = segmentation_ops
                
            func = getattr(module, op)
            params = {}
            
            # Extract parameter info from function annotations or docstring
            if hasattr(func, '__annotations__'):
                for param, param_type in func.__annotations__.items():
                    if param != 'return' and param != 'image':
                        params[param] = {
                            'type': str(param_type.__name__),
                            'default': None  # Could be extracted from signature if needed
                        }
            
            operation_details[op] = {
                'category': category,
                'description': func.__doc__.split('\n')[0] if func.__doc__ else '',
                'parameters': params
            }
    
    return jsonify({
        'success': True,
        'operations': operations,
        'operation_details': operation_details
    })

@app.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    """Clear old uploaded files (admin function)"""
    # This would typically be password protected in a real app
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': f'Error clearing uploads: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)