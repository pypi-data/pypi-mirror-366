import numpy as np

class RNNBackProp:
    def _Singular_BPTT(self, inputs, AllHiddenStates, hiddenPreActivationValues, outputPreActivation, targets, outputs):
        self._checkParams(inputs, AllHiddenStates, hiddenPreActivationValues, outputPreActivation, targets, outputs)
        inputWeightGradients = np.zeros_like(self.inputWeight)
        hiddenStateWeightGradients = np.zeros_like(self.hiddenWeight)
        biasGradients = np.zeros_like(self.bias)
        outputWeightGradients = np.zeros((self.outputSize, self.hiddenSize))
        outputbiasGradients = np.zeros(self.outputSize)

        delta = np.zeros_like(AllHiddenStates[0])

        outputLoss = self.lossDerivative(outputs, targets, outputs.shape[0])
        outputActivationDeriv = self.activationDerivative(outputPreActivation)
        outputLoss = outputLoss * outputActivationDeriv

        outputWeightGradients += np.dot(outputLoss, AllHiddenStates[len(AllHiddenStates) - 1].T)
        outputbiasGradients += outputLoss.flatten()

        for i in reversed(range(len(AllHiddenStates))):
            error = (self.outputWeight.T @ outputLoss + delta) * self.activationDerivative(np.array(hiddenPreActivationValues[i][0]))
            
            inputWeightGradients += np.outer(error, inputs[i].flatten())
            biasGradients += error
            
            if(i > 0):
                hiddenStateWeightGradients += np.outer(error, AllHiddenStates[i - 1].flatten())
            
            delta = self.hiddenWeight.T @ error

            outputLoss = np.zeros_like(outputLoss)

        return inputWeightGradients, hiddenStateWeightGradients, biasGradients, outputWeightGradients, outputbiasGradients

    def _checkParams(self, inputs, AllHiddenStates, preActivationValues, outputPreActivation, targets, outputs):
        Size = len(inputs)
        assert Size == len(AllHiddenStates), f"Inputs length {Size} must match hidden states length {len(AllHiddenStates)}"
        assert Size == len(preActivationValues), f"Inputs length {Size} must match pre-activation values length {len(preActivationValues)}"
    
        for i in range(Size):
            assert inputs[i].shape == (self.inputSize, 1), f"Input at time {i} has shape {inputs[i].shape} but expected ({self.inputSize}, 1)"
            assert AllHiddenStates[i].shape == (self.hiddenSize, 1), f"Hidden state at time {i} has shape {AllHiddenStates[i].shape} but expected {(self.hiddenSize, 1)}"
            assert preActivationValues[i].shape == (self.hiddenSize, 1), f"Pre-activation at time {i} has shape {preActivationValues[i].shape} but expected {(self.hiddenSize, 1)}"
            
        assert outputPreActivation.shape == (self.outputSize, 1), f"Output pre-activation shape {outputPreActivation.shape} expected {(self.outputSize, 1)}"
        assert targets.shape == (self.outputSize, 1), f"Targets shape {targets.shape} does not match output size {(self.outputSize,)}"
        assert outputs.shape == (self.outputSize, 1), f"Output has shape {outputs.shape} but expected ({self.outputSize}, 1)"

        assert self.inputWeight.shape == (self.hiddenSize, self.inputSize), f"Input weights shape {self.inputWeight.shape} expected {(self.hiddenSize, self.inputSize)}"
        assert self.hiddenWeight.shape == (self.hiddenSize, self.hiddenSize), f"Hidden weights shape {self.hiddenWeights.shape} expected {(self.hiddenSize, self.hiddenSize)}"
        assert self.outputWeight.shape == (self.outputSize, self.hiddenSize), f"Output weights shape {self.outputWeight.shape} expected {(self.outputSize, self.hiddenSize)}"
        assert self.bias.shape == (self.hiddenSize, 1), f"Bias shape {self.bias.shape} expected {(self.hiddenSize, 1)}"
        