import cv2
import numpy as np

class PointOperations:
    def negative_transformation(self, image):
        """
        Apply negative transformation to the image.
        :param image: Input image (grayscale)
        :return: Negative image
        """
        return 255 - image

    def log_transformation(self, image):
        """
        Apply log transformation to the image.
        :param image: Input image (grayscale)
        :return: Log transformed image
        """
        c = 255 / np.log(1 + np.max(image))
        log_image = c * np.log(1 + image.astype(np.float64))
        log_image = np.uint8(np.clip(log_image, 0, 255))
        return log_image

    def threshold_transformation(self, image, threshold=128):
        """
        Apply threshold transformation to the image.
        :param image: Input image (grayscale)
        :param threshold: Threshold value (0-255)
        :return: Thresholded binary image
        """
        _, thresh_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        return thresh_image

def main():
    # Load the image in grayscale
    image = cv2.imread('image.jpg', cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load 'image.jpg'. Please ensure the file exists in the script directory.")
        return

    point_ops = PointOperations()

    # Apply point operations
    negative = point_ops.negative_transformation(image)
    log_transformed = point_ops.log_transformation(image)
    thresholded = point_ops.threshold_transformation(image, threshold=128)

    # Display results
    cv2.imshow('Original', image)
    cv2.imshow('Negative Transformation', negative)
    cv2.imshow('Log Transformation', log_transformed)
    cv2.imshow('Threshold Transformation', thresholded)

    print("Press any key in the image window to exit.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
