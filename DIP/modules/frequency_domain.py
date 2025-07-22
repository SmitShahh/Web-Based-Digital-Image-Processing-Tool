import cv2
import numpy as np

class FrequencyDomain:
    """Class containing frequency domain image processing operations"""
    
    def visualize_spectrum(self, image):
        """Visualize the Fourier spectrum with magnitude and phase.
        
        Args:
            image: Input image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Calculate DFT
        dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        
        # Calculate magnitude spectrum and phase
        magnitude = cv2.magnitude(dft_shift[:,:,0], dft_shift[:,:,1])
        phase = cv2.phase(dft_shift[:,:,0], dft_shift[:,:,1])
        
        # Convert to logarithmic scale for better visualization
        magnitude = 20 * np.log(magnitude + 1)
        
        # Normalize for display
        magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        phase = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        
        # Create colored visualizations
        magnitude_colored = cv2.applyColorMap(magnitude, cv2.COLORMAP_JET)
        phase_colored = cv2.applyColorMap(phase, cv2.COLORMAP_JET)
        
        # Combine for visualization
        result = np.hstack([magnitude_colored, phase_colored])
        
        description = """
        <strong>Fourier Spectrum Visualization</strong><br>
        Left: Magnitude Spectrum (log scale) | Right: Phase Spectrum<br><br>
        
        The Discrete Fourier Transform (DFT) converts an image from the spatial domain to the frequency domain, revealing:
        
        <ul>
            <li><strong>Magnitude Spectrum:</strong> Shows the strength of different frequencies.
                <ul>
                    <li>Center: Low frequencies (overall structure)</li>
                    <li>Edges: High frequencies (details and edges)</li>
                    <li>Bright spots: Strong frequency components</li>
                </ul>
            </li>
            <li><strong>Phase Spectrum:</strong> Contains information about the position of features.
                <ul>
                    <li>Critical for preserving image structure</li>
                    <li>Changes in phase severely distort the image</li>
                </ul>
            </li>
        </ul>
        
        <strong>Interpreting the Spectrum:</strong>
        <ul>
            <li>Horizontal lines in the image appear as vertical components in the spectrum</li>
            <li>Vertical lines appear as horizontal components</li>
            <li>Diagonal components maintain their orientation</li>
            <li>Periodic patterns create bright spots at corresponding frequencies</li>
        </ul>
        """
        
        return result, description
    
    def bandpass_filter(self, image, low_cutoff=10, high_cutoff=50):
        """Apply a bandpass filter in the frequency domain.
        
        Args:
            image: Input image
            low_cutoff: Low frequency cutoff radius
            high_cutoff: High frequency cutoff radius
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
        
        # Pad image
        padded = cv2.copyMakeBorder(gray, 0, optimal_rows - rows, 0, optimal_cols - cols, 
                                   cv2.BORDER_CONSTANT, value=0)
        
        # Perform DFT
        dft = cv2.dft(np.float32(padded), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        
        # Create bandpass mask
        crow, ccol = dft_shift.shape[0] // 2, dft_shift.shape[1] // 2
        mask = np.zeros((dft_shift.shape[0], dft_shift.shape[1]), np.uint8)
        
        # Draw filled circle for high cutoff (low-pass)
        cv2.circle(mask, (ccol, crow), high_cutoff, 1, -1)
        
        # Draw filled circle for low cutoff (high-pass)
        cv2.circle(mask, (ccol, crow), low_cutoff, 0, -1)
        
        # Create mask for complex numbers (both real and imaginary parts)
        mask = np.stack([mask, mask], axis=2)
        
        # Apply mask
        filtered_dft = dft_shift * mask
        
        # Inverse shift
        filtered_shift = np.fft.ifftshift(filtered_dft)
        
        # Inverse DFT
        filtered_img = cv2.idft(filtered_shift)
        filtered_img = cv2.magnitude(filtered_img[:,:,0], filtered_img[:,:,1])
        
        # Normalize and convert to uint8
        filtered_img = cv2.normalize(filtered_img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        
        # Crop to original size
        filtered_img = filtered_img[:rows, :cols]
        
        # Convert back to 3 channels for consistent display
        result = cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
        
        description = f"""
        <strong>Bandpass Filtering</strong><br>
        Low cutoff frequency: {low_cutoff}<br>
        High cutoff frequency: {high_cutoff}<br><br>
        
        Bandpass filtering retains a specific range of frequencies while removing others.
        <ul>
            <li>Frequencies below {low_cutoff} are removed (high-pass component)</li>
            <li>Frequencies above {high_cutoff} are removed (low-pass component)</li>
            <li>Only frequencies between {low_cutoff} and {high_cutoff} are preserved</li>
        </ul>
        
        This is useful for:
        <ul>
            <li>Isolating specific texture patterns</li>
            <li>Removing both low-frequency background variations and high-frequency noise</li>
            <li>Enhancing mid-frequency features like edges of a certain scale</li>
            <li>Medical imaging to isolate structures of specific sizes</li>
        </ul>
        
        The process works by converting the image to the frequency domain using DFT, applying a ring-shaped mask,
        and then converting back to the spatial domain using inverse DFT.
        """
        
        return result, description
    
    def notch_filter(self, image, notch_x=None, notch_y=None, notch_radius=10):
        """Apply a notch filter to remove specific frequency components.
        
        Args:
            image: Input image
            notch_x, notch_y: Coordinates of notch centers (if None, calculated automatically)
            notch_radius: Radius of notch filter
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
        
        # Pad image
        padded = cv2.copyMakeBorder(gray, 0, optimal_rows - rows, 0, optimal_cols - cols, 
                                   cv2.BORDER_CONSTANT, value=0)
        
        # Perform DFT
        dft = cv2.dft(np.float32(padded), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        
        # Calculate magnitude spectrum
        magnitude = 20 * np.log(cv2.magnitude(dft_shift[:,:,0], dft_shift[:,:,1]) + 1)
        
        # Find notch positions automatically if not provided
        if notch_x is None or notch_y is None:
            # Simple peak finding in the magnitude spectrum
            # (excluding the DC component at the center)
            crow, ccol = magnitude.shape[0] // 2, magnitude.shape[1] // 2
            center_mask = np.ones_like(magnitude)
            cv2.circle(center_mask, (ccol, crow), 20, 0, -1)  # Mask out center
            
            # Find the location of the maximum value
            _, max_val, _, max_loc = cv2.minMaxLoc(magnitude * center_mask)
            notch_x, notch_y = max_loc
            
            # Find symmetric point across center
            sym_x = 2 * ccol - notch_x
            sym_y = 2 * crow - notch_y
        else:
            crow, ccol = magnitude.shape[0] // 2, magnitude.shape[1] // 2
            sym_x = 2 * ccol - notch_x
            sym_y = 2 * crow - notch_y
        
        # Create notch filter mask
        mask = np.ones((dft_shift.shape[0], dft_shift.shape[1]), np.uint8)
        
        # Apply notch at the identified frequency component and its symmetric counterpart
        cv2.circle(mask, (notch_x, notch_y), notch_radius, 0, -1)
        cv2.circle(mask, (sym_x, sym_y), notch_radius, 0, -1)
        
        # Create mask for complex numbers
        mask = np.stack([mask, mask], axis=2)
        
        # Apply mask
        filtered_dft = dft_shift * mask
        
        # Inverse shift
        filtered_shift = np.fft.ifftshift(filtered_dft)
        
        # Inverse DFT
        filtered_img = cv2.idft(filtered_shift)
        filtered_img = cv2.magnitude(filtered_img[:,:,0], filtered_img[:,:,1])
        
        # Normalize and convert to uint8
        filtered_img = cv2.normalize(filtered_img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        
        # Crop to original size
        filtered_img = filtered_img[:rows, :cols]
        
        # Convert back to 3 channels for consistent display
        result = cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
        
        description = f"""
        <strong>Notch Filtering</strong><br>
        Notch center: ({notch_x}, {notch_y}) and ({sym_x}, {sym_y})<br>
        Notch radius: {notch_radius}<br><br>
        
        Notch filtering removes specific frequency components that often correspond to periodic noise patterns.
        <ul>
            <li>Particularly effective for removing regular patterns like scan lines, grid artifacts, or moire patterns</li>
            <li>Preserves all other frequency content, minimizing impact on image quality</li>
            <li>Both the frequency component and its symmetric counterpart are removed to maintain balance</li>
        </ul>
        
        This is useful for:
        <ul>
            <li>Removing periodic noise from scanned images</li>
            <li>Cleaning up images of textured products or fabrics</li>
            <li>Preprocessing for microscopy or scientific imaging</li>
        </ul>
        
        The notch positions were {'automatically detected' if notch_x is None else 'manually specified'} 
        based on the strongest frequency components outside the DC (zero frequency) region.
        """
        
        return result, description