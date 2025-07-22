import cv2
import numpy as np

class RestorationOperations:
    """Class containing image restoration operations"""
    
    def add_degradation(self, image, noise_type='gaussian', noise_param=25, blur_size=0):
        """Add controllable degradation to an image for restoration demos.
        
        Args:
            image: Input image
            noise_type: Type of noise to add ('gaussian', 'salt_pepper', 'speckle')
            noise_param: Parameter controlling noise intensity
            blur_size: Size of blur kernel (0 for no blur)
        """
        result = image.copy().astype(np.float32)
        
        # Apply blur if requested
        if blur_size > 0:
            # Ensure odd kernel size
            if blur_size % 2 == 0:
                blur_size += 1
            result = cv2.GaussianBlur(result, (blur_size, blur_size), 0)
        
        # Add noise
        if noise_type == 'gaussian':
            # Gaussian noise
            mean = 0
            sigma = noise_param
            noise = np.random.normal(mean, sigma, result.shape).astype(np.float32)
            result += noise
        elif noise_type == 'salt_pepper':
            # Salt and pepper noise
            amount = noise_param / 100.0  # Convert to proportion
            # Salt
            salt_mask = np.random.random(result.shape[:2]) < (amount / 2)
            result[salt_mask] = 255
            # Pepper
            pepper_mask = np.random.random(result.shape[:2]) < (amount / 2)
            result[pepper_mask] = 0
        elif noise_type == 'speckle':
            # Speckle noise (multiplicative)
            intensity = noise_param / 100.0
            noise = np.random.normal(0, intensity, result.shape).astype(np.float32)
            result += result * noise
        
        # Clip values
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        description = f"""
        <strong>Image Degradation</strong><br>
        Noise type: {noise_type}<br>
        Noise parameter: {noise_param}<br>
        Blur kernel size: {blur_size if blur_size > 0 else 'None'}<br><br>
        
        This operation adds controlled degradation to simulate real-world image quality issues:
        <ul>
            <li><strong>Gaussian noise:</strong> Random variations following a normal distribution (parameter: standard deviation)</li>
            <li><strong>Salt & Pepper noise:</strong> Random white and black pixels (parameter: percentage of affected pixels)</li>
            <li><strong>Speckle noise:</strong> Multiplicative noise commonly seen in radar and ultrasound (parameter: intensity)</li>
            <li><strong>Gaussian blur:</strong> Simulates out-of-focus or motion blur (parameter: kernel size)</li>
        </ul>
        
        Use this degraded image as input for restoration algorithms to evaluate their effectiveness.
        """
        
        return result, description
    
    def wiener_deconvolution(self, image, psf_size=5, noise_power=0.01):
        """Apply Wiener deconvolution for image restoration.
        
        Args:
            image: Input image (degraded)
            psf_size: Size of the point spread function kernel
            noise_power: Estimated noise power
        """
        # Convert to grayscale if not already
        if len(image.shape) > 2 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Create a simple PSF (Point Spread Function)
        # For simplicity, using a Gaussian kernel as the PSF
        psf = cv2.getGaussianKernel(psf_size, 0)
        psf = psf @ psf.T  # Outer product to get 2D kernel
        
        # Normalize PSF
        psf /= psf.sum()
        
        # Pad image and PSF for FFT
        padded_gray = np.pad(gray, ((psf_size, psf_size), (psf_size, psf_size)), 'reflect')
        padded_psf = np.pad(psf, ((0, padded_gray.shape[0] - psf.shape[0]), 
                                  (0, padded_gray.shape[1] - psf.shape[1])), 'constant')
        
        # Shift PSF to center
        padded_psf = np.roll(padded_psf, (-psf.shape[0]//2, -psf.shape[1]//2), axis=(0, 1))
        
        # FFT of image and PSF
        gray_fft = np.fft.fft2(padded_gray)
        psf_fft = np.fft.fft2(padded_psf)
        
        # Wiener deconvolution
        deconvolved = np.conj(psf_fft) / (np.abs(psf_fft)**2 + noise_power)
        deconvolved = gray_fft * deconvolved
        
        # Inverse FFT
        result = np.abs(np.fft.ifft2(deconvolved))
        
        # Crop to original size
        result = result[psf_size:-psf_size, psf_size:-psf_size]
        
        # Normalize
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Convert back to 3 channels for consistent display
        result_3ch = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        
        description = f"""
        <strong>Wiener Deconvolution</strong><br>
        PSF size: {psf_size}x{psf_size}<br>
        Noise power: {noise_power}<br><br>
        
        Wiener deconvolution is an image restoration technique that attempts to recover a degraded image by:
        <ul>
            <li>Estimating the original image using knowledge of the degradation process (PSF)</li>
            <li>Considering the noise present in the image</li>
            <li>Operating in the frequency domain using the Fourier transform</li>
        </ul>
        
        The algorithm:
        <ol>
            <li>Models image degradation as a convolution with a Point Spread Function (PSF)</li>
            <li>Operates in the frequency domain where convolution becomes multiplication</li>
            <li>Applies an optimal filter that balances noise amplification and restoration quality</li>
        </ol>
        
        Wiener filtering is used in:
        <ul>
            <li>Astronomical imaging</li>
            <li>Medical image processing</li>
            <li>Microscopy</li>
            <li>Photography restoration</li>
        </ul>
        
        The noise power parameter controls the trade-off between noise suppression and detail preservation.
        """
        
        return result_3ch, description
    
    def inpainting(self, image, mask_radius=20, num_points=5):
        """Apply inpainting to remove objects or restore damaged regions.
        
        Args:
            image: Input image
            mask_radius: Radius of mask points
            num_points: Number of random mask points to create
        """
        result = image.copy()
        
        # Create a mask for inpainting (random circular regions)
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        height, width = mask.shape
        for _ in range(num_points):
            # Generate random position
            x = np.random.randint(mask_radius, width - mask_radius)
            y = np.random.randint(mask_radius, height - mask_radius)
            
            # Draw circle on mask
            cv2.circle(mask, (x, y), mask_radius, 255, -1)
        
        # Apply mask to image to visualize damaged areas
        damaged = result.copy()
        damaged[mask == 255] = [0, 0, 255]  # Mark in red
        
        # Apply inpainting
        result = cv2.inpaint(result, mask, 3, cv2.INPAINT_TELEA)
        
        # Combine original damaged and inpainted for comparison
        display = np.hstack([damaged, result])
        
        description = f"""
        <strong>Image Inpainting</strong><br>
        Mask radius: {mask_radius}<br>
        Number of damaged areas: {num_points}<br><br>
        
        Left: Damaged image (red regions) | Right: Inpainted result<br><br>
        
        Image inpainting is the process of filling in missing or damaged regions in an image:
        <ul>
            <li>Uses information from surrounding pixels to reconstruct the damaged areas</li>
            <li>Preserves texture and structural continuity</li>
            <li>Works best when the damaged areas are relatively small</li>
        </ul>
        
        This implementation uses the Fast Marching Method (Telea algorithm) which:
        <ol>
            <li>Gradually fills the inpainting region from the boundary inward</li>
            <li>Propagates image information following a distance map</li>
            <li>Estimates pixel values based on nearby pixels and their gradients</li>
        </ol>
        
        Inpainting is widely used for:
        <ul>
            <li>Removing unwanted objects from photos</li>
            <li>Restoring damaged or scratched images</li>
            <li>Filling in missing regions in transmitted images</li>
            <li>Creating seamless panoramas</li>
        </ul>
        """
        
        return display, description