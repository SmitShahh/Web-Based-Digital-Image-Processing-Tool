// SmartDIP - Advanced Image Comparison Script

/**
 * Initialize the image comparison slider
 * This function sets up the drag functionality for the comparison slider
 */
function initializeComparisonSlider() {
    const slider = document.querySelector('.image-comparison-slider');
    if (!slider) return;
    
    const handle = slider.querySelector('.image-comparison-handle');
    const afterImage = slider.querySelector('.image-comparison-after');
    
    let isDragging = false;
    
    // Set initial position (50%)
    setPosition(50);
    
    // Mouse events
    handle.addEventListener('mousedown', startDragging);
    document.addEventListener('mouseup', stopDragging);
    document.addEventListener('mousemove', drag);
    
    // Touch events
    handle.addEventListener('touchstart', startDragging);
    document.addEventListener('touchend', stopDragging);
    document.addEventListener('touchmove', drag);
    
    // Click anywhere on slider
    slider.addEventListener('click', function(e) {
        if (e.target === handle) return; // Don't process clicks on the handle itself
        
        const sliderRect = slider.getBoundingClientRect();
        const percentage = ((e.clientX - sliderRect.left) / sliderRect.width) * 100;
        
        setPosition(percentage);
    });
    
    // Start dragging function
    function startDragging(e) {
        e.preventDefault();
        isDragging = true;
        
        // Add active class for styling
        handle.classList.add('active');
        
        // Add grabbing cursor to entire document during drag
        document.body.style.cursor = 'grabbing';
    }
    
    // Stop dragging function
    function stopDragging() {
        isDragging = false;
        
        // Remove active class
        handle.classList.remove('active');
        
        // Reset cursor
        document.body.style.cursor = '';
    }
    
    // Drag function
    function drag(e) {
        if (!isDragging) return;
        
        e.preventDefault();
        
        const sliderRect = slider.getBoundingClientRect();
        let clientX;
        
        // Handle both mouse and touch events
        if (e.type === 'touchmove') {
            clientX = e.touches[0].clientX;
        } else {
            clientX = e.clientX;
        }
        
        // Calculate percentage
        let percentage = ((clientX - sliderRect.left) / sliderRect.width) * 100;
        
        // Constrain to slider bounds
        percentage = Math.min(100, Math.max(0, percentage));
        
        // Set the position
        setPosition(percentage);
    }
    
    // Set position of handle and after image
    function setPosition(percentage) {
        handle.style.left = `${percentage}%`;
        afterImage.style.width = `${percentage}%`;
    }
}

/**
 * Create a magnifier glass for image comparison
 * This adds a magnifying glass effect to the comparison view
 */
function createMagnifier() {
    const slider = document.querySelector('.image-comparison-slider');
    if (!slider) return;
    
    // Create magnifier element
    const magnifier = document.createElement('div');
    magnifier.className = 'magnifier';
    magnifier.style.display = 'none';
    slider.appendChild(magnifier);
    
    // Set up the magnifier glass
    const glass = {
        element: magnifier,
        radius: 75, // pixels
        zoom: 2.5
    };
    
    // Track magnifier state
    let isActive = false;
    
    // Toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'btn btn-sm btn-outline-secondary magnifier-toggle';
    toggleBtn.innerHTML = '<i class="bi bi-search"></i> Magnifier';
    
    // Add toggle button after the slider
    slider.parentNode.insertBefore(toggleBtn, slider.nextSibling);
    
    // Toggle magnifier on button click
    toggleBtn.addEventListener('click', function() {
        isActive = !isActive;
        glass.element.style.display = isActive ? 'block' : 'none';
        this.classList.toggle('active');
    });
    
    // Move magnifier with mouse
    slider.addEventListener('mousemove', updateMagnifier);
    
    // Hide magnifier when mouse leaves the slider
    slider.addEventListener('mouseleave', function() {
        if (isActive) {
            glass.element.style.display = 'none';
        }
    });
    
    // Show magnifier when mouse enters (if active)
    slider.addEventListener('mouseenter', function() {
        if (isActive) {
            glass.element.style.display = 'block';
        }
    });
    
    // Update magnifier position and content
    function updateMagnifier(e) {
        if (!isActive) return;
        
        // Get cursor position
        const sliderRect = slider.getBoundingClientRect();
        const x = e.clientX - sliderRect.left;
        const y = e.clientY - sliderRect.top;
        
        // Position magnifier
        glass.element.style.left = `${x}px`;
        glass.element.style.top = `${y}px`;
        
        // Set magnifier size and border
        glass.element.style.width = `${glass.radius * 2}px`;
        glass.element.style.height = `${glass.radius * 2}px`;
        glass.element.style.borderRadius = `${glass.radius}px`;
        
        // Background position for zoom effect
        glass.element.style.backgroundImage = getBackgroundAtPosition(x, y);
        glass.element.style.backgroundSize = `${slider.offsetWidth * glass.zoom}px ${slider.offsetHeight * glass.zoom}px`;
        
        // Center the background image on the cursor position
        const bgPosX = Math.min(sliderRect.width, Math.max(0, x * glass.zoom - glass.radius));
        const bgPosY = Math.min(sliderRect.height, Math.max(0, y * glass.zoom - glass.radius));
        glass.element.style.backgroundPosition = `-${bgPosX}px -${bgPosY}px`;
    }
    
    // Get background image at cursor position
    function getBackgroundAtPosition(x, y) {
        // Get the dividing line position
        const divider = parseFloat(document.querySelector('.image-comparison-after').style.width) / 100 * slider.offsetWidth;
        
        // Determine which image to show
        if (x < divider) {
            return getComputedStyle(document.querySelector('.image-comparison-after')).backgroundImage;
        } else {
            return getComputedStyle(document.querySelector('.image-comparison-before')).backgroundImage;
        }
    }
}

/**
 * Sets up advanced comparison controls
 * This adds comparison controls for different visualization modes
 */
function setupComparisonControls() {
    const comparisonSection = document.getElementById('comparison-section');
    if (!comparisonSection) return;
    
    // Create controls container
    const controlsContainer = document.createElement('div');
    controlsContainer.className = 'comparison-controls mt-3 d-flex justify-content-center';
    
    // Add controls
    controlsContainer.innerHTML = `
        <div class="btn-group" role="group">
            <button type="button" class="btn btn-outline-primary active" data-mode="slider">
                <i class="bi bi-arrow-left-right"></i> Slider
            </button>
            <button type="button" class="btn btn-outline-primary" data-mode="side-by-side">
                <i class="bi bi-layout-split"></i> Side by Side
            </button>
            <button type="button" class="btn btn-outline-primary" data-mode="blend">
                <i class="bi bi-layers"></i> Blend
            </button>
            <button type="button" class="btn btn-outline-primary" data-mode="difference">
                <i class="bi bi-file-diff"></i> Difference
            </button>
        </div>
    `;
    
    // Add controls after the comparison slider
    const sliderContainer = comparisonSection.querySelector('.image-comparison-container');
    sliderContainer.after(controlsContainer);
    
    // Add event listeners to control buttons
    const buttons = controlsContainer.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Change comparison mode
            changeComparisonMode(this.getAttribute('data-mode'));
        });
    });
    
    // Create container for side-by-side, blend and difference modes
    const alternativeModes = document.createElement('div');
    alternativeModes.className = 'alternative-comparison-modes mt-3';
    alternativeModes.style.display = 'none';
    sliderContainer.after(alternativeModes);
    
    // Change comparison mode function
    function changeComparisonMode(mode) {
        const slider = document.querySelector('.image-comparison-slider');
        const alternativeModes = document.querySelector('.alternative-comparison-modes');
        
        // Get image URLs
        const originalImgUrl = document.querySelector('.image-comparison-before').style.backgroundImage.slice(5, -2);
        const processedImgUrl = document.querySelector('.image-comparison-after').style.backgroundImage.slice(5, -2);
        
        switch (mode) {
            case 'slider':
                // Show slider, hide alternative modes
                slider.parentElement.style.display = 'block';
                alternativeModes.style.display = 'none';
                break;
                
            case 'side-by-side':
                // Hide slider, show side-by-side
                slider.parentElement.style.display = 'none';
                alternativeModes.style.display = 'block';
                
                // Create side-by-side view
                alternativeModes.innerHTML = `
                    <div class="row">
                        <div class="col-md-6 text-center">
                            <h6>Original</h6>
                            <img src="${originalImgUrl}" class="img-fluid" alt="Original Image">
                        </div>
                        <div class="col-md-6 text-center">
                            <h6>Processed</h6>
                            <img src="${processedImgUrl}" class="img-fluid" alt="Processed Image">
                        </div>
                    </div>
                `;
                break;
                
            case 'blend':
                // Hide slider, show blend
                slider.parentElement.style.display = 'none';
                alternativeModes.style.display = 'block';
                
                // Create blend view with opacity slider
                alternativeModes.innerHTML = `
                    <div class="text-center position-relative blend-container">
                        <img src="${originalImgUrl}" class="img-fluid" alt="Original Image">
                        <img src="${processedImgUrl}" class="img-fluid position-absolute top-0 start-0" 
                             alt="Processed Image" style="opacity: 0.5; width: 100%; height: 100%;">
                    </div>
                    <div class="mt-2">
                        <label for="blend-opacity" class="form-label">Blend Opacity: 50%</label>
                        <input type="range" class="form-range" id="blend-opacity" min="0" max="100" value="50">
                    </div>
                `;
                
                // Add event listener to opacity slider
                document.getElementById('blend-opacity').addEventListener('input', function() {
                    const opacity = this.value / 100;
                    document.querySelector('.blend-container img:nth-child(2)').style.opacity = opacity;
                    document.querySelector('label[for="blend-opacity"]').textContent = `Blend Opacity: ${this.value}%`;
                });
                break;
                
            case 'difference':
                // Hide slider, show difference
                slider.parentElement.style.display = 'none';
                alternativeModes.style.display = 'block';
                
                // Create a canvas for difference calculation
                alternativeModes.innerHTML = `
                    <div class="text-center">
                        <canvas id="difference-canvas" class="img-fluid"></canvas>
                    </div>
                    <div class="mt-2 text-center">
                        <span class="badge bg-secondary">Dark areas = similar | Bright areas = different</span>
                    </div>
                `;
                
                // Calculate and display difference
                calculateDifference(originalImgUrl, processedImgUrl);
                break;
        }
    }
    
    // Function to calculate difference between images
    function calculateDifference(originalUrl, processedUrl) {
        const canvas = document.getElementById('difference-canvas');
        const ctx = canvas.getContext('2d');
        
        // Create Image objects
        const originalImg = new Image();
        const processedImg = new Image();
        
        // Set crossOrigin to allow canvas to read the images
        originalImg.crossOrigin = 'Anonymous';
        processedImg.crossOrigin = 'Anonymous';
        
        // Load original image
        originalImg.onload = function() {
            // Set canvas size
            canvas.width = originalImg.width;
            canvas.height = originalImg.height;
            
            // Draw original image to canvas
            ctx.drawImage(originalImg, 0, 0);
            
            // Get original image data
            const originalData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            
            // Load processed image
            processedImg.onload = function() {
                // Draw processed image to canvas
                ctx.drawImage(processedImg, 0, 0);
                
                // Get processed image data
                const processedData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                
                // Calculate difference
                const differenceData = ctx.createImageData(canvas.width, canvas.height);
                
                for (let i = 0; i < originalData.data.length; i += 4) {
                    // Calculate absolute difference for each channel
                    const rDiff = Math.abs(originalData.data[i] - processedData.data[i]);
                    const gDiff = Math.abs(originalData.data[i+1] - processedData.data[i+1]);
                    const bDiff = Math.abs(originalData.data[i+2] - processedData.data[i+2]);
                    
                    // Enhance difference for better visibility
                    const enhanceFactor = 2;
                    
                    // Set difference pixels (using average of RGB differences)
                    differenceData.data[i] = rDiff * enhanceFactor;
                    differenceData.data[i+1] = gDiff * enhanceFactor;
                    differenceData.data[i+2] = bDiff * enhanceFactor;
                    differenceData.data[i+3] = 255; // Alpha channel
                }
                
                // Draw difference image
                ctx.putImageData(differenceData, 0, 0);
            };
            
            processedImg.src = processedUrl;
        };
        
        originalImg.src = originalUrl;
    }
}

// Initialize these features when the comparison view is activated
document.addEventListener('DOMContentLoaded', function() {
    // These will be called from main.js when comparison view is active
    window.comparisonFeatures = {
        initializeComparisonSlider,
        createMagnifier,
        setupComparisonControls
    };
});