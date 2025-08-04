import cv2
import numpy as np

class ImageFilters:
    def mean_filter(self, image, ksize=3):
        """
        Apply mean filter (average blur) to the image.
        :param image: Input image
        :param ksize: Kernel size (must be odd)
        :return: Filtered image
        """
        return cv2.blur(image, (ksize, ksize))

    def gaussian_filter(self, image, ksize=3, sigma=0):
        """
        Apply Gaussian filter to the image.
        :param image: Input image
        :param ksize: Kernel size (must be odd)
        :param sigma: Gaussian kernel standard deviation. 0 means calculated from ksize.
        :return: Filtered image
        """
        return cv2.GaussianBlur(image, (ksize, ksize), sigma)

    def median_filter(self, image, ksize=3):
        """
        Apply median filter to the image.
        :param image: Input image
        :param ksize: Kernel size (must be odd)
        :return: Filtered image
        """
        return cv2.medianBlur(image, ksize)

    def sobel_filter(self, image, dx=1, dy=0, ksize=3):
        """
        Apply Sobel filter to the image.
        :param image: Input image (grayscale)
        :param dx: Order of derivative x
        :param dy: Order of derivative y
        :param ksize: Kernel size (must be 1, 3, 5, or 7)
        :return: Filtered image (Sobel edges)
        """
        return cv2.Sobel(image, cv2.CV_64F, dx, dy, ksize=ksize)

    def gradient_magnitude_filter(self, image, ksize=3):
        """
        Calculate gradient magnitude from Sobel x and y.
        :param image: Input image (grayscale)
        :param ksize: Kernel size for Sobel
        :return: Gradient magnitude image
        """
        sobelx = self.sobel_filter(image, dx=1, dy=0, ksize=ksize)
        sobely = self.sobel_filter(image, dx=0, dy=1, ksize=ksize)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        magnitude = np.uint8(np.clip(magnitude, 0, 255))
        return magnitude

    def gradient_direction_filter(self, image, ksize=3):
        """
        Calculate gradient direction from Sobel x and y.
        :param image: Input image (grayscale)
        :param ksize: Kernel size for Sobel
        :return: Gradient direction image in degrees (0-360)
        """
        sobelx = self.sobel_filter(image, dx=1, dy=0, ksize=ksize)
        sobely = self.sobel_filter(image, dx=0, dy=1, ksize=ksize)
        direction = np.arctan2(sobely, sobelx)  # radians
        direction = np.degrees(direction)  # convert to degrees
        direction = (direction + 360) % 360  # normalize to 0-360
        direction = np.uint8(direction / 360 * 255)  # scale to 0-255 for display
        return direction

    def laplace_filter(self, image, ksize=3):
        """
        Apply Laplace filter to the image.
        :param image: Input image (grayscale)
        :param ksize: Kernel size (1, 3, 5, or 7)
        :return: Filtered image
        """
        laplacian = cv2.Laplacian(image, cv2.CV_64F, ksize=ksize)
        laplacian = np.uint8(np.clip(np.absolute(laplacian), 0, 255))
        return laplacian

def main():
    # Load the AOT Fury Titan image in grayscale
    image = cv2.imread('aot-fury-titan-desktop-wallpaper-preview.jpg', cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load 'aot-fury-titan-desktop-wallpaper-preview.jpg'. Please ensure the file exists in the script directory.")
        return

    filters = ImageFilters()

    # Apply filters
    mean = filters.mean_filter(image)
    gaussian = filters.gaussian_filter(image)
    median = filters.median_filter(image)
    sobel_x = filters.sobel_filter(image, dx=1, dy=0)
    sobel_y = filters.sobel_filter(image, dx=0, dy=1)
    grad_magnitude = filters.gradient_magnitude_filter(image) 
    grad_direction = filters.gradient_direction_filter(image)
    laplace = filters.laplace_filter(image)

    # Display results
    cv2.imshow('Original', image)
    cv2.imshow('Mean Filter', mean)
    cv2.imshow('Gaussian Filter', gaussian)
    cv2.imshow('Median Filter', median)
    cv2.imshow('Sobel Filter X', cv2.convertScaleAbs(sobel_x))
    cv2.imshow('Sobel Filter Y', cv2.convertScaleAbs(sobel_y))
    cv2.imshow('Gradient Magnitude', grad_magnitude)
    cv2.imshow('Gradient Direction', grad_direction)
    cv2.imshow('Laplace Filter', laplace)

    print("Press any key in the image window to exit.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
