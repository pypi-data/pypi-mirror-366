import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from sklearn.model_selection import train_test_split
from PIL import Image



def LoadData(self, image_paths=None, labels=None, test_size=0.2):
        """
        Load and preprocess image data and split into training and test sets.

        Args:
            image_paths (list): List of image file paths.
            labels (list): List of integer labels.
            test_size (float): Fraction of data to use for validation.

        Returns:
            Tuple of (X_train, X_test, y_train, y_test).
        """
        if image_paths is None or labels is None:
            raise ValueError("Image paths and labels must be provided.")

        images = []
        for path in image_paths:
            img = Image.open(path)
            if img.mode not in ["RGB", "L"]:
                img = img.convert("RGB")
            img = img.resize(self.input_shape[:2])
            img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0
            images.append(img_array)

        X = np.array(images)
        y = np.array(labels)
        return train_test_split(X, y, test_size=test_size, random_state=42)

def DatasetToNumpy(self, dataset_dir):
        """
        Convert an entire dataset folder to image arrays and labels.

        Args:
            dataset_dir (str): Path to dataset directory with subfolders as class names.

        Returns:
            Tuple (image_paths, labels, class_names)
        """
        image_paths = []
        labels = []
        class_names = sorted([
            folder for folder in os.listdir(dataset_dir)
            if os.path.isdir(os.path.join(dataset_dir, folder))
        ])

        for idx, class_name in enumerate(class_names):
            class_dir = os.path.join(dataset_dir, class_name)
            for filename in os.listdir(class_dir):
                if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    image_paths.append(os.path.join(class_dir, filename))
                    labels.append(idx)

        self.class_names = class_names
        return image_paths, labels, class_names

def TrainModel(self, X_train, y_train, X_val, y_val, batch_size=32, epochs=10, callbacks=None, model_path='SmartVisionBest.keras'):
        """
        Train the SmartVisionCNN model on the given training and validation data.

        If no custom callbacks are provided, this method uses:
            - EarlyStopping to stop training early when validation loss stops improving.
            - ModelCheckpoint to save the best model based on validation loss.
            - ReduceLROnPlateau to reduce the learning rate if performance plateaus.

        Args:
            X_train (ndarray): Training images.
            y_train (ndarray): Training labels.
            X_val (ndarray): Validation images.
            y_val (ndarray): Validation labels.
            batch_size (int): Batch size for training.
            epochs (int): Number of epochs to train the model.
            callbacks (list): Optional list of Keras callbacks to use during training.
            model_path (str): Path to save the best model.

        Returns:
            keras.callbacks.History: The training history object.
        """
        if callbacks is None:
            callbacks = [
                tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
                tf.keras.callbacks.ModelCheckpoint(model_path, save_best_only=True, monitor='val_loss'),
                tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2)
            ]

        return self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            batch_size=batch_size,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )

def SaveModel(self, save_path):
        """
        Save the trained model to a given file path.

        Args:
            save_path (str): Path to save the model.
        """
        self.model.save(save_path)

def LoadModel(self, load_path):
        """
        Load a previously saved model from disk.

        Args:
            load_path (str): Path of the saved model.
        """
        self.model = tf.keras.models.load_model(load_path)

def PredictImage(self, image):
        """
        Predict the class of a single image. Handles input types:
        - Image path (str)
        - PIL image
        - NumPy array
        - TensorFlow tensor

        Args:
            image: Image input in any supported format.

        Returns:
            int or str: Predicted class index or class name if available.
        """
        if isinstance(image, str) and os.path.exists(image):
            image = Image.open(image).convert("RGB")

        if isinstance(image, Image.Image):
            image = tf.keras.preprocessing.image.img_to_array(image)

        if isinstance(image, np.ndarray):
            image = tf.convert_to_tensor(image)

        if not isinstance(image, tf.Tensor):
            raise TypeError("Unsupported image type. Provide file path, PIL image, array, or tensor.")

        image = tf.image.resize(image, self.input_shape[:2])
        image = tf.expand_dims(image, axis=0) / 255.0
        prediction = self.model.predict(image)
        pred_idx = int(np.argmax(prediction, axis=1)[0])

        if self.class_names and pred_idx < len(self.class_names):
            return self.class_names[pred_idx]

        return pred_idx