import os
import csv
import datetime
import warnings
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import VGG16, ResNet50, DenseNet121, MobileNetV2
from tensorflow.keras.layers import Input, Flatten, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping
from lime import lime_image
from skimage.segmentation import mark_boundaries
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Create a console object to handle printing
console = Console()

# Suppress TensorFlow warnings for cleaner output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore')

# --- Configuration ---
IMG_SIZE = (224, 224)
MODEL_OPTIONS = {
    "1": {"name": "VGG16", "func": VGG16},
    "2": {"name": "ResNet50", "func": ResNet50},
    "3": {"name": "DenseNet121", "func": DenseNet121},
    "4": {"name": "MobileNetV2", "func": MobileNetV2}
}

# --- Helper Functions ---
def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_user_input(prompt, valid_options=None, input_type=str, default=None):
    """
    Generic function to get validated user input with default value support.
    """
    prompt_with_default = f"{prompt} (default: {default})" if default is not None else prompt
    prompt_with_default += ": "
    
    while True:
        try:
            user_input = input(prompt_with_default)
            # If user presses Enter and a default exists, return the default
            if not user_input and default is not None:
                return default
            
            # Original validation logic
            if valid_options and user_input not in valid_options:
                raise ValueError(f"Invalid option. Please choose from {valid_options}.")
            return input_type(user_input)
        except ValueError as e:
            print(f"Error: {e}. Please try again.")

def create_output_directory():
    """Creates a timestamped directory for storing results."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dir_name = f"results/results_{timestamp}"
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

# --- Core Pipeline Functions ---

def display_welcome():
    """Displays the welcome message for the X-DEP pipeline using rich."""
    clear_screen()

    title = Text("Welcome to the X-DEP Pipeline", style="bold magenta", justify="center")
    description = Text(
        "An Integrated Pipeline for Developing and Evaluating\nTrustworthy Computer Vision Models",
        style="cyan", justify="center"
    )

    welcome_panel = Panel(
        Text.assemble(title, "\n\n", description),
        border_style="green",
        title="X-DEP",
        title_align="left"
    )

    console.print(welcome_panel)
    console.print("This script will guide you through training, benchmarking, and diagnosing models using XAI.\n")

    get_user_input("Press Enter to start", default="").strip()

def get_data_directory():
    """Prompts user for the data directory and validates it."""
    while True:
        data_dir = input("Enter the full path to your dataset directory: ")
        if os.path.isdir(data_dir):
            subfolders = [f for f in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, f))]
            if len(subfolders) > 1:
                print(f"\nFound {len(subfolders)} classes (subfolders): {', '.join(subfolders)}")
                return data_dir, subfolders
            else:
                print("Error: The directory must contain at least two subfolders, one for each class.")
        else:
            print("Error: The specified path is not a valid directory.")

def preprocess_data(data_dir, batch_size):
    """Loads and preprocesses the dataset."""
    print("\n--- Step 1: Data Preprocessing ---")
    
    # Load datasets
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.3,
        subset="training",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=batch_size
    )
    val_test_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.3,
        subset="validation",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=batch_size
    )
    
    # Split validation/test set
    val_batches = tf.data.experimental.cardinality(val_test_ds)
    test_ds = val_test_ds.take(val_batches // 2)
    val_ds = val_test_ds.skip(val_batches // 2)

    class_names = train_ds.class_names
    
    # Augmentation and Normalization
    augmentation_layer = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomBrightness(0.2),
    ])
    
    normalization_layer = tf.keras.layers.Rescaling(1./255)

    train_ds = train_ds.map(lambda x, y: (augmentation_layer(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
    train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y), num_parallel_calls=tf.data.AUTOTUNE)
    val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y), num_parallel_calls=tf.data.AUTOTUNE)
    test_ds = test_ds.map(lambda x, y: (normalization_layer(x), y), num_parallel_calls=tf.data.AUTOTUNE)
    
    # Prefetch for performance
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    test_ds = test_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    console.print("✅ Dataset loaded and preprocessed successfully.", style="bold green")
    return train_ds, val_ds, test_ds, class_names


def get_training_configurations():
    """Gets model and hyperparameter choices from the user."""
    print("\n--- Step 2: Model Training & Benchmarking ---")
    
    # Model Selection
    print("Available Models:")
    for key, val in MODEL_OPTIONS.items():
        print(f"  {key}: {val['name']}")
    
    selected_models = []
    while not selected_models:
        choices_str = get_user_input("Select one or more models (e.g., '1' or '1,3')", default="1")
        choices = choices_str.split(',')
        for choice in choices:
            choice = choice.strip()
            if choice in MODEL_OPTIONS:
                selected_models.append(choice)
        if not selected_models:
            print("Invalid selection. Please try again.")

    # Get configurations for each selected model
    configs = []
    for model_key in selected_models:
        model_name = MODEL_OPTIONS[model_key]['name']
        print(f"\n--- Configuring {model_name} ---")
        
        config = {"model_key": model_key}
        config['epochs'] = get_user_input("Enter number of epochs", input_type=int, default=25)
        config['batch_size'] = get_user_input("Enter batch size", input_type=int, default=32)
        
        # Learning Rate
        lr_choice = get_user_input("Use (1) Fixed or (2) Adaptive learning rate?", ["1", "2"], default="1")
        config['lr_type'] = "Fixed" if lr_choice == "1" else "Adaptive"
        if lr_choice == "1":
            config['learning_rate'] = get_user_input("Enter fixed learning rate", input_type=float, default=0.0001)
        
        # Patience
        patience_choice = get_user_input("Use Early Stopping (patience)? (y/n)", ["y", "n"], default="y")
        if patience_choice == 'y':
            config['patience'] = get_user_input("Enter patience level", input_type=int, default=5)
        else:
            config['patience'] = None

        # Visualizations
        print("Select visualizations to generate:")
        vis_choices = []
        if get_user_input("  - Loss/Accuracy Curves? (y/n)", ["y", "n"], default='y') == 'y': vis_choices.append("curves")
        if get_user_input("  - Confusion Matrix? (y/n)", ["y", "n"], default='y') == 'y': vis_choices.append("matrix")
        config['visualizations'] = vis_choices
        
        configs.append(config)
    
    return configs


def build_and_train_model(config, num_classes, train_ds, val_ds, test_ds, output_dir):
    """Builds, trains, and evaluates a single model based on its configuration."""
    model_info = MODEL_OPTIONS[config['model_key']]
    model_name = model_info['name']
    print(f"\n--- Training {model_name} ---")

    # Build Model
    base_model = model_info['func'](input_shape=(*IMG_SIZE, 3), include_top=False, weights='imagenet')
    base_model.trainable = False # Freeze base model
    
    inputs = Input(shape=(*IMG_SIZE, 3))
    x = base_model(inputs, training=False)
    x = Flatten()(x)
    outputs = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs, outputs)

    # Compile Model
    optimizer = tf.keras.optimizers.Adam() if config['lr_type'] == 'Adaptive' else tf.keras.optimizers.Adam(learning_rate=config['learning_rate'])
    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Callbacks
    callbacks = []
    if config['patience']:
        early_stopping = EarlyStopping(monitor='val_loss', patience=config['patience'], restore_best_weights=True)
        callbacks.append(early_stopping)

    # Train Model
    history = model.fit(
        train_ds,
        epochs=config['epochs'],
        validation_data=val_ds,
        callbacks=callbacks
    )

    # Evaluate Model
    loss, accuracy = model.evaluate(test_ds)
    
    # Generate Predictions for detailed report
    y_pred_probs = model.predict(test_ds)
    y_pred = np.argmax(y_pred_probs, axis=1)
    y_true = np.concatenate([y for x, y in test_ds], axis=0)

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    
    results = {
        'model_name': model_name,
        'accuracy': accuracy,
        'precision': report['macro avg']['precision'],
        'recall': report['macro avg']['recall'],
        'f1-score': report['macro avg']['f1-score'],
    }
    
    # Generate Visualizations
    if 'curves' in config['visualizations']:
        generate_curves(history, model_name, output_dir)
    if 'matrix' in config['visualizations']:
        generate_confusion_matrix(y_true, y_pred, list(range(num_classes)), model_name, output_dir)

    return model, results


def generate_curves(history, model_name, output_dir):
    """Saves loss and accuracy curves."""
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title(f'{model_name} Accuracy')
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title(f'{model_name} Loss')
    plt.legend()
    plt.savefig(os.path.join(output_dir, f"{model_name}_curves.png"))
    plt.close()
    print(f"Saved accuracy/loss curves for {model_name}.")


def generate_confusion_matrix(y_true, y_pred, class_names, model_name, output_dir):
    """Saves a confusion matrix plot."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title(f'{model_name} Confusion Matrix')
    plt.savefig(os.path.join(output_dir, f"{model_name}_confusion_matrix.png"))
    plt.close()
    print(f"Saved confusion matrix for {model_name}.")

def run_xai_diagnostics(model, model_name, test_ds, num_samples, class_names, output_dir):
    """Runs LIME and a simple Grad-CAM and saves explanations."""
    print(f"\n--- Step 3: XAI Diagnostics for {model_name} ---")
    
    # Take sample images for explanation
    sample_images, sample_labels = next(iter(test_ds.unbatch().batch(num_samples)))
    
    # --- LIME Explanations ---
    explainer = lime_image.LimeImageExplainer()
    print(f"Generating LIME explanations for {num_samples} images...")
    for i in range(num_samples):
        image = sample_images[i].numpy()
        
        explanation = explainer.explain_instance(
            image,
            model.predict,
            top_labels=1,
            hide_color=0,
            num_samples=1000
        )
        
        temp, mask = explanation.get_image_and_mask(
            explanation.top_labels[0], positive_only=True, num_features=5, hide_rest=True
        )
        
        plt.figure(figsize=(8, 4))
        plt.subplot(1, 2, 1)
        plt.imshow(image)
        plt.title('Original Image')
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        plt.imshow(mark_boundaries(temp, mask))
        plt.title('LIME Explanation')
        plt.axis('off')
        
        lime_path = os.path.join(output_dir, f"{model_name}_lime_example_{i+1}.png")
        plt.savefig(lime_path)
        plt.close()

    print(f"LIME explanations saved to {output_dir}")

    # --- Grad-CAM ---
    # Note: A full Grad-CAM is more complex. This is a simplified concept.
    # For a robust implementation, `tf-keras-vis` is recommended.
    # Here, we'll just note that it would be implemented here.
    print("Grad-CAM module would run here.")
    print("(For a full implementation, consider integrating libraries like tf-keras-vis)")


def save_results_to_csv(all_results, output_dir):
    """Saves all collected results to a single CSV file."""
    if not all_results:
        return
        
    csv_path = os.path.join(output_dir, "final_benchmark_report.csv")
    
    # Make sure all dicts have the same keys for consistent headers
    fieldnames = ['model_name', 'accuracy', 'precision', 'recall', 'f1-score', 'epochs', 'batch_size', 'lr_type', 'learning_rate', 'patience']
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"\n--- Final Report ---")
    print(f"All results have been saved to {csv_path}")

# --- Main Execution ---
def main():
    display_welcome()
    output_dir = create_output_directory()
    data_dir, class_names = get_data_directory()
    
    configs = get_training_configurations()
    
    # Use the batch size from the first config for data loading
    # (assuming user wants same batch size for preprocessing)
    initial_batch_size = configs[0]['batch_size']
    train_ds, val_ds, test_ds, _ = preprocess_data(data_dir, initial_batch_size)

    all_model_results = []
    
    for config in configs:
        model, results = build_and_train_model(config, len(class_names), train_ds, val_ds, test_ds, output_dir)
        
        # Add hyperparams to results dict for final report
        results.update(config)
        all_model_results.append(results)
        
        # XAI Module
        num_xai_samples = get_user_input("\nHow many example images for XAI diagnostics?", input_type=int, default=3)
        if num_xai_samples > 0:
            run_xai_diagnostics(model, MODEL_OPTIONS[config['model_key']]['name'], test_ds, num_xai_samples, class_names, output_dir)

    # --- Step 4: Analyze & Validate ---
    # The CSV file serves as the basis for the user's analysis
    save_results_to_csv(all_model_results, output_dir)
    print("\nPipeline finished. Check the output directory for results.")
    print(f"Directory: {output_dir}")

if __name__ == '__main__':
    main()