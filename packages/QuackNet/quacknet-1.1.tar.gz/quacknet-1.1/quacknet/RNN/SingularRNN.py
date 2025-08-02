from quacknet.core.activationFunctions import relu, sigmoid, linear, tanH, softMax
from quacknet.RNN.SingularBackPropRNN import RNNBackProp
from quacknet.RNN.SingularOptimiserRNN import RNNOptimiser
from quacknet.core.lossFunctions import MAELossFunction, MSELossFunction, CrossEntropyLossFunction
from quacknet.core.lossDerivativeFunctions import MAEDerivative, MSEDerivative, CrossEntropyLossDerivative
from quacknet.core.activationDerivativeFunctions import ReLUDerivative, SigmoidDerivative, LinearDerivative, TanHDerivative, SoftMaxDerivative
import numpy as np
import math

"""
Singular RNN only has 1 hidden state

InputData --> Hidden State --> Dense Layer (output layer)
"""

class SingularRNN(RNNBackProp, RNNOptimiser): 
    def __init__(self, hiddenStateActivationFunction, outputLayerActivationFunction, lossFunction, useBatches = False, batchSize = 64):
        self.inputWeight = None
        self.hiddenWeight = None
        self.bias = None
        self.outputWeight = None
        self.outputBias = None
        self.hiddenState = None
        
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

    def forwardSequence(self, inputData): # goes through the whole sequence / time steps
        preActivations = []
        allHiddenStates = []
        for i in range(len(inputData)):
            preAct, outputPreAct, output = self._oneStep(inputData[i])
            preActivations.append(preAct)
            allHiddenStates.append(self.hiddenState.copy())
        return preActivations, allHiddenStates, output, outputPreAct

    def _oneStep(self, inputData): # forward prop on 1 time step
        preActivation, self.hiddenState = self._calculateHiddenLayer(inputData, self.hiddenState, self.inputWeight, self.hiddenWeight, self.bias, self.hiddenStateActivationFunction)
        preAct, output = self._calculateOutputLayer(self.hiddenState, self.outputWeight, self.outputBias, self.outputLayerActivationFunction)
        return preActivation, preAct, output.reshape(-1, 1)

    def _calculateHiddenLayer(self, inputData, lastHiddenState, inputWeight, hiddenWeight, bias, activationFunction): # a( w_x * x + w_h * h + b )
        preActivation = np.dot(inputWeight, inputData) + np.dot(hiddenWeight, lastHiddenState) + bias
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
    
    def initialiseWeights(self, inputSize, hiddenSize, outputSize):
        self.inputWeight = self._initialiseWeights(hiddenSize, inputSize, self.hiddenStateActivationFunction)
        self.hiddenWeight = self._initialiseWeights(hiddenSize, hiddenSize, self.hiddenStateActivationFunction)
        self.outputWeight = self._initialiseWeights(outputSize, hiddenSize, self.outputLayerActivationFunction)
        self.bias = np.zeros((hiddenSize, 1))
        self.outputBias = np.zeros((outputSize, 1))
        self.hiddenState = np.zeros((hiddenSize, 1))
        self.inputSize = inputSize
        self.hiddenSize = hiddenSize
        self.outputSize = outputSize

    def backwardPropagation(self, inputs, AllHiddenStates, preActivationValues, outputPreAct, targets, outputs):
        return self._Singular_BPTT(inputs, AllHiddenStates, preActivationValues, outputPreAct, targets, outputs)

    def optimiser(self, inputData, labels, alpha, beta1, beta2, epsilon):
        if(self.useBatches == True):
            AllOutputs, self.inputWeight, self.hiddenWeight, self.biases, self.outputWeight, self.outputBiases = self._AdamsOptimiserWithBatches(inputData, labels, self.inputWeight, self.hiddenWeight, self.bias, self.outputWeight, self.outputBias, self.batchSize, alpha, beta1, beta2, epsilon)
        else:
            AllOutputs, self.inputWeight, self.hiddenWeight, self.biases, self.outputWeight, self.outputBiases = self._AdamsOptimiserWithoutBatches(inputData, labels, self.inputWeight, self.hiddenWeight, self.bias, self.outputWeight, self.outputBias, alpha, beta1, beta2, epsilon)
        return AllOutputs

    def train(self, inputData, labels, alpha = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8):
        AllOutputs = self.optimiser(inputData, labels, alpha, beta1, beta2, epsilon)
        loss = self.lossFunction(AllOutputs, labels)
        return loss