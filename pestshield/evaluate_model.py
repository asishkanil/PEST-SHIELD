import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# ✅ Dataset path (same path used in training)
dataset_path = os.path.abspath("C:\\Users\\user\\Downloads\\archive (2)\\pest\\train")
img_size = (256, 256)
batch_size = 32

# ✅ Data generator for validation
datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

validation_generator = datagen.flow_from_directory(
    dataset_path,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

# ✅ Load the saved model
model = tf.keras.models.load_model("pest_classifier_resnet_v2.keras")

# ✅ Evaluate accuracy
loss, accuracy = model.evaluate(validation_generator)
print(f"\n✅ Validation Accuracy: {accuracy * 100:.2f}%")
print(f"✅ Validation Loss: {loss:.4f}")
