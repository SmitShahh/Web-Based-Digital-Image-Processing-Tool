// SmartDIP - Enhanced Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    let currentImage = null;
    let operationQueue = [];
    let availableOperations = {};
    let operationDetails = {};
    let processingResults = [];
    let darkMode = localStorage.getItem('darkMode') === 'enabled';

    // DOM Elements - Main UI
    const uploadForm = document.getElementById('upload-form');
    const imageUpload = document.getElementById('image-upload');
    const uploadStatus = document.getElementById('upload-status');
    const originalImageContainer = document.getElementById('original-image-container');
    const originalImageInfo = document.getElementById('original-image-info');
    const operationsSection = document.getElementById('operations-section');
    const resultsSection = document.getElementById('results-section');
    const comparisonSection = document.getElementById('comparison-section');
    const educationalSection = document.getElementById('educational-content-section');

    // DOM Elements - Operation selectors
    const operationCategory = document.getElementById('operation-category');
    const operationSelect = document.getElementById('operation-select');
    const parametersContainer = document.getElementById('parameters-container');
    const addOperationBtn = document.getElementById('add-operation-btn');

    // DOM Elements - Queue control
    const operationQueueContainer = document.getElementById('operation-queue');
    const clearQueueBtn = document.getElementById('clear-queue-btn');
    const processQueueBtn = document.getElementById('process-queue-btn');

    // DOM Elements - Results display
    const resultsContainer = document.getElementById('results-container');
    const comparisonOriginal = document.getElementById('comparison-original');
    const comparisonFinal = document.getElementById('comparison-final');

    // DOM Elements - Educational content
    const educationalContent = document.getElementById('educational-content');
    const relatedConcepts = document.getElementById('related-concepts');
    const mathematicalBackground = document.getElementById('mathematical-background');

    // DOM Elements - Image statistics
    const imageHistogram = document.getElementById('image-histogram');
    const imageStatsText = document.getElementById('image-stats-text');

    // DOM Elements - Theme toggle
    const themeToggleBtn = document.getElementById('theme-toggle');

    // Initialize - Apply dark mode if enabled
    if (darkMode) {
        document.body.classList.add('dark-mode');
        if (themeToggleBtn) {
            themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
        }
    }

    // Initialize - fetch available operations on page load
    if (operationCategory) {
        fetchAvailableOperations();
    }

    // Event Listeners - Main functionality
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleImageUpload);
    }
    
    if (clearQueueBtn) {
        clearQueueBtn.addEventListener('click', clearOperationQueue);
    }
    
    if (processQueueBtn) {
        processQueueBtn.addEventListener('click', processOperationQueue);
    }

    // Event Listeners - Operation selector
    if (operationCategory) {
        operationCategory.addEventListener('change', handleCategoryChange);
    }
    
    if (operationSelect) {
        operationSelect.addEventListener('change', handleOperationChange);
    }
    
    if (addOperationBtn) {
        addOperationBtn.addEventListener('click', addOperationToQueue);
    }

    // Event Listeners - Theme toggle
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleDarkMode);
    }

    // ---- Functions ----

    // Toggle dark mode
    function toggleDarkMode() {
        if (document.body.classList.contains('dark-mode')) {
            document.body.classList.remove('dark-mode');
            themeToggleBtn.innerHTML = '<i class="bi bi-moon-fill"></i>';
            localStorage.setItem('darkMode', 'disabled');
        } else {
            document.body.classList.add('dark-mode');
            themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
            localStorage.setItem('darkMode', 'enabled');
        }
    }

    // Fetch available operations from the backend
    function fetchAvailableOperations() {
        fetch('/get_available_operations')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    availableOperations = data.operations;
                    operationDetails = data.operation_details;

                    // Populate operation categories
                    populateOperationCategories();
                } else {
                    showError('Failed to load operations: ' + data.error);
                }
            })
            .catch(error => {
                showError('Error fetching operations: ' + error.message);
            });
    }

    // Populate operation categories
    function populateOperationCategories() {
        if (!operationCategory) return;
        
        operationCategory.innerHTML = '<option value="">Select category</option>';
        
        for (const category in availableOperations) {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = capitalizeFirstLetter(category) + ' Operations';
            operationCategory.appendChild(option);
        }
    }

    // Handle category selection change
    function handleCategoryChange() {
        if (!operationCategory || !operationSelect || !parametersContainer) return;
        
        const category = operationCategory.value;
        
        // Clear operation select and parameters
        operationSelect.innerHTML = '<option value="">Select operation</option>';
        parametersContainer.innerHTML = '';
        
        // Disable operation select if no category selected
        if (!category) {
            operationSelect.disabled = true;
            if (addOperationBtn) {
                addOperationBtn.disabled = true;
            }
            return;
        }
        
        // Enable operation select
        operationSelect.disabled = false;
        
        // Populate operations for selected category
        const operations = availableOperations[category];
        operations.forEach(op => {
            const option = document.createElement('option');
            option.value = op;
            option.textContent = formatOperationName(op);
            operationSelect.appendChild(option);
        });
    }

    // Handle operation selection change
    function handleOperationChange() {
        if (!operationSelect || !parametersContainer) return;
        
        // Clear parameters container
        parametersContainer.innerHTML = '';

        // Get selected operation
        const operation = operationSelect.value;

        if (operation) {
            // Enable add operation button
            if (addOperationBtn) {
                addOperationBtn.disabled = false;
            }

            // Get operation details
            const details = operationDetails[operation];

            if (details && details.parameters) {
                // Create parameter inputs for the selected operation
                for (const paramName in details.parameters) {
                    const paramInfo = details.parameters[paramName];
                    const paramType = paramInfo.type || 'number';

                    // Create parameter input
                    const paramContainer = document.createElement('div');
                    paramContainer.className = 'col-md-4 mb-3';

                    const label = document.createElement('label');
                    label.className = 'form-label';
                    label.textContent = formatParameterName(paramName);
                    label.setAttribute('for', `param-${operation}-${paramName}`);

                    let input;
                    if (paramType === 'bool') {
                        // Create checkbox for boolean parameters
                        input = document.createElement('div');
                        input.className = 'form-check';

                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.className = 'form-check-input';
                        checkbox.id = `param-${operation}-${paramName}`;
                        checkbox.name = paramName;

                        const checkboxLabel = document.createElement('label');
                        checkboxLabel.className = 'form-check-label';
                        checkboxLabel.setAttribute('for', `param-${operation}-${paramName}`);
                        checkboxLabel.textContent = 'Enable';

                        input.appendChild(checkbox);
                        input.appendChild(checkboxLabel);
                    } else if (paramName === 'kernel_shape') {
                        // Special case for kernel shapes (dropdown)
                        input = document.createElement('select');
                        input.className = 'form-select';
                        input.id = `param-${operation}-${paramName}`;
                        input.name = paramName;

                        const shapes = ['rect', 'ellipse', 'cross'];
                        shapes.forEach(shape => {
                            const option = document.createElement('option');
                            option.value = shape;
                            option.textContent = capitalizeFirstLetter(shape);
                            input.appendChild(option);
                        });
                    } else if (paramName === 'threshold_type') {
                        // Special case for threshold types (dropdown)
                        input = document.createElement('select');
                        input.className = 'form-select';
                        input.id = `param-${operation}-${paramName}`;
                        input.name = paramName;

                        const thresholdTypes = [
                            { value: 0, name: 'Binary' },
                            { value: 1, name: 'Binary Inverted' },
                            { value: 2, name: 'Truncate' },
                            { value: 3, name: 'To Zero' },
                            { value: 4, name: 'To Zero Inverted' }
                        ];

                        thresholdTypes.forEach(type => {
                            const option = document.createElement('option');
                            option.value = type.value;
                            option.textContent = type.name;
                            input.appendChild(option);
                        });
                    } else if (paramName === 'noise_type') {
                        // Special case for noise types (dropdown)
                        input = document.createElement('select');
                        input.className = 'form-select';
                        input.id = `param-${operation}-${paramName}`;
                        input.name = paramName;

                        const noiseTypes = [
                            { value: 'gaussian', name: 'Gaussian Noise' },
                            { value: 'salt_pepper', name: 'Salt & Pepper Noise' },
                            { value: 'speckle', name: 'Speckle Noise' }
                        ];

                        noiseTypes.forEach(type => {
                            const option = document.createElement('option');
                            option.value = type.value;
                            option.textContent = type.name;
                            input.appendChild(option);
                        });
                    } else if (paramName === 'color_space') {
                        // Special case for color spaces (dropdown)
                        input = document.createElement('select');
                        input.className = 'form-select';
                        input.id = `param-${operation}-${paramName}`;
                        input.name = paramName;

                        const colorSpaces = [
                            { value: 'RGB', name: 'RGB' },
                            { value: 'HSV', name: 'HSV' },
                            { value: 'LAB', name: 'LAB' },
                            { value: 'YCrCb', name: 'YCrCb' }
                        ];

                        colorSpaces.forEach(space => {
                            const option = document.createElement('option');
                            option.value = space.value;
                            option.textContent = space.name;
                            input.appendChild(option);
                        });
                    } else {
                        // Default: create number input with appropriate constraints
                        input = document.createElement('input');
                        input.type = 'number';
                        input.className = 'form-control';
                        input.id = `param-${operation}-${paramName}`;
                        input.name = paramName;

                        // Set default values and constraints based on parameter name
                        if (paramName.includes('kernel_size')) {
                            input.value = 5;
                            input.min = 1;
                            input.max = 31;
                            input.step = 2; // Ensure odd values only
                        } else if (paramName.includes('threshold')) {
                            input.value = 127;
                            input.min = 0;
                            input.max = 255;
                        } else if (paramName.includes('sigma')) {
                            input.value = 1.0;
                            input.min = 0.1;
                            input.step = 0.1;
                        } else if (paramName === 'alpha') {
                            input.value = 1.5;
                            input.min = 0.1;
                            input.max = 3.0;
                            input.step = 0.1;
                        } else if (paramName === 'beta') {
                            input.value = 50;
                            input.min = -255;
                            input.max = 255;
                        } else if (paramName.includes('iterations')) {
                            input.value = 1;
                            input.min = 1;
                            input.max = 10;
                        } else if (paramName === 'k') { // For k-means
                            input.value = 3;
                            input.min = 2;
                            input.max = 20;
                        } else if (paramName.includes('cutoff')) { // For frequency filters
                            input.value = 30;
                            input.min = 1;
                            input.max = 100;
                        } else if (paramName === 'noise_param') { // For noise parameter
                            input.value = 25;
                            input.min = 1;
                            input.max = 100;
                        } else {
                            input.value = 1;
                        }
                    }

                    // Add label and input to container
                    paramContainer.appendChild(label);
                    
                    if (input instanceof HTMLElement) {
                        paramContainer.appendChild(input);
                    } else if (input instanceof DocumentFragment) {
                        paramContainer.appendChild(input);
                    }

                    // Add to parameters container
                    parametersContainer.appendChild(paramContainer);
                }
            }
        } else {
            // Disable add operation button if no operation selected
            if (addOperationBtn) {
                addOperationBtn.disabled = true;
            }
        }
    }
    
    // Add operation to queue
    function addOperationToQueue() {
        if (!operationSelect || !parametersContainer) return;
        
        // Get the select element and parameters container
        const operation = operationSelect.value;

        if (!operation) {
            showError('Please select an operation');
            return;
        }

        // Collect parameters for the operation
        const params = {};
        const paramInputs = parametersContainer.querySelectorAll('input, select');

        paramInputs.forEach(input => {
            let value;

            if (input.type === 'checkbox') {
                value = input.checked;
            } else if (input.type === 'number') {
                value = parseFloat(input.value);
            } else {
                value = input.value;
            }

            // Extract the parameter name from the input ID
            // Format: param-{operation}-{paramName}
            const idParts = input.id.split('-');
            if (idParts.length >= 3) {
                const paramName = idParts[2];
                params[paramName] = value;
            }
        });

        // Add operation to queue
        operationQueue.push({
            type: operation,
            params: params
        });

        // Reset the operation select
        operationSelect.value = '';
        parametersContainer.innerHTML = '';
        if (addOperationBtn) {
            addOperationBtn.disabled = true;
        }

        // Update UI
        updateOperationQueueUI();

        // Enable queue buttons
        if (clearQueueBtn) {
            clearQueueBtn.disabled = false;
        }
        if (processQueueBtn) {
            processQueueBtn.disabled = false;
        }

        // Show toast notification
        showToast(`Added ${formatOperationName(operation)} to queue`);
    }

    // Update the operation queue display
    function updateOperationQueueUI() {
        if (!operationQueueContainer) return;
        
        operationQueueContainer.innerHTML = '';

        if (operationQueue.length === 0) {
            const emptyMessage = document.createElement('li');
            emptyMessage.className = 'list-group-item text-muted text-center';
            emptyMessage.innerHTML = '<i class="bi bi-info-circle me-2"></i>No operations in queue. Add operations to process.';
            operationQueueContainer.appendChild(emptyMessage);

            // Disable queue buttons
            if (clearQueueBtn) {
                clearQueueBtn.disabled = true;
            }
            if (processQueueBtn) {
                processQueueBtn.disabled = true;
            }
            return;
        }

        // Create list item for each operation in queue
        operationQueue.forEach((op, index) => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center queue-item';

            // Display operation name
            const opName = formatOperationName(op.type);

            // Display parameters if any
            let paramDisplay = '';
            if (Object.keys(op.params).length > 0) {
                paramDisplay = '<small class="text-muted"> (';
                const paramList = [];
                for (const [key, value] of Object.entries(op.params)) {
                    paramList.push(`${formatParameterName(key)}: ${value}`);
                }
                paramDisplay += paramList.join(', ') + ')</small>';
            }

            listItem.innerHTML = `
                <div>
                    <span>${index + 1}. ${opName}${paramDisplay}</span>
                </div>
                <button class="btn btn-sm btn-outline-danger queue-item-remove" onclick="removeOperation(${index})">
                    <i class="bi bi-x"></i>
                </button>
            `;

            operationQueueContainer.appendChild(listItem);
        });
    }

    // Remove operation from queue
    window.removeOperation = function(index) {
        operationQueue.splice(index, 1);
        updateOperationQueueUI();
        showToast('Operation removed from queue');
    };

    // Clear operation queue
    function clearOperationQueue() {
        operationQueue = [];
        updateOperationQueueUI();
        showToast('Operation queue cleared');
    }

    // Handle image upload
    function handleImageUpload(event) {
        console.log("Upload function called");
        event.preventDefault();

        if (!imageUpload || !uploadStatus) return;

        const file = imageUpload.files[0];
        console.log("File selected:", file);

        if (!file) {
            showError('Please select an image file');
            return;
        }

        // Show loading state
        uploadStatus.innerHTML = '<div class="alert alert-info"><div class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div> Uploading image...</div>';

        // Create form data
        const formData = new FormData();
        formData.append('file', file);

        console.log("Sending upload request to server");
        // Send request to backend
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log("Response received:", response);
            return response.json();
        })
        .then(data => {
            console.log("Parsed response data:", data);
            if (data.success) {
                // Store image info
                currentImage = {
                    filename: data.filename,
                    width: data.width,
                    height: data.height,
                    image: data.image
                };

                // Update UI
                updateOriginalImageDisplay();

                // Show operations section
                if (operationsSection) {
                    operationsSection.style.display = 'block';
                }

                // Clear previous results
                if (resultsContainer) {
                    resultsContainer.innerHTML = '';
                }
                if (resultsSection) {
                    resultsSection.style.display = 'none';
                }
                if (comparisonSection) {
                    comparisonSection.style.display = 'none';
                }
                if (educationalSection) {
                    educationalSection.style.display = 'none';
                }

                // Show success message
                uploadStatus.innerHTML = '<div class="alert alert-success">Image uploaded successfully</div>';

                // Calculate image statistics
                if (imageHistogram && imageStatsText) {
                    calculateImageStatistics(currentImage);
                }

                // Reset the file input
                if (uploadForm) {
                    uploadForm.reset();
                }

                // Clear after a delay
                setTimeout(() => {
                    uploadStatus.innerHTML = '';
                }, 3000);

                // Show toast
                showToast('Image uploaded successfully', 'success');
            } else {
                showError('Upload failed: ' + data.error);
            }
        })
        .catch(error => {
            console.error("Error during upload:", error);
            showError('Error uploading image: ' + error.message);
        });
    }

    // Update original image display
    function updateOriginalImageDisplay() {
        if (!currentImage || !originalImageContainer) return;

        originalImageContainer.innerHTML = '';

        // Create image element
        const img = document.createElement('img');
        img.className = 'img-fluid';
        img.src = 'data:image/png;base64,' + currentImage.image;
        img.alt = 'Original image';

        originalImageContainer.appendChild(img);

        // Update image info
        if (originalImageInfo) {
            originalImageInfo.textContent = `Dimensions: ${currentImage.width} × ${currentImage.height} pixels`;
        }
    }

    // Process the operation queue
    function processOperationQueue() {
        if (!processQueueBtn) return;
        
        if (operationQueue.length === 0) {
            showError('No operations to process');
            return;
        }

        if (!currentImage) {
            showError('No image uploaded');
            return;
        }

        // Show loading state
        processQueueBtn.disabled = true;
        processQueueBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';

        // Prepare request data
        const requestData = {
            filename: currentImage.filename,
            operations: operationQueue
        };

        // Send request to backend
        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Store results
                processingResults = data.results;

                // Display results
                displayResults(data.results);

                // Show results and comparison sections
                if (resultsSection) {
                    resultsSection.style.display = 'block';
                }
                if (comparisonSection) {
                    comparisonSection.style.display = 'block';
                }

                // Update comparison view
                updateComparisonView();

                // Show educational content for the first operation
                if (data.results.length > 0 && educationalSection) {
                    showEducationalContent(operationQueue[0].type);
                    educationalSection.style.display = 'block';
                }

                // Scroll to results
                if (resultsSection) {
                    resultsSection.scrollIntoView({ behavior: 'smooth' });
                }

                // Show success toast
                showToast('Processing completed successfully!', 'success');
            } else {
                showError('Processing failed: ' + data.error);
            }
        })
        .catch(error => {
            showError('Error processing queue: ' + error.message);
        })
        .finally(() => {
            // Reset button state
            processQueueBtn.disabled = false;
            processQueueBtn.innerHTML = 'Process Queue';
        });
    }

    // Display processing results
    function displayResults(results) {
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = '';

        if (results.length === 0) {
            const noResults = document.createElement('div');
            noResults.className = 'col-12 text-center text-muted';
            noResults.innerHTML = '<i class="bi bi-exclamation-circle me-2"></i>No results to display';
            resultsContainer.appendChild(noResults);
            return;
        }

        // Get result card template
        const template = document.getElementById('result-card-template');
        if (!template) return;

        // Create result cards
        results.forEach((result, index) => {
            // Clone template
            const resultCard = template.content.cloneNode(true);

            // Set operation name
            const opName = formatOperationName(result.operation);
            resultCard.querySelector('.operation-name').textContent = opName;

            // Set image
            const img = resultCard.querySelector('.result-image');
            img.src = 'data:image/png;base64,' + result.image;
            img.alt = opName + ' result';

            // Set description (using innerHTML to render HTML in description)
            const descriptionElem = resultCard.querySelector('.result-description');
            descriptionElem.innerHTML = result.description;

            // Set event listeners for buttons
            const useAsInputBtn = resultCard.querySelector('.use-as-input-btn');
            const saveResultBtn = resultCard.querySelector('.save-result-btn');

            useAsInputBtn.addEventListener('click', () => useResultAsInput(result));
            saveResultBtn.addEventListener('click', () => saveResult(result));

            // Add card to results container with animation
            const resultContainer = document.createElement('div');
            resultContainer.className = 'col-md-6 mb-4 fade-in';
            resultContainer.style.animationDelay = (index * 0.1) + 's';
            resultContainer.appendChild(resultCard);
            resultsContainer.appendChild(resultContainer);
        });
    }

    // Use a result as input for further processing
    function useResultAsInput(result) {
        if (!originalImageContainer) return;
        
        // Create a prompt to confirm
        if (!confirm('Use this processed image as the new input? This will clear the current operation queue.')) {
            return;
        }

        // Show loading state
        const loadingMessage = document.createElement('div');
        loadingMessage.className = 'text-center p-3';
        loadingMessage.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Setting new input image...</p>';
        originalImageContainer.innerHTML = '';
        originalImageContainer.appendChild(loadingMessage);

        // Send request to save the processed image
        fetch('/save_processed', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: result.image,
                operation: result.operation
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update current image with the saved image
                currentImage = {
                    filename: data.filename,
                    width: result.width,
                    height: result.height,
                    image: result.image
                };

                // Reset UI state
                clearOperationQueue();
                if (resultsContainer) {
                    resultsContainer.innerHTML = '';
                }
                if (resultsSection) {
                    resultsSection.style.display = 'none';
                }
                if (comparisonSection) {
                    comparisonSection.style.display = 'none';
                }
                if (educationalSection) {
                    educationalSection.style.display = 'none';
                }

                // Update original image display
                updateOriginalImageDisplay();

                // Calculate image statistics
                if (imageHistogram && imageStatsText) {
                    calculateImageStatistics(currentImage);
                }

                // Scroll to top
                window.scrollTo({ top: 0, behavior: 'smooth' });

                // Show success toast
                showToast('Image set as new input', 'success');
            } else {
                showError('Failed to set new input: ' + data.error);
            }
        })
        .catch(error => {
            showError('Error setting new input: ' + error.message);
        });
    }

    // Update comparison view
    function updateComparisonView() {
        if (!comparisonOriginal || !comparisonFinal) return;
        
        // Set up the comparison slider
        if (currentImage && processingResults.length > 0) {
            // Get original and final images
            const originalImg = 'data:image/png;base64,' + currentImage.image;
            const finalResult = processingResults[processingResults.length - 1];
            const finalImg = 'data:image/png;base64,' + finalResult.image;

            // Set background images
            comparisonOriginal.innerHTML = `<img src="${originalImg}" class="img-fluid" alt="Original image">`;
            comparisonFinal.innerHTML = `<img src="${finalImg}" class="img-fluid" alt="Processed image">`;
        }
    }

    // Save a result image
    function saveResult(result) {
        // Create a temporary link element
        const link = document.createElement('a');
        link.href = 'data:image/png;base64,' + result.image;

        // Generate a filename
        const filename = result.operation + '_result.png';
        link.download = filename;

        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Show toast
        showToast('Image saved successfully', 'success');
    }

    // Show educational content for an operation
    function showEducationalContent(operation) {
        // Skip if educational section doesn't exist
        if (!educationalContent || !relatedConcepts || !mathematicalBackground) return;
        
        // Generate content based on operation
        const content = getEducationalContent(operation);

        // Set the content
        educationalContent.innerHTML = content.main;

        // Set related concepts
        relatedConcepts.innerHTML = '';
        content.related.forEach(concept => {
            const item = document.createElement('li');
            item.className = 'list-group-item';
            item.innerHTML = `<i class="bi bi-link-45deg me-2"></i>${concept}`;
            relatedConcepts.appendChild(item);
        });

        // Set mathematical background
        mathematicalBackground.innerHTML = content.math;
    }

    // Calculate and display image statistics
    function calculateImageStatistics(imageData) {
        if (!imageData || !imageHistogram || !imageStatsText) return;

        // This would typically compute histogram and statistics from the image data
        // For this implementation, we'll just display a placeholder

        imageStatsText.innerHTML = `
            <div class="d-flex flex-wrap justify-content-around">
                <div class="stat-box">
                    <span class="stat-label">Dimensions</span>
                    ${imageData.width} × ${imageData.height} px
                </div>
                <div class="stat-box">
                    <span class="stat-label">File Size</span>
                    ~${Math.round((imageData.image.length * 3) / 4 / 1024)} KB
                </div>
            </div>
        `;

        // A real implementation would calculate and display a histogram
        imageHistogram.innerHTML = '<p class="text-center text-muted">Histogram would be displayed here</p>';
    }

    // Get educational content for an operation
    function getEducationalContent(operation) {
        // Example for histogram equalization
        if (operation === 'histogram_equalization') {
            return {
                main: `
                    <h3>Histogram Equalization</h3>

                    <p>Histogram equalization is a technique for adjusting image intensities to enhance contrast. The method works by effectively spreading out the most frequent intensity values, resulting in a higher contrast image with a more uniform distribution of grayscale values.</p>

                    <h4>How It Works</h4>
                    <p>The algorithm works by:</p>
                    <ol>
                        <li>Calculating the histogram of the image</li>
                        <li>Computing the cumulative distribution function (CDF)</li>
                        <li>Mapping each pixel's intensity using the normalized CDF as a transformation function</li>
                    </ol>

                    <h4>Applications</h4>
                    <p>Histogram equalization is widely used in:</p>
                    <ul>
                        <li>Medical imaging to enhance details in X-rays and MRI scans</li>
                        <li>Satellite imaging to improve visibility of terrain features</li>
                        <li>Photography to correct underexposed or overexposed images</li>
                        <li>As a preprocessing step for other image processing operations</li>
                    </ul>

                    <h4>Limitations</h4>
                    <p>While powerful, histogram equalization has some limitations:</p>
                    <ul>
                        <li>May overamplify noise in relatively smooth regions</li>
                        <li>Global processing might not be optimal for images with varying lighting conditions</li>
                        <li>Can produce unnatural effects in color images if applied to each channel independently</li>
                    </ul>

                    <p>For images with varying lighting conditions, consider using Contrast Limited Adaptive Histogram Equalization (CLAHE) instead, which applies equalization to small regions rather than globally.</p>
                `,
                related: [
                    'CLAHE (Contrast Limited Adaptive Histogram Equalization)',
                    'Image Histograms',
                    'Cumulative Distribution Function',
                    'Contrast Adjustment',
                    'Probability Mass Function'
                ],
                math: `
                    <p>The transformation function used in histogram equalization is:</p>
                    <div class="math-formula">s_k = T(r_k) = (L-1) \\sum_{j=0}^{k} p_r(r_j)</div>
                    <p>Where:</p>
                    <ul>
                        <li>s_k is the new pixel value</li>
                        <li>r_k is the original pixel value</li>
                        <li>L is the number of gray levels (typically 256)</li>
                        <li>p_r(r_j) is the probability of pixel value r_j</li>
                    </ul>
                    <p>In practice, this is computed using:</p>
                    <div class="math-formula">s_k = \\frac{(L-1)}{MN} \\sum_{j=0}^{k} n_j</div>
                    <p>Where M×N is the image size and n_j is the frequency of pixel value j.</p>
                `
            };
        }

        // Default content for other operations
        return {
            main: `
                <h3>${formatOperationName(operation)}</h3>
                <p>This is a placeholder for detailed educational content about ${formatOperationName(operation)}.</p>
                <p>In a complete implementation, this section would include:</p>
                <ul>
                    <li>Detailed explanation of the operation and its working principles</li>
                    <li>Step-by-step breakdown of the algorithm</li>
                    <li>Illustrations and diagrams explaining the process</li>
                    <li>Common applications and use cases</li>
                    <li>Strengths and limitations of the approach</li>
                    <li>Comparison with similar techniques</li>
                    <li>Historical background and development of the technique</li>
                </ul>
            `,
            related: [
                'Related concept 1',
                'Related concept 2',
                'Related concept 3',
                'Related concept 4',
                'Related concept 5'
            ],
            math: `
                <p>This is a placeholder for mathematical explanations related to ${formatOperationName(operation)}.</p>
                <p>In a complete implementation, this would include:</p>
                <ul>
                    <li>Mathematical formulas and equations</li>
                    <li>Derivations and proofs</li>
                    <li>Algorithmic complexity analysis</li>
                    <li>Implementation considerations</li>
                </ul>
            `
        };
    }

    // Show a toast notification
    function showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.id = toastId;

        // Set toast content
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        // Add to container
        toastContainer.appendChild(toast);

        // Initialize and show the toast
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toastInstance = new bootstrap.Toast(toast, {
                autohide: true,
                delay: 3000
            });
            toastInstance.show();
        } else {
            // Fallback if bootstrap.Toast is not available
            toast.style.display = 'block';
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }

        // Remove toast from DOM after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }

    // Show error message
    function showError(message) {
        console.error("Error:", message);
        
        if (uploadStatus) {
            uploadStatus.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>${message}</div>`;

            // Clear after a delay
            setTimeout(() => {
                uploadStatus.innerHTML = '';
            }, 5000);
        }

        // Show as toast as well
        showToast(message, 'danger');
    }

    // ---- Utility Functions ----

    // Capitalize first letter of a string
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    // Format parameter name for display
    function formatParameterName(paramName) {
        return paramName
            .split('_')
            .map(word => capitalizeFirstLetter(word))
            .join(' ');
    }

    // Format operation name for display
    function formatOperationName(operationName) {
        return operationName
            .split('_')
            .map(word => capitalizeFirstLetter(word))
            .join(' ');
    }
});