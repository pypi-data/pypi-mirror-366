import cv2
import numpy as np

class HistogramEqualization:
    def global_histogram_equalization(self, image):
        """
        Perform global histogram equalization on a grayscale image.
        :param image: Input grayscale image
        :return: Histogram equalized image
        """
        return cv2.equalizeHist(image)

    def adaptive_histogram_equalization(self, image, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Perform adaptive histogram equalization (AHE) on a grayscale image.
        :param image: Input grayscale image
        :param clip_limit: Threshold for contrast limiting
        :param tile_grid_size: Size of grid for histogram equalization
        :return: AHE processed image
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)

    def clahe(self, image, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Perform Contrast Limited Adaptive Histogram Equalization (CLAHE).
        This is similar to adaptive_histogram_equalization but named explicitly.
        :param image: Input grayscale image
        :param clip_limit: Threshold for contrast limiting
        :param tile_grid_size: Size of grid for histogram equalization
        :return: CLAHE processed image
        """
        return self.adaptive_histogram_equalization(image, clip_limit, tile_grid_size)

    def bi_histogram_equalization(self, image):
        """
        Perform bi-histogram equalization by splitting the image histogram at the mean intensity.
        :param image: Input grayscale image
        :return: Bi-histogram equalized image
        """
        mean_intensity = np.mean(image)
        lower_mask = image <= mean_intensity
        upper_mask = image > mean_intensity

        lower_part = image.copy()
        upper_part = image.copy()

        lower_part[upper_mask] = 0
        upper_part[lower_mask] = 0

        lower_eq = cv2.equalizeHist(lower_part)
        upper_eq = cv2.equalizeHist(upper_part)

        result = np.where(lower_mask, lower_eq, upper_eq)
        return result.astype(np.uint8)

    def brightness_preserving_bi_histogram_equalization(self, image):
        """
        Perform brightness preserving bi-histogram equalization.
        This method preserves the mean brightness of the image.
        :param image: Input grayscale image
        :return: Brightness preserving bi-histogram equalized image
        """
        mean_intensity = np.mean(image)
        lower_mask = image <= mean_intensity
        upper_mask = image > mean_intensity

        lower_part = image.copy()
        upper_part = image.copy()

        lower_part[upper_mask] = 0
        upper_part[lower_mask] = 0

        lower_eq = cv2.equalizeHist(lower_part)
        upper_eq = cv2.equalizeHist(upper_part)

        # Calculate mean brightness before and after equalization
        mean_before = np.mean(image)
        mean_after = np.mean(np.where(lower_mask, lower_eq, upper_eq))

        # Adjust brightness preserving factor
        brightness_factor = mean_before / (mean_after + 1e-8)
        result = np.where(lower_mask, lower_eq * brightness_factor, upper_eq * brightness_factor)
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)

    def dynamic_histogram_equalization(self, image, alpha=0.5):
        """
        Perform dynamic histogram equalization.
        :param image: Input grayscale image
        :param alpha: Weighting factor between original and equalized histogram (0 to 1)
        :return: Dynamically equalized image
        """
        hist, bins = np.histogram(image.flatten(), 256, [0,256])
        cdf = hist.cumsum()
        cdf_normalized = cdf * hist.max() / cdf.max()

        cdf_m = np.ma.masked_equal(cdf,0)
        cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
        cdf = np.ma.filled(cdf_m,0).astype('uint8')

        equalized = cdf[image]

        result = cv2.addWeighted(image, 1-alpha, equalized, alpha, 0)
        return result

    def multi_p_histogram_equalization(self, image, p=3):
        """
        Perform multi-p histogram equalization by dividing histogram into p parts.
        :param image: Input grayscale image
        :param p: Number of partitions
        :return: Multi-p histogram equalized image
        """
        hist, bins = np.histogram(image.flatten(), 256, [0,256])
        cdf = hist.cumsum()
        total_pixels = image.size

        # Find thresholds to split histogram into p parts with approximately equal pixels
        thresholds = []
        pixels_per_part = total_pixels / p
        cumulative = 0
        for i in range(256):
            cumulative += hist[i]
            if cumulative >= pixels_per_part:
                thresholds.append(i)
                cumulative = 0
        if thresholds[-1] != 255:
            thresholds[-1] = 255

        result = np.zeros_like(image, dtype=np.uint8)
        prev_thresh = 0
        for thresh in thresholds:
            mask = (image >= prev_thresh) & (image <= thresh)
            part = image[mask]
            if part.size > 0:
                part_eq = cv2.equalizeHist(part)
                # Assign equalized pixels back to result using flat indexing
                result_flat = result.flatten()
                mask_flat = mask.flatten()
                part_eq_flat = part_eq.flatten()
                result_flat[mask_flat] = part_eq_flat
                result = result_flat.reshape(image.shape)
            prev_thresh = thresh + 1

        return result

def main():
    # Load image in grayscale
    image = cv2.imread('image.jpg', cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load 'image.jpg'. Please ensure the file exists in the script directory.")
        return

    hist_eq = HistogramEqualization()

    # Apply histogram equalization methods
    global_eq = hist_eq.global_histogram_equalization(image)
    adaptive_eq = hist_eq.adaptive_histogram_equalization(image)
    clahe_eq = hist_eq.clahe(image)
    bi_eq = hist_eq.bi_histogram_equalization(image)
    brightness_preserving_eq = hist_eq.brightness_preserving_bi_histogram_equalization(image)
    dynamic_eq = hist_eq.dynamic_histogram_equalization(image)
    multi_p_eq = hist_eq.multi_p_histogram_equalization(image)

    # Display results
    cv2.imshow('Original', image)
    cv2.imshow('Global Histogram Equalization', global_eq)
    cv2.imshow('Adaptive Histogram Equalization', adaptive_eq)
    cv2.imshow('CLAHE', clahe_eq)
    cv2.imshow('Bi-Histogram Equalization', bi_eq)
    cv2.imshow('Brightness Preserving Bi-Histogram Equalization', brightness_preserving_eq)
    cv2.imshow('Dynamic Histogram Equalization', dynamic_eq)
    cv2.imshow('Multi-P Histogram Equalization', multi_p_eq)

    print("Press any key in the image window to exit.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
