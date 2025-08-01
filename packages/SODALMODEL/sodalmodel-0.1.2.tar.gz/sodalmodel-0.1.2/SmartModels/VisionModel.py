import tensorflow as tf
import tensorflow_hub as hub
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


class SVOL:
    """
    Smart Vision Object Locator (SVOL) for easy object detection using a pre-trained
    EfficientDet model from TensorFlow Hub.

    This class simplifies the process of loading images, performing predictions,
    and visualizing results for object detection tasks. It also includes
    functionality for real-time webcam detection and training a custom model.

    Attributes:
        model: The loaded TensorFlow Hub model for object detection.
        class_names (list): A list of COCO dataset class names.
        custom_model (tf.keras.Model): A custom-trained model.
    """

    def __init__(self, model_url: str = "https://tfhub.dev/tensorflow/efficientdet/d0/1"):
        """
        Initializes the SVOL class by loading the pre-trained model and class labels.

        Args:
            model_url (str): The URL of the TensorFlow Hub model to load.
        """
        self.model = hub.load(model_url)
        self.class_names = self._load_coco_labels()
        self.custom_model = None

    def _load_coco_labels(self) -> list:
        """Loads the COCO dataset class names."""
        return [
            "background", "person", "bicycle", "car", "motorcycle", "airplane", "bus",
            "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign",
            "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
            "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag",
            "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
            "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
            "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana",
            "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza",
            "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table",
            "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone",
            "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock",
            "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
        ]

    def preprocess_image(self, image_path: str) -> tuple:
        """
        Loads and preprocesses an image from a file path.

        Args:
            image_path (str): The path to the image file.

        Returns:
            tuple: A tuple containing the image tensor and the original RGB image.
        """
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_tensor = tf.convert_to_tensor(image_rgb, dtype=tf.uint8)
        image_tensor = tf.expand_dims(image_tensor, axis=0)
        return image_tensor, image_rgb

    def predict(self, image_path: str, score_threshold: float = 0.5) -> dict:
        """
        Performs object detection on a single image.

        Args:
            image_path (str): The path to the image file.
            score_threshold (float): The confidence threshold for filtering detections.

        Returns:
            dict: A dictionary containing the detection results and the original image.
        """
        image_tensor, original_image = self.preprocess_image(image_path)
        results = self.model(image_tensor)

        boxes = results['detection_boxes'].numpy()[0]
        scores = results['detection_scores'].numpy()[0]
        classes = results['detection_classes'].numpy()[0].astype(int)

        height, width, _ = original_image.shape
        output_results = []
        for box, score, cls in zip(boxes, scores, classes):
            if score >= score_threshold:
                ymin, xmin, ymax, xmax = box
                left, top = int(xmin * width), int(ymin * height)
                right, bottom = int(xmax * width), int(ymax * height)
                output_results.append({
                    'box': [left, top, right, bottom],
                    'score': float(score),
                    'class': self.class_names[cls] if cls < len(self.class_names) else f'class_{cls}'
                })

        return {'results': output_results, 'image': original_image}

    def draw_bounding_boxes(self, prediction_result: dict):
        """
        Draws bounding boxes on an image based on the prediction results.

        Args:
            prediction_result (dict): The output from the `predict` method.
        """
        image = prediction_result['image']
        boxes_data = prediction_result['results']

        fig, ax = plt.subplots(1)
        ax.imshow(image)

        for item in boxes_data:
            left, top, right, bottom = item['box']
            score = item['score']
            label = item['class']

            rect = patches.Rectangle(
                (left, top), right - left, bottom - top,
                linewidth=2, edgecolor='red', facecolor='none'
            )
            ax.add_patch(rect)
            ax.text(left, top - 10, f"{label}: {score:.2f}", color='white', fontsize=8, backgroundcolor='red')

        plt.axis('off')
        plt.show()

    def predict_from_webcam(self, score_threshold: float = 0.5):
        """
        Performs real-time object detection using a webcam feed.

        Args:
            score_threshold (float): The confidence threshold for filtering detections.
        """
        cap = cv2.VideoCapture(0)
        print("📷 Webcam is active. Press 'q' to quit.")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_tensor = tf.convert_to_tensor(rgb_frame, dtype=tf.uint8)
            image_tensor = tf.expand_dims(image_tensor, axis=0)

            results = self.model(image_tensor)
            boxes = results['detection_boxes'].numpy()[0]
            scores = results['detection_scores'].numpy()[0]
            classes = results['detection_classes'].numpy()[0].astype(int)

            height, width, _ = frame.shape
            for box, score, cls in zip(boxes, scores, classes):
                if score >= score_threshold:
                    ymin, xmin, ymax, xmax = box
                    start_point = (int(xmin * width), int(ymin * height))
                    end_point = (int(xmax * width), int(ymax * height))
                    label = self.class_names[cls] if cls < len(self.class_names) else f'class_{cls}'

                    cv2.rectangle(frame, start_point, end_point, (0, 0, 255), 2)
                    cv2.putText(frame, f"{label}: {score:.2f}", (start_point[0], start_point[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("SmartVision (SVOL)", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def train_custom_model(
        self,
        model_name: str = "trained_model",
        dataset: tuple = None,
        epochs: int = 5,
        batch_size: int = 32,
        loss: str = 'categorical_crossentropy',
        optimizer: str = 'adam',
        custom_layers: list = None
    ):
        """
        Trains a custom object detection model.

        Args:
            model_name (str): Name to save the trained model.
            dataset (tuple): A tuple (train_data, val_data) of tf.data.Dataset.
                             If None, uses CIFAR-10 as a demo.
            epochs (int): Number of training epochs.
            batch_size (int): Batch size for training.
            loss (str): Loss function.
            optimizer (str): Optimizer type.
            custom_layers (list): List of additional Keras layers to add to the model.
        """
        if dataset:
            train_data, val_data = dataset
        else:
            print("🔁 No dataset provided. Using CIFAR-10 as a demo.")
            (x_train, y_train), (x_val, y_val) = tf.keras.datasets.cifar10.load_data()
            x_train, x_val = x_train / 255.0, x_val / 255.0
            y_train = tf.keras.utils.to_categorical(y_train, 10)
            y_val = tf.keras.utils.to_categorical(y_val, 10)
            train_data = tf.data.Dataset.from_tensor_slices((x_train, y_train)).shuffle(10000).batch(batch_size)
            val_data = tf.data.Dataset.from_tensor_slices((x_val, y_val)).batch(batch_size)

        print("🚀 Starting training...")

        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(32, 32, 3)),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu')
        ])

        if custom_layers:
            for layer in custom_layers:
                model.add(layer)

        model.add(tf.keras.layers.Dense(10, activation='softmax'))
        model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

        checkpoint_path = f"{model_name}.keras"
        checkpoint = tf.keras.callbacks.ModelCheckpoint(checkpoint_path, monitor='val_accuracy', save_best_only=True)

        model.fit(train_data, validation_data=val_data, epochs=epochs, callbacks=[checkpoint])

        self.custom_model = model
        print(f"✅ Training complete. Best model saved as: {checkpoint_path}")

    def load_custom_model(self, path: str):
        """
        Loads a custom-trained model from a file.

        Args:
            path (str): The path to the model file.
        """
        try:
            self.custom_model = tf.keras.models.load_model(path)
            print(f"📂 Model loaded from: {path}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")

    def add_layers_to_model(self, base_model: tf.keras.Model, layers: list) -> tf.keras.Model:
        """
        Adds custom layers to an existing model.

        Args:
            base_model (tf.keras.Model): The base model to extend.
            layers (list): A list of Keras layers to add.

        Returns:
            tf.keras.Model: The extended model.
        """
        for layer in layers:
            base_model.add(layer)
        print("✅ Layers added.")
        return base_model
