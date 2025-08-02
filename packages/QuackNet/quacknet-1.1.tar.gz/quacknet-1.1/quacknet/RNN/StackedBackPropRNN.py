import numpy as np

class RNNBackProp:
    def _Stacked_BPTT(self, inputs, AllHiddenStates, hiddenPreActivationValues, outputPreActivation, targets, outputs):
        self._checkParams(inputs, AllHiddenStates, hiddenPreActivationValues, outputPreActivation, targets, outputs)
        
        inputWeightGradients = [np.zeros_like(w) for w in self.inputWeights]
        hiddenStateWeightGradients = np.zeros_like(self.hiddenWeights)
        biasGradients = np.zeros_like(self.biases)

        outputWeightGradients = np.zeros((self.outputSize, self.hiddenSizes[-1]))
        outputbiasGradients = np.zeros(self.outputSize)

        T = len(inputs) # number of time steps
        L = len(self.hiddenSizes) # number of hidden layers

        outputLoss = self.lossDerivative(outputs, targets, outputs.shape[0])
        outputActivationDeriv = self.activationDerivative(outputPreActivation)
        outputLoss = outputLoss * outputActivationDeriv

        outputWeightGradients += np.dot(outputLoss, AllHiddenStates[-1][-1].T)
        outputbiasGradients += outputLoss.flatten()

        delta = []
        for l in range(L):
            delta.append(np.zeros((self.hiddenSizes[l], 1)))

        delta[L - 1] = self.outputWeight.T @ outputLoss

        for t in reversed(range(T)):
            for l in reversed(range(L)):
                preAct = hiddenPreActivationValues[t][l]
                actDeriv = self.activationDerivative(preAct)
                error = delta[l] * actDeriv
                
                inputToLayer = inputs[t]
                if(l != 0):
                    inputToLayer = AllHiddenStates[t][l - 1]

                inputWeightGradients[l] += np.dot(error, inputToLayer.T)
                biasGradients[l] += error
                
                if(t > 0):
                    delta[l] += self.hiddenWeights[l].T @ error
                else:
                    delta[l] = np.zeros_like(delta[l])
                
                if(l > 0):
                    delta[l -1] += self.hiddenWeights[l].T @ error

                hiddenStateWeightGradients[l] += error @ AllHiddenStates[t - 1][l].T

        return inputWeightGradients, hiddenStateWeightGradients, biasGradients, outputWeightGradients, outputbiasGradients

    def _checkParams(self, inputs, AllHiddenStates, preActivationValues, outputPreActivation, targets, outputs):
        T = len(inputs)
        L = len(self.hiddenSizes)

        assert T == len(AllHiddenStates), f"Inputs length {T} must match hidden states length {len(AllHiddenStates)}"
        assert T == len(preActivationValues), f"Inputs length {T} must match pre-activation values length {len(preActivationValues)}"
    
        for t in range(T):
            assert inputs[t].shape == (self.inputSize, 1), f"Input at time {t} has shape {inputs[t].shape} but expected ({self.inputSize}, 1)"

            assert len(AllHiddenStates[t]) == L, f"Expected {L} hidden layers at time {t}, got {len(AllHiddenStates[t])}"
            assert len(preActivationValues[t]) == L, f"Expected {L} pre-activations at time {t}, got {len(preActivationValues[t])}"
            
            for l in range(L):
                expectedShape = (self.hiddenSizes[l], 1)
                assert AllHiddenStates[t][l].shape == expectedShape, f"Hidden state at time {t}, layer {l} has shape {AllHiddenStates[t][l].shape}, expected {expectedShape}"
                assert preActivationValues[t][l].shape == expectedShape, f"Pre-activation at time {t}, layer {l} has shape {preActivationValues[t][l].shape}, expected {expectedShape}"

        assert outputPreActivation.shape == (self.outputSize, 1), f"Output pre-activation shape {outputPreActivation.shape} expected {(self.outputSize, 1)}"
        assert targets.shape == (self.outputSize, 1), f"Targets shape {targets.shape} does not match output size {(self.outputSize,)}"
        assert outputs.shape == (self.outputSize, 1), f"Output has shape {outputs.shape} but expected ({self.outputSize}, 1)"

        for l in range(L):
            inputShape = (self.hiddenSizes[l], self.inputSize if l == 0 else self.hiddenSizes[l - 1])
            hiddenShape = (self.hiddenSizes[l], self.hiddenSizes[l])
            biasShape = (self.hiddenSizes[l], 1)

            assert self.inputWeights[l].shape == inputShape, f"Input weight at layer {l} has shape {self.inputWeights[l].shape}, expected {inputShape}"
            assert self.hiddenWeights[l].shape == hiddenShape, f"Hidden weight at layer {l} has shape {self.hiddenWeights[l].shape}, expected {hiddenShape}"
            assert self.biases[l].shape == biasShape, f"Bias at layer {l} has shape {self.biases[l].shape}, expected {biasShape}"

        assert self.outputWeight.shape == (self.outputSize, self.hiddenSizes[-1]), f"Output weight shape {self.outputWeight.shape}, expected ({self.outputSize}, {self.hiddenSizes[-1]})"
        assert self.outputBias.shape == (self.outputSize, 1), f"Output bias shape {self.outputBias.shape}, expected ({self.outputSize}, 1)"
