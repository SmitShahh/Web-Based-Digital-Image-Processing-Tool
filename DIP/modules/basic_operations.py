import cv2
import numpy as np

class BasicOperations:
    """Class containing basic image processing operations"""
    
    def grayscale(self, image):
        """Convert an image to grayscale.
        
        Uses OpenCV's cvtColor function to convert from BGR to grayscale.
        """
        result = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Convert back to 3 channels for consistent display
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        
        description = """
        <strong>Grayscale Conversion</strong><br>
        This operation converts a color image to grayscale by removing all color information.
        Each pixel's intensity is calculated from its RGB values using the formula:<br>
        <code>Y = 0.299*R + 0.587*G + 0.114*B</code><br>
        Grayscale is often used as a preprocessing step for many image processing algorithms.
        """
        
        return result, description
    
    def negative(self, image):
        """Create a negative of the image.
        
        Inverts all pixel values by subtracting from the maximum possible value.
        """
        result = 255 - image
        
        description = """
        <strong>Negative Image</strong><br>
        The negative operation inverts all pixel values by subtracting them from the maximum possible value (255).
        This creates an effect similar to a photographic negative where dark areas become light and vice versa.
        Mathematically: <code>g(x,y) = 255 - f(x,y)</code> for each pixel location (x,y).
        """
        
        return result, description
    
    def threshold(self, image, threshold_value=127, max_value=255, threshold_type=cv2.THRESH_BINARY):
        """Apply thresholding to an image.
        
        Args:
            image: Input image
            threshold_value: Threshold value (0-255)
            max_value: Maximum value to use
            threshold_type: OpenCV threshold type
        """
        # Convert to grayscale if not already
        if len(image.shape) > 2 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        ret, result = cv2.threshold(gray, threshold_value, max_value, threshold_type)
        
        # Convert back to 3 channels for consistent display
        if len(result.shape) < 3:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        
        threshold_types = {
            cv2.THRESH_BINARY: "Binary",
            cv2.THRESH_BINARY_INV: "Binary Inverted",
            cv2.THRESH_TRUNC: "Truncate",
            cv2.THRESH_TOZERO: "To Zero",
            cv2.THRESH_TOZERO_INV: "To Zero Inverted"
        }
        
        threshold_type_name = threshold_types.get(threshold_type, "Unknown")
        
        description = f"""
        <strong>Thresholding ({threshold_type_name})</strong><br>
        Threshold value: {threshold_value}<br>
        Max value: {max_value}<br><br>
        
        Thresholding creates a binary image by setting all pixels above a threshold value to 
        one value (typically white) and all pixels below the threshold to another value (typically black).
        This is useful for segmentation, extracting objects from backgrounds, and converting grayscale
        images to binary for further processing.
        """
        
        return result, description
    
    def adjust_brightness(self, image, beta=50):
        """Adjust image brightness by adding a constant value.
        
        Args:
            image: Input image
            beta: Brightness adjustment value (-255 to 255)
        """
        result = cv2.convertScaleAbs(image, alpha=1, beta=beta)
        
        description = f"""
        <strong>Brightness Adjustment</strong><br>
        Adjustment value: {beta}<br><br>
        
        This operation adjusts the brightness of an image by adding a constant value (beta) to each pixel.
        Positive values increase brightness while negative values decrease it.
        Mathematically: <code>g(x,y) = f(x,y) + beta</code> (with clipping to stay within valid range).
        """
        
        return result, description
    
    def adjust_contrast(self, image, alpha=1.5):
        """Adjust image contrast by multiplying by a constant value.
        
        Args:
            image: Input image
            alpha: Contrast adjustment factor (0.0-3.0)
        """
        result = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
        
        description = f"""
        <strong>Contrast Adjustment</strong><br>
        Adjustment factor: {alpha}<br><br>
        
        This operation adjusts the contrast of an image by multiplying each pixel by a constant value (alpha).
        Values greater than 1 increase contrast while values between 0 and 1 decrease contrast.
        Mathematically: <code>g(x,y) = alpha * f(x,y)</code> (with clipping to stay within valid range).
        """
        
        return result, description
    
    def gaussian_blur(self, image, kernel_size=5, sigma_x=0):
        """Apply Gaussian blur to an image.
        
        Args:
            image: Input image
            kernel_size: Size of Gaussian kernel (must be odd)
            sigma_x: Standard deviation in X direction
        """
        # Ensure kernel size is odd
        if kernel_size % 2 == 0:
            kernel_size += 1
            
        result = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma_x)
        
        description = f"""
        <strong>Gaussian Blur</strong><br>
        Kernel size: {kernel_size}x{kernel_size}<br>
        Sigma X: {sigma_x}<br><br>
        
        Gaussian blur smooths an image by convolving it with a Gaussian filter. 
        The Gaussian filter uses a weighted average where central pixels have higher weights.
        This is commonly used for noise reduction and as a preprocessing step for edge detection.
        The kernel size determines the neighborhood size for blurring, while sigma controls the 
        standard deviation of the Gaussian distribution (larger sigma means more blur).
        """
        
        return result, description
    
    def median_blur(self, image, kernel_size=5):
        """Apply median blur to an image.
        
        Args:
            image: Input image
            kernel_size: Size of median filter kernel (must be odd)
        """
        # Ensure kernel size is odd
        if kernel_size % 2 == 0:
            kernel_size += 1
            
        result = cv2.medianBlur(image, kernel_size)
        
        description = f"""
        <strong>Median Blur</strong><br>
        Kernel size: {kernel_size}x{kernel_size}<br><br>
        
        Median blur replaces each pixel with the median value from its neighborhood defined by the kernel size.
        Unlike Gaussian blur, median filtering is particularly effective at removing salt-and-pepper noise
        while preserving edges. It's a non-linear filter that doesn't create new pixel values, making it
        suitable for removing outliers without affecting the overall image structure.
        """
        
        return result, description
    
    def bilateral_filter(self, image, d=9, sigma_color=75, sigma_space=75):
        """Apply bilateral filter to an image.
        
        Args:
            image: Input image
            d: Diameter of each pixel neighborhood
            sigma_color: Filter sigma in the color space
            sigma_space: Filter sigma in the coordinate space
        """
        result = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
        
        description = f"""
        <strong>Bilateral Filter</strong><br>
        Diameter: {d}<br>
        Sigma Color: {sigma_color}<br>
        Sigma Space: {sigma_space}<br><br>
        
        The bilateral filter is an edge-preserving smoothing filter that combines spatial proximity and color 
        similarity. Unlike standard Gaussian blur, it preserves edges while smoothing other regions.
        It considers both the spatial distance (sigma_space) and color difference (sigma_color) when calculating 
        the weights for neighborhood pixels. This makes it excellent for noise reduction while preserving 
        important image details.
        """
        
        return result, description
    
    def histogram_equalization(self, image):
        """Apply histogram equalization to enhance image contrast.
        
        This method works best on grayscale images but is applied to each channel
        separately for color images.
        """
        # Handle grayscale vs color
        if len(image.shape) == 2 or image.shape[2] == 1:
            # Grayscale
            result = cv2.equalizeHist(image)
            if len(result.shape) < 3:
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        else:
            # Color - convert to YCrCb, equalize Y channel, convert back
            ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
            ycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])
            result = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        
        description = """
        <strong>Histogram Equalization</strong><br>
        Histogram equalization enhances image contrast by effectively spreading out the most frequent 
        intensity values across the entire intensity range (0-255). It's particularly useful for 
        images with poor contrast due to under or overexposure.<br><br>
        
        The operation redistributes pixel intensities to make the image histogram more uniform.
        For color images, this implementation converts to YCrCb color space and equalizes only the 
        luminance (Y) channel to preserve the color balance.
        """
        
        return result, description
    
    def sharpen(self, image, kernel_size=3, strength=1.0):
        """Sharpen an image using unsharp masking.
        
        Args:
            image: Input image
            kernel_size: Size of Gaussian blur kernel used in unsharp masking
            strength: Strength of sharpening effect (0.0-3.0)
        """
        # Create a blurred version of the image
        if kernel_size % 2 == 0:
            kernel_size += 1
            
        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        
        # Unsharp masking: subtract blurred image from original
        unsharp_mask = cv2.addWeighted(image, 1.0 + strength, blurred, -strength, 0)
        
        description = f"""
        <strong>Unsharp Masking (Sharpening)</strong><br>
        Kernel size: {kernel_size}<br>
        Strength: {strength}<br><br>
        
        Sharpening enhances edges and fine details in an image by increasing local contrast.
        This implementation uses unsharp masking, where a blurred (unsharp) version is subtracted 
        from the original image. The result is an image with emphasized high-frequency components (edges).
        
        Mathematically: <code>g(x,y) = f(x,y) + strength * (f(x,y) - blurred(x,y))</code>
        
        Higher strength values create a more pronounced sharpening effect.
        """
        
        return unsharp_mask, description