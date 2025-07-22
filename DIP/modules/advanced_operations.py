import cv2
import numpy as np

class AdvancedOperations:
    """Class containing advanced image processing operations"""
    
    def retinex(self, image, sigma_list=[15, 80, 250], dynamic=False):
        """Apply Multi-Scale Retinex (MSR) algorithm for image enhancement.
        
        Args:
            image: Input image
            sigma_list: List of standard deviations for Gaussian blur
            dynamic: Whether to use dynamic color restoration
        
        Args:
            image: Input image
            sigma_list: List of standard deviations for Gaussian blur
            dynamic: Whether to use dynamic color restoration
        """
        # Convert BGR to float32
        img_float = np.float32(image) / 255.0
        
        # Process each channel separately
        channels = []
        for ch in cv2.split(img_float):
            # Initialize the sum for MSR
            retinex = np.zeros_like(ch)
            
            # Process for each scale (sigma)
            for sigma in sigma_list:
                # Calculate Gaussian blur
                blur = cv2.GaussianBlur(ch, (0, 0), sigma)
                # Avoid log(0)
                blur = np.where(blur < 0.0001, 0.0001, blur)
                # Compute retinex for this scale and add to sum
                retinex += np.log10(ch + 0.01) - np.log10(blur + 0.01)
                
            # Normalize by number of scales
            retinex = retinex / len(sigma_list)
            
            # Apply dynamic color restoration if requested
            if dynamic:
                # Simple color restoration based on the original color ratios
                restoration = np.log10((ch + 0.01) / (np.sum(img_float, axis=2) / 3 + 0.01))
                retinex = retinex * restoration
            
            # Normalize to 0-1 range
            min_val = np.min(retinex)
            max_val = np.max(retinex)
            range_val = max_val - min_val
            if range_val > 0:
                retinex = (retinex - min_val) / range_val
            
            channels.append(retinex)
        
        # Merge channels
        result = cv2.merge(channels)
        
        # Convert to uint8
        result = np.uint8(result * 255)
        
        description = f"""
        <strong>Multi-Scale Retinex (MSR)</strong><br>
        Sigma values: {sigma_list}<br>
        Dynamic color restoration: {'Enabled' if dynamic else 'Disabled'}<br><br>
        
        The Retinex algorithm enhances image appearance by improving local contrast and dynamic range.
        It's based on the human visual system's ability to perceive colors consistently regardless of lighting conditions.
        
        The Multi-Scale Retinex (MSR) algorithm:
        <ol>
          <li>Processes the image at multiple scales (controlled by sigma values)</li>
          <li>For each scale, calculates log(image) - log(blurred image)</li>
          <li>Combines the results from different scales</li>
          <li>Optional dynamic color restoration preserves color relationships</li>
        </ol>
        
        MSR is particularly effective for enhancing images with poor lighting conditions, shadows, or backlighting.
        """
        
        return result, description
    
    def clahe(self, image, clip_limit=2.0, tile_grid_size=8):
        """Apply Contrast Limited Adaptive Histogram Equalization (CLAHE).
        
        Args:
            image: Input image
            clip_limit: Threshold for contrast limiting
            tile_grid_size: Size of grid for histogram equalization
        """
        # Convert to LAB color space for color images
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Convert to LAB, equalize L channel, convert back
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
            l_clahe = clahe.apply(l)
            
            # Merge channels and convert back to BGR
            merged = cv2.merge([l_clahe, a, b])
            result = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        else:
            # Grayscale
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
            result = clahe.apply(image)
            # Convert back to 3 channels for consistent display
            if len(result.shape) < 3:
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
                
        description = f"""
        <strong>Contrast Limited Adaptive Histogram Equalization (CLAHE)</strong><br>
        Clip Limit: {clip_limit}<br>
        Tile Grid Size: {tile_grid_size}x{tile_grid_size}<br><br>
        
        CLAHE is an advanced form of adaptive histogram equalization that limits contrast enhancement to 
        reduce noise amplification. The algorithm divides the image into small tiles and applies histogram 
        equalization to each tile. Contrast limiting (clip limit) prevents over-amplification of noise by 
        redistributing values above the clip limit equally across the histogram.
        
        For color images, CLAHE is applied only to the luminance channel in LAB color space to preserve
        color relationships. CLAHE provides better local contrast enhancement than standard histogram
        equalization, especially for images with varying lighting conditions.
        """
        
        return result, description
    
    def fourier_transform(self, image):
        """Display the Fourier transform of an image.
        
        Shows the magnitude spectrum of the image's frequency domain representation.
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Get optimal size for DFT
        rows, cols = gray.shape
        optimal_rows = cv2.getOptimalDFTSize(rows)
        optimal_cols = cv2.getOptimalDFTSize(cols)
        
        # Pad image to optimal size
        padded = cv2.copyMakeBorder(gray, 0, optimal_rows - rows, 0, optimal_cols - cols, 
                                   cv2.BORDER_CONSTANT, value=0)
        
        # Perform DFT
        dft = cv2.dft(np.float32(padded), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        
        # Calculate magnitude spectrum
        magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:,:,0], dft_shift[:,:,1]) + 1)
        
        # Normalize to 0-255
        magnitude_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        
        # Convert to 3 channels for display
        result = cv2.cvtColor(magnitude_spectrum, cv2.COLOR_GRAY2BGR)
        
        description = """
        <strong>Fourier Transform (Magnitude Spectrum)</strong><br>
        The Fourier Transform decomposes an image into its frequency components, showing
        how much information is present at different frequencies. The result displayed is
        the magnitude spectrum (log-scaled for better visualization).<br><br>
        
        In the frequency domain representation:
        <ul>
          <li>The center of the image represents low frequencies (overall image structure)</li>
          <li>The edges represent high frequencies (fine details and edges)</li>
          <li>Bright points indicate strong frequency components</li>
        </ul>
        
        The Fourier Transform is fundamental to many image processing operations like
        filtering, compression, and feature extraction.
        """
        
        return result, description
    
    def frequency_filter(self, image, filter_type='lowpass', cutoff_freq=30):
        """Apply frequency domain filtering (lowpass/highpass).
        
        Args:
            image: Input image
            filter_type: 'lowpass' or 'highpass'
            cutoff_freq: Cutoff frequency (radius)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Get optimal size for DFT
        rows, cols = gray.shape
        optimal_rows = cv2.getOptimalDFTSize(rows)
        optimal_cols = cv2.getOptimalDFTSize(cols)
        
        # Pad image to optimal size
        padded = cv2.copyMakeBorder(gray, 0, optimal_rows - rows, 0, optimal_cols - cols, 
                                   cv2.BORDER_CONSTANT, value=0)
        
        # Perform DFT
        dft = cv2.dft(np.float32(padded), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        
        # Create mask (filter)
        crow, ccol = dft_shift.shape[0] // 2, dft_shift.shape[1] // 2
        mask = np.zeros((dft_shift.shape[0], dft_shift.shape[1]), np.uint8)
        
        if filter_type.lower() == 'lowpass':
            cv2.circle(mask, (ccol, crow), cutoff_freq, 1, -1)
            filter_name = "Low-Pass"
        else:  # highpass
            cv2.circle(mask, (ccol, crow), cutoff_freq, 1, -1)
            mask = 1 - mask
            filter_name = "High-Pass"
            
        # Apply mask to both real and imaginary parts
        mask = np.stack([mask, mask], axis=2)
        filtered_dft = dft_shift * mask
        
        # Inverse DFT
        filtered_shift = np.fft.ifftshift(filtered_dft)
        filtered_img = cv2.idft(filtered_shift)
        filtered_img = cv2.magnitude(filtered_img[:,:,0], filtered_img[:,:,1])
        
        # Normalize and convert to uint8
        filtered_img = cv2.normalize(filtered_img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        
        # Crop to original size
        filtered_img = filtered_img[:rows, :cols]
        
        # Convert to 3 channels for display
        result = cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
        
        description = f"""
        <strong>Frequency Domain {filter_name} Filtering</strong><br>
        Cutoff Frequency: {cutoff_freq}<br><br>
        
        This operation filters the image in the frequency domain using a {filter_name.lower()} filter.
        The process involves:
        <ol>
          <li>Converting the image to the frequency domain using Fourier Transform</li>
          <li>Applying a mask that keeps only frequencies below (lowpass) or above (highpass) the cutoff</li>
          <li>Converting back to the spatial domain using Inverse Fourier Transform</li>
        </ol>
        
        Low-pass filtering removes high-frequency components (fine details and noise), resulting in a blurred image.
        High-pass filtering removes low-frequency components (overall structure), enhancing edges and fine details.
        """