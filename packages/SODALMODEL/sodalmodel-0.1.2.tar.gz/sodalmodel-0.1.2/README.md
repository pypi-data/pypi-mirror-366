# 🧠 SODALMODEL

> A unified deep learning library for image **classification**, **object detection**, and **automatic dataset labeling** — powered by TensorFlow, OpenCV, ultralytics and NumPy — but easy to use with **just one line of code**!

[![PyPI version](https://img.shields.io/pypi/v/SODALMODEL)](https://pypi.org/project/SODALMODEL/)
[![Python](https://img.shields.io/pypi/pyversions/SODALMODEL)](https://pypi.org/project/SODALMODEL/)
[![License](https://img.shields.io/github/license/YKandoloJean/SMARTVISIONCNN)](https://github.com/YOTCHEB/SODALMODEL.git)

---

## 🔥 Features

### 🎯 Object Detection — `SVOL` (Smart Vision Object Locator)
- 🚀 Pre-trained EfficientDet D0 model from TensorFlow Hub
- 🖼️ Automatic image preprocessing, bounding box detection, and drawing
- 📹 Real-time detection from webcam feed
- 🎯 High accuracy object localization on COCO dataset classes

### 🧠 Image Classification — `SmartVisionCNN`
- 🧱 Customizable convolutional neural network architecture
- 🧪 Supports training, evaluation, and accuracy/loss visualization
- 💾 Save and load trained models seamlessly
- 🔄 Easily add custom layers like Dropout for regularization

### 📝 Automatic Dataset Labeling — `AutoLabeler`
- 🤖 Automatically generate bounding box annotations for unlabeled image datasets
- 📁 Supports saving annotations in YOLO `.txt` and Pascal VOC `.xml` formats
- 🔍 Uses SVOL detection results for labeling with configurable confidence threshold
- 🎯 Requires user to provide class labels for accurate annotation generation

### 🔒 Model Protection — `ModelProtector`
- 🔐 Password-protect your trained models to restrict unauthorized access
- 🔓 Unlock models via password prompt to enable predictions and saving
- 🔒 Simple and secure file-based locking mechanism
- 🛡️ Prevents accidental or malicious model usage without permission

---

## 🚀 Getting Started

Here's a quick example of how to use `SmartVisionCNN` to train a model on the MNIST dataset:

```python

```

## 📚 Documentation

The official documentation is available at [link-to-your-docs.com](https://github.com/YOTCHEB/SODALMODEL). It includes detailed information on each module, class, and function.

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a pull request.

Please make sure to update tests as appropriate.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

*   [TensorFlow](https://www.tensorflow.org/)
*   [OpenCV](https://opencv.org/)
*   [Ultralytics](https://ultralytics.com/)
*   [NumPy](https://numpy.org/)

---

## 📦 Installation

Install the latest release from PyPI:

```bash
pip install SODALMODEL
