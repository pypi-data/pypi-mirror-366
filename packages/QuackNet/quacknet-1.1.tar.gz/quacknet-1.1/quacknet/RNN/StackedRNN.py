from quacknet.core.activationFunctions import relu, sigmoid, linear, tanH, softMax
from quacknet.core.lossFunctions import MAELossFunction, MSELossFunction, CrossEntropyLossFunction
from quacknet.core.lossDerivativeFunctions import MAEDerivative, MSEDerivative, CrossEntropyLossDerivative
from quacknet.core.activationDerivativeFunctions import ReLUDerivative, SigmoidDerivative, LinearDerivative, TanHDerivative, SoftMaxDerivative
from quacknet.RNN.StackedBackPropRNN import RNNBackProp
from quacknet.RNN.StackedOptimiserRNN import StackedRNNOptimiser
import numpy as np
import math

"""
Stacked RNN only has lots of hidden states
InputData --> [ Hidden State Layer 1 --> Hidden State Layer 2 --> ... --> Hidden State Layer N ] --> Dense Layer (output layer)
"""

class StackedRNN(RNNBackProp, StackedRNNOptimiser): 
    def __init__(self, hiddenStateActivationFunction, outputLayerActivationFunction, lossFunction, numberOfHiddenStates, hiddenSizes, useBatches = False, batchSize = 64):
        self.inputWeights = None
        self.hiddenWeights = None
        self.biases = None
        self.outputWeights = None
        self.outputBias = None
        self.hiddenStates = None
        
        funcs = {
            "relu": relu,
            "sigmoid": sigmoid,
            "linear": linear,
            "tanh": tanH,
            "softmax": softMax,
        }
        if(hiddenStateActivationFunction.lower() not in funcs):
            raise ValueError(f"Activation function not made: {hiddenStateActivationFunction.lower()}")
        if(outputLayerActivationFunction.lower() not in funcs):
            raise ValueError(f"Activation function not made: {outputLayerActivationFunction.lower()}")
        self.hiddenStateActivationFunction = funcs[hiddenStateActivationFunction.lower()]
        self.outputLayerActivationFunction = funcs[outputLayerActivationFunction.lower()]

        derivs = {
            relu: ReLUDerivative,
            sigmoid: SigmoidDerivative,
            linear: LinearDerivative,
            tanH: TanHDerivative,
            softMax: SoftMaxDerivative,
        }
        self.activationDerivative = derivs[self.hiddenStateActivationFunction]
        self.outputLayerDerivative = derivs[self.outputLayerActivationFunction]

        lossFunctionDict = {
            "mse": MSELossFunction,
            "mae": MAELossFunction,
            "cross entropy": CrossEntropyLossFunction,"cross": CrossEntropyLossFunction,
        }
        self.lossFunction = lossFunctionDict[lossFunction.lower()]
        lossDerivs = {
            MSELossFunction: MSEDerivative,
            MAELossFunction: MAEDerivative,
            CrossEntropyLossFunction: CrossEntropyLossDerivative,
        }
        self.lossDerivative = lossDerivs[self.lossFunction]

        self.useBatches = useBatches
        self.batchSize = batchSize

        self.numberOfHiddenStates = numberOfHiddenStates
        self.hiddenSizes = hiddenSizes

        assert type(self.hiddenSizes) == list, f"hiddenSizes has to be a list"
        for num in self.hiddenSizes:
            assert isinstance(num, int), f"hiddenSize has to be a list of integers"

    def forwardSequence(self, inputData): # goes through the whole sequence / time steps
        preActivations = []
        allHiddenStates = []
        for i in range(len(inputData)):
            allPreAct, outputPreAct, output, allHidenStates = self._oneStep(inputData[i])
            preActivations.append(allPreAct)
            allHiddenStates.append(allHidenStates)
        return preActivations, allHiddenStates, output, outputPreAct

    def _oneStep(self, inputData): # forward prop on 1 time step
        allPreActivations = []
        allHidenStates = []

        currentInput = inputData

        for i in range(self.numberOfHiddenStates):
            preActivation, self.hiddenStates[i] = self._calculateHiddenLayer(currentInput, self.hiddenStates[i], self.inputWeights[i], self.hiddenWeights[i], self.biases[i], self.hiddenStateActivationFunction)
            
            allPreActivations.append(preActivation)
            allHidenStates.append(self.hiddenStates[i])
            currentInput = self.hiddenStates[i]

        preAct, output = self._calculateOutputLayer(allHidenStates[-1], self.outputWeight, self.outputBias, self.outputLayerActivationFunction)
        return allPreActivations, preAct, output.reshape(-1, 1), allHidenStates

    def _calculateHiddenLayer(self, inputData, lastHiddenState, inputWeights, hiddenWeights, bias, activationFunction): # a( w_x * x + w_h * h + b )
        preActivation = np.dot(inputWeights, inputData) + np.dot(hiddenWeights, lastHiddenState) + bias
        newHiddenState = activationFunction(preActivation)
        return preActivation, newHiddenState

    def _calculateOutputLayer(self, input, outputWeight, outputBias, activationFunction): # a( w_o * o + b_o)
        preActivation = np.dot(outputWeight, input) + outputBias
        output = activationFunction(preActivation)
        return preActivation, output

    def _initialiseWeights(self, outputSize, inputSize, activationFunction):
        if(activationFunction == relu):
            bounds = math.sqrt(2 / inputSize) # He initialisation
        elif(activationFunction == sigmoid):
            bounds = math.sqrt(6 / (inputSize + outputSize)) # Xavier initialisation
        else:
            bounds = 1 / np.sqrt(inputSize) # default
        w = np.random.normal(0, bounds, size=(outputSize, inputSize))
        return w
    
    def initialiseWeights(self, inputSize, outputSize):
        self.inputWeights = []
        self.hiddenWeights = []
        self.biases = []
        self.hiddenStates = []

        for i, hiddenSize in enumerate(self.hiddenSizes):
            inSize = inputSize 
            if(i != 0):
                inSize = self.hiddenSizes[i - 1]

            inputW = self._initialiseWeights(hiddenSize, inSize, self.hiddenStateActivationFunction)
            hiddenW = self._initialiseWeights(hiddenSize, hiddenSize, self.hiddenStateActivationFunction)
            bias = np.zeros((hiddenSize, 1))
            hiddenState = np.zeros((hiddenSize, 1))
        
            self.inputWeights.append(inputW)
            self.hiddenWeights.append(hiddenW)
            self.biases.append(bias)
            self.hiddenStates.append(hiddenState)

        self.outputWeight = self._initialiseWeights(outputSize, self.hiddenSizes[-1], self.outputLayerActivationFunction)
        self.outputBias = np.zeros((outputSize, 1))
    
    
        self.inputSize = inputSize
        self.outputSize = outputSize

    def backwardPropagation(self, inputs, AllHiddenStates, preActivationValues, outputPreAct, targets, outputs):
        return self._Stacked_BPTT(inputs, AllHiddenStates, preActivationValues, outputPreAct, targets, outputs)

    def optimiser(self, inputData, labels, alpha, beta1, beta2, epsilon):
        if(self.useBatches == True):
            AllOutputs, self.inputWeights, self.hiddenWeights, self.biases, self.outputWeight, self.outputBiases = self._Stacked_AdamsOptimiserWithBatches(inputData, labels, self.inputWeights, self.hiddenWeights, self.biases, self.outputWeight, self.outputBias, self.batchSize, alpha, beta1, beta2, epsilon)
        else:
            AllOutputs, self.inputWeights, self.hiddenWeights, self.biases, self.outputWeight, self.outputBiases = self._Stacked_AdamsOptimiserWithoutBatches(inputData, labels, self.inputWeights, self.hiddenWeights, self.biases, self.outputWeight, self.outputBias, alpha, beta1, beta2, epsilon)
        return AllOutputs

    def train(self, inputData, labels, alpha = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8):
        AllOutputs = self.optimiser(inputData, labels, alpha, beta1, beta2, epsilon)
        loss = self.lossFunction(AllOutputs, labels)
        return loss