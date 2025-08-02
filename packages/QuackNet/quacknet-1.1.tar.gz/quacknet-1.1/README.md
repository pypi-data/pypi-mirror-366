# QuackNet
<!-- Hook -->
A pure Python deep learning library built entirely from scratch, designed for educational insight and hands-on experimentation with neural networks and CNNs without using TensorFlow or PyTorch.

**QuackNet** is a Python-based library for building and training neural networks and convolutional networks entirely from scratch. It offers foundational implementations of key components such as forward propagation, backpropagation and optimisation algorithms, without relying on machine learning frameworks like TensorFlow or PyTorch.

<!-- Badges -->
Latest release: [![PyPI version](https://img.shields.io/pypi/v/QuackNet)](https://pypi.org/project/QuackNet/) 
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://sirquackpng.github.io/QuackNet/quacknet.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Table of Contents

-   [Installation](#installation)
-   [Quick Start](#quick-start)
-   [Benchmark](#benchmark)
-   [Why This Library](#why-this-library)
-   [Key Features](#key-features)
-   [Highlights](#highlights)
-   [Advanced Usage](#advanced-usage)
-   [Examples](#examples)
-   [Roadmap](#roadmap)
-   [Unit Tests](#unit-tests)
-   [Related Projects](#related-projects)
-   [Project Architecture](#project-architecture)
-   [License](#license)

## Installation

QuackNet is simple to install via PyPI.

**Install via PyPI**
```
pip install QuackNet
```

## Quick Start

```python

from quacknet.main import Network

n = Network(lossFunc="Cross Entropy", learningRate=0.01, optimisationFunc="SGD")
n.addLayer(5, "ReLU")
n.addLayer(3, "SoftMax")
n.createWeightsAndBiases()

inputData = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
labels = [[1], [0]]

accuracy, averageLoss = n.train(inputData, labels, epochs=5)
```

For more detailed examples, see [Advanced Usage](#advanced-usage) or [Examples](#examples)

## Benchmark

### Performance Comparison: QuackNet vs PyTorch & TensorFlow

The library was benchmarked on the MNIST dataset against PyTorch and TensorFlow using identical architectures and hyperparameters to ensure fair comparison.

-   **Neural Network Model Architecture:** 784 (input) → 128 → 64 → 10 (output)
-   **Activation Function:** Leaky ReLU for input and hidden layers, and SoftMax for output layer
-   **Optimiser:** Gradient Descent with Batches
-   **Batch Size:** 64
-   **Learning rate:** 0.01
-   **Epochs** 10

Below is the graph showing the training accuracy and loss over 10 epochs, for the three ML frameworks.

![Training Accuracy & Loss for the 3 frameworks](benchmarkFolder/MNISTBenchmark/AllThreeFrameworkMNISTBenchmark.png)

| Framework   | Accuracy | Loss  |
|-------------|----------|-------|
| QuackNet    | 96.26%   | 0.127 |     
| PyTorch     | 93.58%   | 0.223 |
| TensorFlow  | 94.88%   | 0.175 |

**Note:** Due to differences in weight initialisation, dataset shuffling, and internal batch handling, QuackNet occasionally performs slightly better in this specific benchmark. Results may vary across runs.

**code:**

-   The code for the QuackNet benchmark can be found [here](benchmarkFolder/MNISTBenchmark/mnistExample.py)
-   The code for the PyTorch benchmark can be found [here](benchmarkFolder/MNISTBenchmark/pytorchBenchmark.py)
-   The code for the TensorFlow benchmark can be found [here](benchmarkFolder/MNISTBenchmark/tensorflowBenchmark.py)

### QuackNet benchmark on MNIST

The code for this benchmark can be found is the same as the one used to benchmark against PyTorch and TensorFlow.

Below is the graph showing the training accuracy and loss over 10 epochs, across 5 runs:

![QuackNet Training Accuracy & Loss over 10 Epochs for 5 runs](benchmarkFolder/MNISTBenchmark/QuackNetBenchmarkWith5RunsOver10Epochs.png)

## Why this Library?

QuackNet was created to deepen my understanding of how neural networks work internally. Unlike high-level frameworks, it shows the mechanisms of forward and backward propagation, gradient computation, and weight gradients. Offering a highly educational and customisable platform for learning and experimentation.

## Learning Outcomes

Building QuackNet from scratch enabled mastery of:

**Core Concepts:**
- **Backpropagation**
    -   Derived and implemented gradient calculations for dense and convolutional layers
- **Optimiser Internals**
    -   Coded Stochastic Gradient Descent and Adam
- **CNN Operations**
    -   Implemented kernels, padding, strides, and pooling
- **Data Handling**
    -   Used vectorisation (NumPy) to make code more performant
    -   Designed preprocessing (normalisation -> augmentation -> batching)

**CS Skills:**
- **Testing Rigor**
    -   Unit test coverage >80%
    -   Unit test are used to ensure reliability of components
- **API Design**
    -   Created easy interface (e.g., ```Network.addLayer()```) for educational use
- **Documentation**
    -   Used pdoc to create automated documentation
    -   Private functions are marked with a '_' at the start
    -   All functions have docstrings showing their args/params

## Key Features

**1. Custom Implementation:**
-   Implemented from scratch layers, activation functions and loss functions.
-   No reliance on external libraries for machine learning (except for numpy)

**2. Core Functionality:**
-   Support for common activation functions (e.g. Leaky ReLU, Sigmoid, SoftMax)
-   Multiple loss functions with derivatives (e.g. MSE, MAE, Cross Entropy)
-   Optimisers: Gradient Descent, Stochastic Gradient Descent (SGD), and Adam.
-   Supports batching for efficient training.   

**3. Layer Support:**
-   Fully Connected Layer (Dense)
-   Convolutional
-   Pooling (Max and Average)
-   Global Average Pooling
-   Activation Layers

**4. Additional Features:**
-   Save and load model weights and biases.
-   Evaluation metrics such as accuracy and loss.
-   Visualisation tools for training progress.
-   Demo projects like MNIST and HAM10000 classification.

## Highlights

-   **Custom Architectures:** Define and train neural networks with fully customisable architectures
-   **Optimisation Algorithms:** Includes Gradient Descent, Stochastic Gradient Descent and Adam optimiser for efficient training
-   **Loss and Activation Functions:** Prebuilt support for common loss and activation functions with the option to make your own
-   **Layer Support:**
    -   Fully Connected (Dense)
    -   Convolutional
    -   Pooling (Max and Average)
    -   Global Average Pooling
    -   Activation layer
-   **Evaluation Tools:** Includes metrics for model evaluation such as accuracy and loss
-   **Save and Load:** Save weights and biases for reuse for further training
-   **Demo Projects:** Includes example implementations such as MNIST digit classification

## Advanced Usage
Here is an example of how to create and train a simple neural network using the library:
```python
from quacknet.main import Network

# Define a neural network architecture
n = Network(
    lossFunc = "Cross Entropy",
    learningRate = 0.01,
    optimisationFunc = "SGD", # Stochastic Gradient Descent
)
n.addLayer(3) # Input layer
n.addLayer(2, "ReLU") # Hidden layer
n.addLayer(1, "SoftMax") # Output layer
n.createWeightsAndBiases()

# Train the network
accuracy, averageLoss = n.train(mnist_images, mnist_labels, epochs = 10)

# Evaluate
print(f"Accuracy: {accuracy}%")
print(f"Average loss: {averageLoss}")
```

**Note:** This example assumes input and labels are preprocessed as NumPy arrays. You can use [this script](ExampleCode\MNISTExample\saveMNISTimages.py) to download and save MNIST images using `torchvision`.

## Examples

-   [Simple Neural Network Example](/ExampleCode/NNExample.py): A basic neural network implementation demonstrating forward and backpropagation
-   [Convolutional Neural Network Example](/ExampleCode/CNNExample.py): Shows how to use the convolutional layers in the library
-   [MNIST Neural Network Example](/ExampleCode/MNISTExample/mnistExample.py): Trains a neural network on the MNIST dataset using QuackNet

## Roadmap

- [X] **Forward propagation**
    Implemented the feed forward pass for neural network layers
- [X] **Activation functions**
    Added support for Leaky ReLU, Sigmoid, SoftMax, and others
- [X] **Loss functions**
    Implemented MSE, MAE, and Cross Entropy loss with their derivatives
- [X] **Backpropagation**
    Completed backpropagation for gradient calculation and parameter updates
- [X] **Optimisers**
    Added support for batching, stochastic gradient descent and gradient descent
- [X] **Convolutional Neural Network**
    Implemented kernels, pooling and dense layers for Convolutional Neural Network
- [X] **Visualisation tools**  
    Added support for visualising training, such as loss and accuracy graphs
- [X] **Benchmark against PyTorch/TensorFlow**
    Benchmark against popular machine learning frameworks on MNIST dataset
- [X] **Add Adam optimiser**  
    Implement the Adam optimiser to improve training performance and convergence
- [X] **Data augmentation**
    Add data augmentation such as flipping, rotation and cropping
- [X] **Input Data augmentation:**
    Add pixel normalisation of pixels and one-hot encoded label
- [X] **Skin Lesion detector**    
    Use the neural network library to create a model for detecting skin lesions using HAM10000 for skin lesion images
- [ ] **Recurrent Neural Network and Transformers**
    Implement BPTT, multi head attention, residual connection 
- [ ] **Additional activation functions**  
    Implement advanced activation functions (eg. GELU and Swish)

## Unit Tests

QuackNet includes unit tests that ensures the reliability of QuackNet's neural and convolutional components. They help to confirm that all layers and training processes behave as expected after every major update to ensure structural stability of all components. The tests are organised into two directories:
-   [Unit Tests for NN](/unitTests/NN/) - for standard neural network tests 
-   [Unit Tests for CNN](/unitTests/CNN/) - for convolutional network specific tests 

These tests cover:

-   Forward and backward propagation for both neural networks and convolutional neural networks.
-   CNN specific layers: Dense, Convolutional, Pooling
-   Activation functions and loss functions, including their derivatives
-   Optimisation algorithms: SGD, GD, Adam

To run the tests:

```bash
pytest
```

To check test coverage:

```bash
coverage run -m pytest
coverage report -m
```

## Related Projects

### Skin Lesion Detector

A convolutional neural network (CNN) skin lesion classification model built with QuackNet, trained using the HAM10000 dataset. This model achieved 60.2% accuracy on a balanced validation set of skin lesion images.

You can explore the full project here:
[Skin Lesion Detector Repository](https://github.com/SirQuackPng/skinLesionDetector)

This project demonstrates how QuackNet can be applied to real-world image classification tasks.

## Project Architecture

### Neural Network Class
-   **Purpose** Handles fully connected layers for standard neural network
-   **Key Components:**
    -   Layers: Dense Layer
    -   Functions: Forward propagation, backpropagation
    -   Optimisers: SGD, GD, GD using batching

### Convolutional Neural Network Class
-   **Purpose** Specialised for image data processing using convolutional layers
-   **Key Components:**
    -   Layers: Convolutional, pooling, dense and activation layers
    -   Functions: Forward propagation, backpropagation, flattening, global average pooling
    -   Optimisers: Adam optimiser, SGD, GD, GD using batching

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
