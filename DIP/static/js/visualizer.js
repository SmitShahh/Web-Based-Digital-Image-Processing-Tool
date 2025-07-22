// SmartDIP - Visualization Script
// Handles advanced visualization features for image processing operations

/**
 * Creates a histogram visualization from image data
 * @param {HTMLImageElement} img - The image element to analyze
 * @param {HTMLCanvasElement} canvas - The canvas to draw the histogram on
 * @param {string} mode - Histogram mode ('gray', 'rgb', 'hsv')
 */
function createHistogramVisualization(img, canvas, mode = 'gray') {
    // Get canvas context
    const ctx = canvas.getContext('2d');
    
    // Create a temporary canvas to extract image data
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = img.width;
    tempCanvas.height = img.height;
    tempCtx.drawImage(img, 0, 0);
    
    // Get image data
    const imageData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
    const data = imageData.data;
    
    // Initialize histogram arrays
    const histR = new Array(256).fill(0);
    const histG = new Array(256).fill(0);
    const histB = new Array(256).fill(0);
    const histGray = new Array(256).fill(0);
    
    // Calculate histograms
    for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        
        histR[r]++;
        histG[g]++;
        histB[b]++;
        
        // Calculate grayscale value
        const gray = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
        histGray[gray]++;
    }
    
    // Find the maximum value for scaling
    let maxVal;
    
    if (mode === 'rgb') {
        maxVal = Math.max(...histR, ...histG, ...histB);
    } else if (mode === 'hsv') {
        // HSV histogram would require conversion - we'll stick with RGB here
        maxVal = Math.max(...histR, ...histG, ...histB);
    } else {
        maxVal = Math.max(...histGray);
    }
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set canvas size
    canvas.width = 256;
    canvas.height = 150;
    
    // Draw background
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw histogram
    if (mode === 'rgb') {
        // Draw RGB histograms
        drawHistogramChannel(ctx, histR, maxVal, 'red', canvas.height);
        drawHistogramChannel(ctx, histG, maxVal, 'green', canvas.height);
        drawHistogramChannel(ctx, histB, maxVal, 'blue', canvas.height);
    } else {
        // Draw grayscale histogram
        drawHistogramChannel(ctx, histGray, maxVal, 'black', canvas.height);
    }
    
    // Draw axes
    ctx.strokeStyle = '#999';
    ctx.beginPath();
    ctx.moveTo(0, canvas.height - 1);
    ctx.lineTo(canvas.width, canvas.height - 1);
    ctx.stroke();
}

/**
 * Draws a histogram channel on the canvas
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Array} hist - Histogram data array
 * @param {number} maxVal - Maximum value for scaling
 * @param {string} color - Color of the histogram
 * @param {number} height - Canvas height
 */
function drawHistogramChannel(ctx, hist, maxVal, color, height) {
    ctx.beginPath();
    ctx.strokeStyle = color;
    
    for (let i = 0; i < hist.length; i++) {
        // Scale histogram values to fit canvas
        const barHeight = (hist[i] / maxVal) * height;
        
        // Draw line
        ctx.moveTo(i, height);
        ctx.lineTo(i, height - barHeight);
    }
    
    ctx.stroke();
}

/**
 * Creates a pseudo-colored visualization of an image
 * @param {HTMLImageElement} img - The image element to process
 * @param {string} colormap - The colormap to use (e.g., 'jet', 'viridis', 'hot')
 * @returns {HTMLCanvasElement} - The canvas with the pseudo-colored image
 */
function createPseudoColorVisualization(img, colormap = 'jet') {
    // Create a canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;
    
    // Draw the image to canvas
    ctx.drawImage(img, 0, 0);
    
    // Get image data
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    
    // Apply the colormap
    for (let i = 0; i < data.length; i += 4) {
        // Get grayscale value
        const gray = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
        
        // Apply colormap
        const color = applyColormap(gray, colormap);
        
        data[i] = color.r;
        data[i + 1] = color.g;
        data[i + 2] = color.b;
    }
    
    // Put modified image data back to canvas
    ctx.putImageData(imageData, 0, 0);
    
    return canvas;
}

/**
 * Maps a grayscale value to a color using the specified colormap
 * @param {number} value - Grayscale value (0-255)
 * @param {string} colormap - The colormap to use
 * @returns {Object} - RGB color object
 */
function applyColormap(value, colormap) {
    // Normalize value to 0-1
    const v = value / 255;
    
    let r, g, b;
    
    switch (colormap) {
        case 'jet':
            r = jetColormap(v, 0);
            g = jetColormap(v, 1);
            b = jetColormap(v, 2);
            break;
            
        case 'hot':
            r = v * 255;
            g = v < 0.5 ? 0 : (v - 0.5) * 2 * 255;
            b = v < 0.75 ? 0 : (v - 0.75) * 4 * 255;
            break;
            
        case 'viridis':
            // Simplified approximation of viridis
            r = v < 0.5 ? 68 : 94 + (v - 0.5) * 158;
            g = 1 + v * 254;
            b = v < 0.5 ? 84 + v * 104 : 140 - (v - 0.5) * 140;
            break;
            
        default:
            r = g = b = value;
    }
    
    return { r: Math.round(r), g: Math.round(g), b: Math.round(b) };
}

/**
 * Calculate color for jet colormap
 * @param {number} v - Normalized value (0-1)
 * @param {number} component - Component index (0=R, 1=G, 2=B)
 * @returns {number} - Color component value (0-255)
 */
function jetColormap(v, component) {
    const n = 4; // Number of color transitions
    let result;
    
    if (component === 0) {  // Red
        if (v < 0.125) result = 0;
        else if (v < 0.375) result = (v - 0.125) * 4;
        else if (v < 0.625) result = 1;
        else if (v < 0.875) result = 1 - (v - 0.625) * 4;
        else result = 0;
    } else if (component === 1) {  // Green
        if (v < 0.125) result = 0;
        else if (v < 0.375) result = (v - 0.125) * 4;
        else if (v < 0.625) result = 1;
        else if (v < 0.875) result = 1 - (v - 0.625) * 4;
        else result = 0;
        
        // Shift green
        const shift = 0.25;
        result = v <= shift ? 0 :
                v >= 1 - shift ? 0 :
                (v - shift) / (1 - 2 * shift);
    } else {  // Blue
        if (v < 0.375) result = 1 - v * 8/3;
        else result = 0;
    }
    
    return Math.round(result * 255);
}

/**
 * Creates a 3D surface plot visualization of an image
 * @param {HTMLImageElement} img - The image element to visualize
 * @param {HTMLElement} container - The container element to place the plot
 */
function create3DSurfacePlot(img, container) {
    // This would ideally use a 3D library like Three.js or Plotly
    // Here's a simplified version using Canvas API
    
    // Create canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 400;
    canvas.height = 300;
    
    // Sample the image to get intensity values
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = img.width;
    tempCanvas.height = img.height;
    tempCtx.drawImage(img, 0, 0);
    
    // Get image data
    const imageData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
    const data = imageData.data;
    
    // Sample points (downsample if the image is large)
    const sampleStepX = Math.max(1, Math.floor(img.width / 40));
    const sampleStepY = Math.max(1, Math.floor(img.height / 30));
    
    // Draw background
    ctx.fillStyle = '#f5f5f5';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Define 3D projection parameters
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const scale = 5;
    const angleX = Math.PI / 6; // Rotation around X axis
    const angleY = Math.PI / 6; // Rotation around Y axis
    
    // Draw surface lines
    ctx.strokeStyle = '#007bff';
    ctx.lineWidth = 0.5;
    
    // Draw X lines
    for (let y = 0; y < img.height; y += sampleStepY) {
        ctx.beginPath();
        
        for (let x = 0; x < img.width; x += sampleStepX) {
            const i = (y * img.width + x) * 4;
            const gray = (data[i] + data[i + 1] + data[i + 2]) / 3;
            
            // Apply 3D transformations (simplified)
            const x3d = x - img.width / 2;
            const y3d = y - img.height / 2;
            const z3d = gray / 5;
            
            // Rotate and project
            const xProj = x3d * Math.cos(angleY) - z3d * Math.sin(angleY);
            const yProj = y3d * Math.cos(angleX) - z3d * Math.sin(angleX);
            
            // Scale and translate
            const screenX = centerX + xProj * scale;
            const screenY = centerY + yProj * scale;
            
            if (x === 0) {
                ctx.moveTo(screenX, screenY);
            } else {
                ctx.lineTo(screenX, screenY);
            }
        }
        
        ctx.stroke();
    }
    
    // Draw Y lines
    for (let x = 0; x < img.width; x += sampleStepX) {
        ctx.beginPath();
        
        for (let y = 0; y < img.height; y += sampleStepY) {
            const i = (y * img.width + x) * 4;
            const gray = (data[i] + data[i + 1] + data[i + 2]) / 3;
            
            // Apply 3D transformations (simplified)
            const x3d = x - img.width / 2;
            const y3d = y - img.height / 2;
            const z3d = gray / 5;
            
            // Rotate and project
            const xProj = x3d * Math.cos(angleY) - z3d * Math.sin(angleY);
            const yProj = y3d * Math.cos(angleX) - z3d * Math.sin(angleX);
            
            // Scale and translate
            const screenX = centerX + xProj * scale;
            const screenY = centerY + yProj * scale;
            
            if (y === 0) {
                ctx.moveTo(screenX, screenY);
            } else {
                ctx.lineTo(screenX, screenY);
            }
        }
        
        ctx.stroke();
    }
    
    // Draw title
    ctx.fillStyle = '#333';
    ctx.font = '12px Arial';
    ctx.fillText('3D Surface Plot (Intensity Map)', 10, 20);
    
    // Add canvas to container
    container.innerHTML = '';
    container.appendChild(canvas);
}

/**
 * Creates a zoomed region of interest (ROI) visualization
 * @param {HTMLImageElement} img - The image element to zoom
 * @param {Object} roi - The region of interest {x, y, width, height}
 * @param {HTMLElement} container - The container element
 * @param {number} zoomFactor - The zoom factor
 */
function createZoomedROI(img, roi, container, zoomFactor = 3) {
    // Create canvas for the original image with ROI marker
    const originalCanvas = document.createElement('canvas');
    const originalCtx = originalCanvas.getContext('2d');
    originalCanvas.width = img.width;
    originalCanvas.height = img.height;
    
    // Draw original image
    originalCtx.drawImage(img, 0, 0);
    
    // Draw ROI rectangle
    originalCtx.strokeStyle = 'red';
    originalCtx.lineWidth = 2;
    originalCtx.strokeRect(roi.x, roi.y, roi.width, roi.height);
    
    // Create canvas for zoomed ROI
    const zoomedCanvas = document.createElement('canvas');
    const zoomedCtx = zoomedCanvas.getContext('2d');
    zoomedCanvas.width = roi.width * zoomFactor;
    zoomedCanvas.height = roi.height * zoomFactor;
    
    // Draw zoomed ROI
    zoomedCtx.drawImage(
        img,
        roi.x, roi.y, roi.width, roi.height,
        0, 0, zoomedCanvas.width, zoomedCanvas.height
    );
    
    // Add grid lines to zoomed view
    zoomedCtx.strokeStyle = 'rgba(200, 200, 200, 0.5)';
    zoomedCtx.lineWidth = 0.5;
    
    // Vertical grid lines
    for (let x = 0; x < zoomedCanvas.width; x += zoomFactor) {
        zoomedCtx.beginPath();
        zoomedCtx.moveTo(x, 0);
        zoomedCtx.lineTo(x, zoomedCanvas.height);
        zoomedCtx.stroke();
    }
    
    // Horizontal grid lines
    for (let y = 0; y < zoomedCanvas.height; y += zoomFactor) {
        zoomedCtx.beginPath();
        zoomedCtx.moveTo(0, y);
        zoomedCtx.lineTo(zoomedCanvas.width, y);
        zoomedCtx.stroke();
    }
    
    // Create container for both canvases
    const visualizationContainer = document.createElement('div');
    visualizationContainer.className = 'd-flex flex-wrap justify-content-center';
    
    // Original image container
    const originalContainer = document.createElement('div');
    originalContainer.className = 'me-3 mb-3 text-center';
    originalContainer.appendChild(originalCanvas);
    
    // Add label
    const originalLabel = document.createElement('div');
    originalLabel.className = 'small text-muted mt-1';
    originalLabel.textContent = 'Original Image with ROI';
    originalContainer.appendChild(originalLabel);
    
    // Zoomed image container
    const zoomedContainer = document.createElement('div');
    zoomedContainer.className = 'mb-3 text-center';
    zoomedContainer.appendChild(zoomedCanvas);
    
    // Add label
    const zoomedLabel = document.createElement('div');
    zoomedLabel.className = 'small text-muted mt-1';
    zoomedLabel.textContent = `${zoomFactor}x Zoomed Region`;
    zoomedContainer.appendChild(zoomedLabel);
    
    // Add both to visualization container
    visualizationContainer.appendChild(originalContainer);
    visualizationContainer.appendChild(zoomedContainer);
    
    // Add to main container
    container.innerHTML = '';
    container.appendChild(visualizationContainer);
}

/**
 * Creates an interactive pixel inspector visualization
 * @param {HTMLImageElement} img - The image element to inspect
 * @param {HTMLElement} container - The container element
 */
function createPixelInspector(img, container) {
    // Create canvas for the interactive image
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;
    
    // Draw image to canvas
    ctx.drawImage(img, 0, 0);
    
    // Get image data
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    
    // Create a container for the visualization
    const inspectorContainer = document.createElement('div');
    inspectorContainer.className = 'd-flex flex-wrap justify-content-center';
    
    // Canvas container
    const canvasContainer = document.createElement('div');
    canvasContainer.className = 'position-relative me-3 mb-3';
    canvasContainer.style.cursor = 'crosshair';
    
    // Create info panel
    const infoPanel = document.createElement('div');
    infoPanel.className = 'card mb-3';
    infoPanel.style.minWidth = '200px';
    infoPanel.innerHTML = `
        <div class="card-header bg-primary text-white">Pixel Information</div>
        <div class="card-body">
            <p id="pixel-position">Position: Hover over image</p>
            <div class="d-flex align-items-center mb-2">
                <div id="pixel-color-preview" style="width: 30px; height: 30px; border: 1px solid #ccc; margin-right: 10px;"></div>
                <div id="pixel-color-values">RGB: ---, ---, ---</div>
            </div>
            <p id="pixel-intensity">Intensity: ---</p>
            <p class="small text-muted">Hover over the image to inspect pixel values</p>
        </div>
    `;
    
    // Add canvas to container
    canvasContainer.appendChild(canvas);
    
    // Add highlight overlay for current pixel
    const overlay = document.createElement('div');
    overlay.className = 'position-absolute';
    overlay.style.border = '1px solid red';
    overlay.style.pointerEvents = 'none';
    overlay.style.width = '5px';
    overlay.style.height = '5px';
    overlay.style.display = 'none';
    canvasContainer.appendChild(overlay);
    
    // Add both to inspector container
    inspectorContainer.appendChild(canvasContainer);
    inspectorContainer.appendChild(infoPanel);
    
    // Add to main container
    container.innerHTML = '';
    container.appendChild(inspectorContainer);
    
    // Add event listeners
    canvas.addEventListener('mousemove', function(e) {
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / (rect.width / canvas.width));
        const y = Math.floor((e.clientY - rect.top) / (rect.height / canvas.height));
        
        // Handle edge case
        if (x < 0 || y < 0 || x >= canvas.width || y >= canvas.height) return;
        
        // Get pixel data
        const i = (y * canvas.width + x) * 4;
        const r = imageData.data[i];
        const g = imageData.data[i + 1];
        const b = imageData.data[i + 2];
        const a = imageData.data[i + 3];
        
        // Calculate intensity (grayscale value)
        const intensity = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
        
        // Update info panel
        document.getElementById('pixel-position').textContent = `Position: (${x}, ${y})`;
        document.getElementById('pixel-color-values').textContent = `RGB: ${r}, ${g}, ${b}`;
        document.getElementById('pixel-intensity').textContent = `Intensity: ${intensity}`;
        
        // Update color preview
        document.getElementById('pixel-color-preview').style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
        
        // Update overlay position
        overlay.style.display = 'block';
        overlay.style.left = `${x * (rect.width / canvas.width) - 2}px`;
        overlay.style.top = `${y * (rect.height / canvas.height) - 2}px`;
    });
    
    canvas.addEventListener('mouseout', function() {
        // Hide overlay when mouse leaves the canvas
        overlay.style.display = 'none';
        
        // Reset info panel
        document.getElementById('pixel-position').textContent = 'Position: Hover over image';
        document.getElementById('pixel-color-values').textContent = 'RGB: ---, ---, ---';
        document.getElementById('pixel-intensity').textContent = 'Intensity: ---';
        document.getElementById('pixel-color-preview').style.backgroundColor = '';
    });
}

// Export functions for use in other scripts
window.visualization = {
    createHistogramVisualization,
    createPseudoColorVisualization,
    create3DSurfacePlot,
    createZoomedROI,
    createPixelInspector
};