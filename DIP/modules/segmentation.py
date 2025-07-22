import cv2
import numpy as np

class SegmentationOperations:
    """Class containing image segmentation operations"""
    
    def canny_edge(self, image, threshold1=100, threshold2=200, aperture_size=3):
        """Apply Canny edge detection.
        
        Args:
            image: Input image
            threshold1: First threshold for hysteresis procedure
            threshold2: Second threshold for hysteresis procedure
            aperture_size: Aperture size for Sobel operator
        """
        # Convert to grayscale if not already
        if len(image.shape) > 2 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Apply Canny edge detection
        edges = cv2.Canny(gray, threshold1, threshold2, apertureSize=aperture_size)
        
        # Convert back to 3 channels for consistent display
        result = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        description = f"""
        <strong>Canny Edge Detection</strong><br>
        Lower Threshold: {threshold1}<br>
        Upper Threshold: {threshold2}<br>
        Aperture Size: {aperture_size}<br><br>
        
        Canny edge detection is a multi-stage algorithm that detects edges with minimal noise.
        The process involves:
        <ol>
          <li>Noise reduction with Gaussian blur</li>
          <li>Gradient calculation using Sobel operators</li>
          <li>Non-maximum suppression to thin edges</li>
          <li>Hysteresis thresholding using two thresholds</li>
        </ol>
        
        The thresholds determine edge sensitivity:
        <ul>
          <li>Lower threshold (threshold1): Weaker edges connected to strong edges are included</li>
          <li>Upper threshold (threshold2): Strong edges that form the definite edge skeleton</li>
        </ul>
        
        Canny edge detection excels at:
        <ul>
          <li>Detecting true edges with minimal noise</li>
          <li>Providing thin, well-connected edge contours</li>
          <li>Forming the basis for object detection and shape analysis</li>
        </ul>
        """
        
        return result, description
    
    def sobel_edge(self, image, dx=1, dy=1, ksize=3):
        """Apply Sobel edge detection.
        
        Args:
            image: Input image
            dx: Order of derivative in x direction
            dy: Order of derivative in y direction
            ksize: Size of Sobel kernel
        """
        # Convert to grayscale if not already
        if len(image.shape) > 2 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Calculate gradients
        sobelx = cv2.Sobel(gray, cv2.CV_64F, dx, 0, ksize=ksize)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, dy, ksize=ksize)
        
        # Calculate absolute gradients and convert to uint8
        abs_sobelx = cv2.convertScaleAbs(sobelx)
        abs_sobely = cv2.convertScaleAbs(sobely)
        
        # Combine gradients
        sobel_combined = cv2.addWeighted(abs_sobelx, 0.5, abs_sobely, 0.5, 0)
        
        # Convert back to 3 channels for consistent display
        result = cv2.cvtColor(sobel_combined, cv2.COLOR_GRAY2BGR)
        
        description = f"""
        <strong>Sobel Edge Detection</strong><br>
        X derivative order: {dx}<br>
        Y derivative order: {dy}<br>
        Kernel size: {ksize}<br><br>
        
        Sobel edge detection calculates the gradient of image intensity at each pixel.
        It uses two 3×3 kernels to approximate derivatives in horizontal and vertical directions.
        
        The Sobel operator:
        <ul>
          <li>Emphasizes regions of high spatial frequency (edges)</li>
          <li>Is less sensitive to noise compared to simple differentiation</li>
          <li>Provides both edge magnitude and direction information</li>
        </ul>
        
        This implementation:
        <ul>
          <li>Calculates separate x and y derivatives</li>
          <li>Takes the weighted average to combine them</li>
          <li>Shows edge strength but not direction</li>
        </ul>
        
        Sobel is computationally simple but can produce thicker edges than more advanced methods.
        """
        
        return result, description
    
    def watershed(self, image):
        """Apply watershed segmentation algorithm.
        
        This segments the image into different regions using the watershed algorithm.
        """
        # Convert to grayscale if not already
        if len(image.shape) > 2 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            if len(gray.shape) < 3:
                gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                image = gray_3ch
        
        # Apply Otsu's thresholding
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Noise removal with morphological opening
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Sure background area
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        
        # Finding sure foreground area
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        
        # Finding unknown region
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        
        # Marker labeling
        ret, markers = cv2.connectedComponents(sure_fg)
        
        # Add one to all labels so that background is not 0, but 1
        markers = markers + 1
        
        # Mark the unknown region with zero
        markers[unknown == 255] = 0
        
        # Apply watershed
        markers = cv2.watershed(image, markers)
        
        # Create visual result with colored regions
        result = image.copy()
        
        # Random colors for regions
        colors = []
        max_labels = np.max(markers)
        for i in range(max_labels + 1):
            colors.append((np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256)))
        
        # Color each segment with random color
        for i in range(2, max_labels + 1):
            result[markers == i] = colors[i]
            
        # Mark watershed boundaries in red
        result[markers == -1] = [0, 0, 255]
        
        description = """
        <strong>Watershed Segmentation</strong><br>
        The watershed algorithm treats the image as a topographic surface where:
        <ul>
          <li>Light pixels are high regions (hills)</li>
          <li>Dark pixels are low regions (valleys)</li>
        </ul>
        
        The process involves:
        <ol>
          <li>Initial thresholding and noise removal</li>
          <li>Distance transform to find centers of objects</li>
          <li>Marker creation for foreground and background</li>
          <li>Watershed transformation to find object boundaries</li>
        </ol>
        
        This implementation:
        <ul>
          <li>Uses random colors for different segments</li>
          <li>Shows watershed boundaries in red</li>
          <li>Automatically detects objects without manual marking</li>
        </ul>
        
        Watershed is particularly useful for segmenting touching or overlapping objects.
        """
        
        return result, description
    
    def contour_detection(self, image, threshold_min=127, threshold_max=255):
        """Detect and draw contours in an image.
        
        Args:
            image: Input image
            threshold_min: Lower threshold value for binary conversion
            threshold_max: Upper threshold value for binary conversion
        """
        # Convert to grayscale if not already
        if len(image.shape) > 2 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Apply threshold to get binary image
        ret, thresh = cv2.threshold(gray, threshold_min, threshold_max, cv2.THRESH_BINARY)
        
        # Find contours
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create result image
        result = image.copy() if len(image.shape) == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # Draw all contours
        cv2.drawContours(result, contours, -1, (0, 255, 0), 2)
        
        description = f"""
        <strong>Contour Detection</strong><br>
        Threshold Min: {threshold_min}<br>
        Threshold Max: {threshold_max}<br>
        Number of contours found: {len(contours)}<br><br>
        
        Contour detection identifies the boundaries of objects in an image.
        The process involves:
        <ol>
          <li>Converting to grayscale</li>
          <li>Thresholding to create a binary image</li>
          <li>Finding connected components (contours)</li>
          <li>Drawing detected contours on the original image</li>
        </ol>
        
        Each contour represents a curve joining all continuous points along a boundary with the same intensity.
        
        Contour detection is useful for:
        <ul>
          <li>Shape analysis</li>
          <li>Object detection and counting</li>
          <li>Feature extraction</li>
          <li>Object tracking</li>
        </ul>
        
        In this visualization, contours are drawn in green over the original image.
        """
        
        return result, description
    
    def orb_keypoints(self, image, n_features=500):
        """Detect and display ORB keypoints.
        
        Args:
            image: Input image
            n_features: Maximum number of features to retain
        """
        # Initialize ORB detector
        orb = cv2.ORB_create(nfeatures=n_features)
        
        # Find keypoints
        keypoints = orb.detect(image, None)
        
        # Compute descriptors
        keypoints, descriptors = orb.compute(image, keypoints)
        
        # Draw keypoints
        result = cv2.drawKeypoints(image, keypoints, None, color=(0, 255, 0), 
                                  flags=cv2.DrawMatchesFlags_DRAW_RICH_KEYPOINTS)
        
        description = f"""
        <strong>ORB Keypoint Detection</strong><br>
        Maximum Features: {n_features}<br>
        Keypoints found: {len(keypoints)}<br><br>
        
        ORB (Oriented FAST and Rotated BRIEF) is a fast, efficient alternative to SIFT and SURF
        for keypoint detection and description.
        
        The algorithm:
        <ol>
          <li>Uses FAST for keypoint detection</li>
          <li>Computes orientation using intensity centroid</li>
          <li>Uses modified BRIEF descriptors that are rotation-invariant</li>
        </ol>
        
        ORB keypoints are useful for:
        <ul>
          <li>Feature matching between images</li>
          <li>Object recognition</li>
          <li>Image alignment</li>
          <li>3D reconstruction</li>
        </ul>
        
        The green circles represent detected keypoints, with size indicating scale and line indicating orientation.
        """
        
        return result, description