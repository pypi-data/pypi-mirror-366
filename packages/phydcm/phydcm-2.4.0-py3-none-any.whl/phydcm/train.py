import os
import argparse
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, CSVLogger, ReduceLROnPlateau
from phydcm.medvit_model import build_medvit_model
from phydcm.create_datasets import get_datasets
from phydcm.config import Config


def train_model(modality):
    print(f"\n🚀 START TRAINING OF MedViT MODELS ON DATA OF {modality.upper()}...\n")

    # ✅ تحميل الداتا
    train_dir = os.path.join(Config.DATA_DIR, modality, 'train')
    val_dir = os.path.join(Config.DATA_DIR, modality, 'val')

    # الحصول على عدد الأصناف المناسب للموداليتي
    num_classes = Config.get_num_classes(modality)

    train_ds, val_ds = get_datasets(
        train_dir=train_dir,
        val_dir=val_dir,
        image_size=Config.IMAGE_SIZE,
        batch_size=Config.BATCH_SIZE,
        class_mode='categorical'
    )

    # ✅ إنشاء النموذج
    model = build_medvit_model(
        input_shape=Config.IMAGE_SIZE + (3,),
        num_classes=num_classes,
        dropout_rate=Config.DROPOUT_RATE if hasattr(Config, 'DROPOUT_RATE') else 0.3
    )

    # ✅ Compile
    model.compile(
        optimizer=Adam(Config.LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )

    # ✅ Callbacks
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    checkpoint_path = os.path.join(Config.OUTPUT_DIR, f"{modality}_best_model.keras")

    callbacks = [
        ModelCheckpoint(checkpoint_path, monitor='val_accuracy', save_best_only=True, verbose=1),
        EarlyStopping(patience=10, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1),
        CSVLogger(os.path.join(Config.LOG_DIR, f"{modality}_training.log"))
    ]

    # ✅ تدريب
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=Config.EPOCHS,
        callbacks=callbacks,
        verbose=1
    )

    # ✅ حفظ النموذج النهائي
    final_model_path = os.path.join(Config.OUTPUT_DIR, f"{modality}_final_model.keras")
    model.save(final_model_path)
    print(f"\n✅ the final forms has been saved!: {final_model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--modality", type=str, required=True, help="DATA TYPES: mri , ct , pet")
    args = parser.parse_args()

    if args.modality not in ['mri', 'ct', 'pet']:
        raise ValueError("❌ The model should be either 'mri' or 'ct' or 'pet' only.")

    train_model(args.modality)
