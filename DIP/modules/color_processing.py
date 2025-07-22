import cv2
import numpy as np

class ColorProcessing:
    """Class containing color space operations and analysis"""
    
    def rgb_to_hsv(self, image):
        """Convert image from RGB to HSV color space.
        
        Args:
            image: Input image (BGR)
        """
        result = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        description = """
        <strong>RGB to HSV Conversion</strong><br>
        This operation converts an image from RGB (Red, Green, Blue) to HSV (Hue, Saturation, Value) color space.
        <ul>
            <li>Hue: Color type (0-179 in OpenCV)</li>
            <li>Saturation: Color intensity (0-255)</li>
            <li>Value: Brightness (0-255)</li>
        </ul>
        HSV is particularly useful for color-based segmentation as it separates color information from lighting conditions.
        """
        
        return result, description
    
    def rgb_to_lab(self, image):
        """Convert image from RGB to LAB color space.
        
        Args:
            image: Input image (BGR)
        """
        result = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        description = """
        <strong>RGB to LAB Conversion</strong><br>
        This operation converts an image from RGB to LAB (CIELAB) color space.
        <ul>
            <li>L: Lightness (0-100)</li>
            <li>a: Green to Red (-128 to 127)</li>
            <li>b: Blue to Yellow (-128 to 127)</li>
        </ul>
        LAB color space is designed to be perceptually uniform and is device-independent, making it useful for color comparison and correction.
        """
        
        return result, description
    
    def rgb_to_ycrcb(self, image):
        """Convert image from RGB to YCrCb color space.
        
        Args:
            image: Input image (BGR)
        """
        result = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        
        description = """
        <strong>RGB to YCrCb Conversion</strong><br>
        This operation converts an image from RGB to YCrCb color space.
        <ul>
            <li>Y: Luminance component (brightness)</li>
            <li>Cr: Red chrominance component</li>
            <li>Cb: Blue chrominance component</li>
        </ul>
        YCrCb is widely used in video compression (JPEG, MPEG) as it separates luminance from chrominance information.
        """
        
        return result, description
    
    def channel_separation(self, image, color_space='RGB'):
        """Separate image into individual channels.
        
        Args:
            image: Input image (BGR)
            color_space: The color space to use ('RGB', 'HSV', 'LAB', 'YCrCb')
        """
        if color_space == 'RGB':
            # Use BGR for OpenCV
            spaces = ['Blue', 'Green', 'Red']
            channels = cv2.split(image)
        elif color_space == 'HSV':
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            spaces = ['Hue', 'Saturation', 'Value']
            channels = cv2.split(converted)
        elif color_space == 'LAB':
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            spaces = ['Lightness', 'A (Green-Red)', 'B (Blue-Yellow)']
            channels = cv2.split(converted)
        elif color_space == 'YCrCb':
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
            spaces = ['Y (Luminance)', 'Cr (Red Chroma)', 'Cb (Blue Chroma)']
            channels = cv2.split(converted)
        else:
            raise ValueError(f"Unsupported color space: {color_space}")
        
        # Create visualization with all channels side by side
        result = np.zeros_like(image)
        
        # Creating a 3-channel representation for each channel
        channel_images = []
        for i, channel in enumerate(channels):
            if len(channel.shape) == 2:  # Single channel
                temp = np.zeros_like(image)
                if color_space == 'RGB':
                    temp[:,:,i] = channel
                else:
                    # For non-RGB spaces, display as grayscale for better visibility
                    temp = cv2.cvtColor(channel, cv2.COLOR_GRAY2BGR)
                channel_images.append(temp)
        
        # Combine channels horizontally
        result = np.hstack(channel_images)
        
        description = f"""
        <strong>Channel Separation ({color_space})</strong><br>
        This operation separates the image into its individual {color_space} channels.
        <ul>
            <li>Left: {spaces[0]}</li>
            <li>Middle: {spaces[1]}</li>
            <li>Right: {spaces[2]}</li>
        </ul>
        Analyzing individual channels helps understand how color information is distributed and can assist in targeted image processing.
        """
        
        return result, description
    
    def color_quantization(self, image, k=8):
        """Reduce the number of colors in the image using K-means clustering.
        
        Args:
            image: Input image (BGR)
            k: Number of color clusters
        """
        # Reshape image for K-means
        pixels = image.reshape((-1, 3)).astype(np.float32)
        
        # Define criteria and apply K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert centers to uint8
        centers = np.uint8(centers)
        
        # Map each pixel to the corresponding center
        quantized = centers[labels.flatten()]
        
        # Reshape back to original image
        result = quantized.reshape(image.shape)
        
        description = f"""
        <strong>Color Quantization</strong><br>
        Colors reduced to: {k}<br><br>
        
        This operation reduces the number of colors in the image by using K-means clustering to group similar colors together.
        Each pixel is assigned to the nearest cluster center, resulting in an image with exactly {k} colors.
        
        Color quantization is useful for:
        <ul>
            <li>Image compression and file size reduction</li>
            <li>Creating artistic effects</li>
            <li>Simplifying image analysis</li>
            <li>Preparing images for certain display technologies</li>
        </ul>
        
        The algorithm works by iteratively finding the best {k} representative colors and mapping all pixels to their closest match.
        """
        
        return result, description