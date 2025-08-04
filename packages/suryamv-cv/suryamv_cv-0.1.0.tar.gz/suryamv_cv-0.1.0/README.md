# Suryacv

Suryacv is a Python package for computer vision that provides various image filtering and processing modules. It includes classes for image filters, point operations, histogram equalization, and low/high pass filtering using OpenCV and NumPy.

## Installation

You can install the package via pip once it is published:

```
pip install suryacv
```

## Usage

```python
from suryacv import ImageFilters, PointOperations, HistogramEqualization, LowPassHighPass

filters = ImageFilters()
point_ops = PointOperations()
hist_eq = HistogramEqualization()
lp_hp = LowPassHighPass()

# Example usage
# result = filters.gaussian_filter(image)
```

## License

This project is licensed under the MIT License.
