import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50V2
from tensorflow.keras.applications.resnet_v2 import preprocess_input
from tensorflow.keras import layers, models, regularizers
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
import numpy as np
import os

#  Dataset Path
dataset_path = os.path.abspath("C:\\Users\\user\\Downloads\\archive (2)\\pest\\train")
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"Dataset path not found: {dataset_path}")

#  Image Size and Batch Size
img_size = (299, 299)
batch_size = 32

#  Data Augmentation
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    zoom_range=0.3,
    shear_range=0.2,
    horizontal_flip=True,
    validation_split=0.1
)

#  Data Generators
train_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

validation_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

#  Class Weights
num_classes = len(train_generator.class_indices)
labels = train_generator.classes
class_weights = compute_class_weight(class_weight='balanced', classes=np.arange(num_classes), y=labels)
class_weight_dict = {i: class_weights[i] for i in range(num_classes)}

#  Build Model
base_model = ResNet50V2(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
base_model.trainable = False

inputs = tf.keras.Input(shape=(299, 299, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)
x = layers.Dense(512, activation='relu', kernel_regularizer=regularizers.l2(0.001))(x)
x = layers.Dropout(0.4)(x)
x = layers.BatchNormalization()(x)
x = layers.Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.001))(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(num_classes, activation='softmax')(x)

model = models.Model(inputs, outputs)

#  Compile (initial training)
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),  # label smoothing added
    metrics=['accuracy']
)

#  Callbacks
callbacks = [
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, verbose=1, min_lr=1e-6),
    EarlyStopping(monitor='val_accuracy', patience=6, restore_best_weights=True, verbose=1)
]

#  Initial Training
model.fit(
    train_generator,
    epochs=25,
    validation_data=validation_generator,
    class_weight=class_weight_dict,
    callbacks=callbacks
)

# ✅
# Fine-tuning: Unfreeze last 120 layers
base_model.trainable = True
for layer in base_model.layers[:-120]:
    layer.trainable = False

#  Compile (fine-tuning)
model.compile(
    optimizer=tf.keras.optimizers.SGD(learning_rate=1e-5, momentum=0.9),
    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
    metrics=['accuracy']
)

#  Fine-tuning Training
model.fit(
    train_generator,
    epochs=30,
    validation_data=validation_generator,
    class_weight=class_weight_dict,
    callbacks=callbacks
)

# ✅ Save the Model
model.save("pest_classifier_resnet_v2_final.keras")

# ✅ Final Evaluation
loss, accuracy = model.evaluate(validation_generator)
print(f"\n Final Validation Accuracy: {accuracy * 100:.2f}%")
print(f" Final Validation Loss: {loss:.4f}")

# Predict on the validation set
y_true = validation_generator.classes
y_pred_prob = model.predict(validation_generator, verbose=1)
y_pred = np.argmax(y_pred_prob, axis=1)

# Precision, Recall, F1-Score for each class
precision = precision_score(y_true, y_pred, average=None)
recall = recall_score(y_true, y_pred, average=None)
f1 = f1_score(y_true, y_pred, average=None)

# Print the metrics for each class
print("\nPrecision for each class:")
for i, p in enumerate(precision):
    print(f"Class {train_generator.class_indices[i]}: {p:.4f}")

print("\nRecall for each class:")
for i, r in enumerate(recall):
    print(f"Class {train_generator.class_indices[i]}: {r:.4f}")

print("\nF1 Score for each class:")
for i, f in enumerate(f1):
    print(f"Class {train_generator.class_indices[i]}: {f:.4f}")

