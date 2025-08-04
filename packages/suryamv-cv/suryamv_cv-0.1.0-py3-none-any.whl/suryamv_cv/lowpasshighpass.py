import cv2
import numpy as np

class LowPassHighPass:
    def low_pass_filter(self, image, ksize=3, sigma=0):
        """
        Apply a low pass filter using Gaussian blur.
        :param image: Input image
        :param ksize: Kernel size (must be odd)
        :param sigma: Gaussian kernel standard deviation. 0 means calculated from ksize.
        :return: Low pass filtered image
        """
        return cv2.GaussianBlur(image, (ksize, ksize), sigma)

    def high_pass_filter(self, image, ksize=3, sigma=0):
        """
        Apply a high pass filter by subtracting the low pass filtered image from the original.
        :param image: Input image
        :param ksize: Kernel size for low pass filter (must be odd)
        :param sigma: Gaussian kernel standard deviation for low pass filter
        :return: High pass filtered image
        """
        low_pass = self.low_pass_filter(image, ksize, sigma)
        high_pass = cv2.subtract(image, low_pass)
        return high_pass

def main():
    # Load the example image in grayscale
    image = cv2.imread('image.jpg', cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load 'image.jpg'. Please ensure the file exists in the script directory.")
        return

    filters = LowPassHighPass()

    # Apply low pass filter
    low_passed = filters.low_pass_filter(image, ksize=7, sigma=1)

    # Apply high pass filter
    high_passed = filters.high_pass_filter(image, ksize=7, sigma=1)

    # Display results
    cv2.imshow('Original Image', image)
    cv2.imshow('Low Pass Filtered Image', low_passed)
    cv2.imshow('High Pass Filtered Image', high_passed)

    print("Press any key in the image window to exit.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
