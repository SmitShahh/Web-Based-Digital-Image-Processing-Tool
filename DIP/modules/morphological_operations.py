import cv2
import numpy as np

class MorphologicalOperations:
    """Class containing morphological image processing operations"""
    
    def __get_kernel(self, kernel_shape, kernel_size):
        """Helper function to create kernel of specified shape and size.
        
        Args:
            kernel_shape: 'rect', 'ellipse', or 'cross'
            kernel_size: Size of the kernel
        """
        if kernel_shape == 'rect':
            return cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        elif kernel_shape == 'ellipse':
            return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        elif kernel_shape == 'cross':
            return cv2.getStructuringElement(cv2.MORPH_CROSS, (kernel_size, kernel_size))
        else:
            # Default to rectangular
            return cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    
    def erosion(self, image, kernel_size=5, kernel_shape='rect', iterations=1):
        """Apply erosion morphological operation.
        
        Args:
            image: Input image
            kernel_size: Size of structuring element
            kernel_shape: Shape of kernel ('rect', 'ellipse', 'cross')
            iterations: Number of times to apply the operation
        """
        # Get appropriate kernel
        kernel = self.__get_kernel(kernel_shape, kernel_size)
        
        # Apply erosion
        result = cv2.erode(image, kernel, iterations=iterations)
        
        description = f"""
        <strong>Erosion</strong><br>
        Kernel shape: {kernel_shape}<br>
        Kernel size: {kernel_size}x{kernel_size}<br>
        Iterations: {iterations}<br><br>
        
        Erosion is a fundamental morphological operation that shrinks bright regions and 
        enlarges dark regions. It works by replacing each pixel with the minimum value in 
        its neighborhood defined by the structuring element (kernel).
        
        Main effects of erosion:
        <ul>
          <li>Removes small objects and fine protrusions</li>
          <li>Separates connected objects</li>
          <li>Shrinks object boundaries</li>
          <li>Eliminates small noise (like salt noise)</li>
        </ul>
        
        Erosion is particularly useful for:
        <ul>
          <li>Removing small noise from binary images</li>
          <li>Shrinking foreground objects</li>
          <li>Breaking connections between connected objects</li>
        </ul>
        """
        
        return result, description
    
    def dilation(self, image, kernel_size=5, kernel_shape='rect', iterations=1):
        """Apply dilation morphological operation.
        
        Args:
            image: Input image
            kernel_size: Size of structuring element
            kernel_shape: Shape of kernel ('rect', 'ellipse', 'cross')
            iterations: Number of times to apply the operation
        """
        # Get appropriate kernel
        kernel = self.__get_kernel(kernel_shape, kernel_size)
        
        # Apply dilation
        result = cv2.dilate(image, kernel, iterations=iterations)
        
        description = f"""
        <strong>Dilation</strong><br>
        Kernel shape: {kernel_shape}<br>
        Kernel size: {kernel_size}x{kernel_size}<br>
        Iterations: {iterations}<br><br>
        
        Dilation is a fundamental morphological operation that enlarges bright regions and 
        shrinks dark regions. It works by replacing each pixel with the maximum value in 
        its neighborhood defined by the structuring element (kernel).
        
        Main effects of dilation:
        <ul>
          <li>Enlarges objects</li>
          <li>Fills in small holes</li>
          <li>Connects broken parts of objects</li>
          <li>Eliminates small dark spots (like pepper noise)</li>
        </ul>
        
        Dilation is particularly useful for:
        <ul>
          <li>Filling in small holes in objects</li>
          <li>Connecting nearby objects</li>
          <li>Expanding foreground regions</li>
          <li>Removing small dark spots from images</li>
        </ul>
        """
        
        return result, description
    
    def opening(self, image, kernel_size=5, kernel_shape='rect'):
        """Apply opening morphological operation (erosion followed by dilation).
        
        Args:
            image: Input image
            kernel_size: Size of structuring element
            kernel_shape: Shape of kernel ('rect', 'ellipse', 'cross')
        """
        # Get appropriate kernel
        kernel = self.__get_kernel(kernel_shape, kernel_size)
        
        # Apply opening (erosion followed by dilation)
        result = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        
        description = f"""
        <strong>Opening</strong><br>
        Kernel shape: {kernel_shape}<br>
        Kernel size: {kernel_size}x{kernel_size}<br><br>
        
        Opening is a morphological operation that consists of an erosion followed by a dilation.
        It's named "opening" because it opens or breaks narrow connections and enlarges small holes.
        
        Main effects of opening:
        <ul>
          <li>Removes small objects and protrusions</li>
          <li>Preserves the shape and size of larger objects</li>
          <li>Smooths object contours</li>
          <li>Removes thin connections between objects</li>
        </ul>
        
        Opening is particularly useful for:
        <ul>
          <li>Removing small noise while preserving object shape</li>
          <li>Breaking thin connections between objects</li>
          <li>Smoothing object boundaries without significant size reduction</li>
        </ul>
        
        Mathematically: Opening(A, B) = Dilation(Erosion(A, B), B), where A is the image and B is the structuring element.
        """
        
        return result, description
    
    def closing(self, image, kernel_size=5, kernel_shape='rect'):
        """Apply closing morphological operation (dilation followed by erosion).
        
        Args:
            image: Input image
            kernel_size: Size of structuring element
            kernel_shape: Shape of kernel ('rect', 'ellipse', 'cross')
        """
        # Get appropriate kernel
        kernel = self.__get_kernel(kernel_shape, kernel_size)
        
        # Apply closing (dilation followed by erosion)
        result = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        description = f"""
        <strong>Closing</strong><br>
        Kernel shape: {kernel_shape}<br>
        Kernel size: {kernel_size}x{kernel_size}<br><br>
        
        Closing is a morphological operation that consists of a dilation followed by an erosion.
        It's named "closing" because it closes or fills small holes and gaps within objects.
        
        Main effects of closing:
        <ul>
          <li>Fills small holes within objects</li>
          <li>Connects nearby objects</li>
          <li>Smooths object contours</li>
          <li>Fills in small gaps in object boundaries</li>
        </ul>
        
        Closing is particularly useful for:
        <ul>
          <li>Filling small holes in objects</li>
          <li>Closing small gaps in object boundaries</li>
          <li>Connecting objects that are close to each other</li>
        </ul>
        
        Mathematically: Closing(A, B) = Erosion(Dilation(A, B), B), where A is the image and B is the structuring element.
        """
        
        return result, description
    
    def gradient(self, image, kernel_size=5, kernel_shape='rect'):
        """Apply morphological gradient (difference between dilation and erosion).
        
        Args:
            image: Input image
            kernel_size: Size of structuring element
            kernel_shape: Shape of kernel ('rect', 'ellipse', 'cross')
        """
        # Get appropriate kernel
        kernel = self.__get_kernel(kernel_shape, kernel_size)
        
        # Apply morphological gradient
        result = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)
        
        description = f"""
        <strong>Morphological Gradient</strong><br>
        Kernel shape: {kernel_shape}<br>
        Kernel size: {kernel_size}x{kernel_size}<br><br>
        
        The morphological gradient is the difference between the dilation and erosion of an image.
        It highlights boundaries and edges of objects in the image.
        
        Mathematically: Gradient(A, B) = Dilation(A, B) - Erosion(A, B), where A is the image and B is the structuring element.
        
        The result emphasizes regions of high intensity changes (edges) in the image. The morphological gradient
        is particularly useful for:
        <ul>
          <li>Edge detection</li>
          <li>Boundary extraction</li>
          <li>Highlighting transitions between objects and background</li>
        </ul>
        
        Unlike gradient-based edge detectors (like Sobel), the morphological gradient considers spatial relationships
        defined by the structuring element, making it suitable for certain applications where traditional edge 
        detection might fail.
        """
        
        return result, description
    
    def top_hat(self, image, kernel_size=9, kernel_shape='rect'):
        """Apply top hat transform (difference between input and opening).
        
        Args:
            image: Input image
            kernel_size: Size of structuring element
            kernel_shape: Shape of kernel ('rect', 'ellipse', 'cross')
        """
        # Get appropriate kernel
        kernel = self.__get_kernel(kernel_shape, kernel_size)
        
        # Apply top hat transform
        result = cv2.morphologyEx(image, cv2.MORPH_TOPHAT, kernel)
        
        description = f"""
        <strong>Top Hat Transform</strong><br>
        Kernel shape: {kernel_shape}<br>
        Kernel size: {kernel_size}x{kernel_size}<br><br>
        
        The Top Hat transform is the difference between the original image and its opening.
        It extracts small bright details and features from an image.
        
        Mathematically: TopHat(A, B) = A - Opening(A, B), where A is the image and B is the structuring element.
        
        The Top Hat transform is particularly useful for:
        <ul>
          <li>Extracting small bright objects from a variable background</li>
          <li>Enhancing contrast in regions with bright details</li>
          <li>Feature extraction for bright objects smaller than the structuring element</li>
          <li>Correcting uneven illumination in images</li>
        </ul>
        
        The size of the structuring element determines what sizes of features are extracted.
        Larger structuring elements extract larger bright features.
        """
        
        return result, description
    
    def black_hat(self, image, kernel_size=9, kernel_shape='rect'):
        """Apply black hat transform (difference between closing and input).
        
        Args:
            image: Input image
            kernel_size: Size of structuring element
            kernel_shape: Shape of kernel ('rect', 'ellipse', 'cross')
        """
        # Get appropriate kernel
        kernel = self.__get_kernel(kernel_shape, kernel_size)
        
        # Apply black hat transform
        result = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, kernel)
        
        description = f"""
        <strong>Black Hat Transform</strong><br>
        Kernel shape: {kernel_shape}<br>
        Kernel size: {kernel_size}x{kernel_size}<br><br>
        
        The Black Hat transform is the difference between the closing of an image and the original image.
        It extracts small dark details and features from an image.
        
        Mathematically: BlackHat(A, B) = Closing(A, B) - A, where A is the image and B is the structuring element.
        
        The Black Hat transform is particularly useful for:
        <ul>
          <li>Extracting small dark objects from a variable background</li>
          <li>Enhancing contrast in regions with dark details</li>
          <li>Feature extraction for dark objects smaller than the structuring element</li>
          <li>Finding dark spots or text on a light background</li>
        </ul>
        
        The size of the structuring element determines what sizes of features are extracted.
        Larger structuring elements extract larger dark features.
        """
        
        return result, description