import numpy as np

class RNNOptimiser():
    def _AdamsOptimiserWithBatches(self, inputData, labels, inputWeights, hiddenWeights, biases, outputWeights, outputBiases, batchSize, alpha, beta1, beta2, epsilon):     
        Output_firstMomentWeight, Output_firstMomentBias, Output_secondMomentWeight, Output_secondMomentBias, Output_weightGradients, Output_biasGradients, Input_firstMomentWeight, Biases_firstMomentBias, Input_secondMomentWeight, Biases_secondMomentBias, Input_weightGradients, Biases_biasGradients, Hidden_firstMomentWeight, Hidden_secondMomentWeight, Hidden_weightGradients = self._InitialiseEverything(inputWeights, hiddenWeights, biases, outputWeights, outputBiases)
        AllOutputs = []
        t = 1
        for i in range(0, len(inputData), batchSize):
            batchData = inputData[i:i+batchSize]
            batchLabels = labels[i:i+batchSize]
            for j in range(len(batchData)):
                preActivations, allHiddenStates, output, outputPreAct = self.forwardSequence(batchData[j])
                AllOutputs.append(output)

                inputWeightGrad, hiddenStateWeightGrad, biasGrad, outputWeightGrad, outputbiasGrad = self.backwardPropagation(batchData[j], allHiddenStates, preActivations, outputPreAct, batchLabels[j], output)
                
                Output_weightGradients = self._addGradients(batchSize, Output_weightGradients, outputWeightGrad)
                Output_biasGradients = self._addGradients(batchSize, Output_biasGradients, outputbiasGrad)
                Input_weightGradients = self._addGradients(batchSize, Input_weightGradients, inputWeightGrad)
                Hidden_weightGradients = self._addGradients(batchSize, Hidden_weightGradients, hiddenStateWeightGrad)
                Biases_biasGradients = self._addGradients(batchSize, Biases_biasGradients, biasGrad)
            
            outputWeights, outputBiases, Output_firstMomentWeight, Output_firstMomentBias, Output_secondMomentWeight, Output_secondMomentBias = self._Adams(Output_weightGradients, Output_biasGradients, outputWeights, outputBiases, t, Output_firstMomentWeight, Output_firstMomentBias, Output_secondMomentWeight, Output_secondMomentBias, alpha, beta1, beta2, epsilon)
            inputWeights, biases, Input_firstMomentWeight, Biases_firstMomentBias, Input_secondMomentWeight, Biases_secondMomentBias = self._Adams(Input_weightGradients, Biases_biasGradients, inputWeights, biases, t, Input_firstMomentWeight, Biases_firstMomentBias, Input_secondMomentWeight, Biases_secondMomentBias, alpha, beta1, beta2, epsilon)
            hiddenWeights, _, Hidden_firstMomentWeight, _, Hidden_secondMomentWeight, _ = self._Adams(Hidden_weightGradients, None, hiddenWeights, None, t, Hidden_firstMomentWeight, None, Hidden_secondMomentWeight, None, alpha, beta1, beta2, epsilon)
            
            t += 1
        return AllOutputs, inputWeights, hiddenWeights, biases, outputWeights, outputBiases

    def _AdamsOptimiserWithoutBatches(self, inputData, labels, inputWeights, hiddenWeights, biases, outputWeights, outputBiases, alpha, beta1, beta2, epsilon):   
        Output_firstMomentWeight, Output_firstMomentBias, Output_secondMomentWeight, Output_secondMomentBias, Output_weightGradients, Output_biasGradients, Input_firstMomentWeight, Biases_firstMomentBias, Input_secondMomentWeight, Biases_secondMomentBias, Input_weightGradients, Biases_biasGradients, Hidden_firstMomentWeight, Hidden_secondMomentWeight, Hidden_weightGradients = self._InitialiseEverything(inputWeights, hiddenWeights, biases, outputWeights, outputBiases)
        AllOutputs = []
        for i in range(len(inputData)):
            preActivations, allHiddenStates, output, outputPreAct = self.forwardSequence(inputData[i])
            AllOutputs.append(output)

            inputWeightGrad, hiddenStateWeightGrad, biasGrad, outputWeightGrad, outputbiasGrad = self.backwardPropagation(inputData[i], allHiddenStates, preActivations, outputPreAct, labels[i], output)
            
            Output_weightGradients = self._addGradients(1, Output_weightGradients, outputWeightGrad)
            Output_biasGradients = self._addGradients(1, Output_biasGradients, outputbiasGrad)
            Input_weightGradients = self._addGradients(1, Input_weightGradients, inputWeightGrad)
            Hidden_weightGradients = self._addGradients(1, Hidden_weightGradients, hiddenStateWeightGrad)
            Biases_biasGradients = self._addGradients(1, Biases_biasGradients, biasGrad)
            
        outputWeights, outputBiases, Output_firstMomentWeight, Output_firstMomentBias, Output_secondMomentWeight, Output_secondMomentBias = self._Adams(Output_weightGradients, Output_biasGradients, outputWeights, outputBiases, i + 1, Output_firstMomentWeight, Output_firstMomentBias, Output_secondMomentWeight, Output_secondMomentBias, alpha, beta1, beta2, epsilon)
        inputWeights, biases, Input_firstMomentWeight, Biases_firstMomentBias, Input_secondMomentWeight, Biases_secondMomentBias = self._Adams(Input_weightGradients, Biases_biasGradients, inputWeights, biases, i + 1, Input_firstMomentWeight, Biases_firstMomentBias, Input_secondMomentWeight, Biases_secondMomentBias, alpha, beta1, beta2, epsilon)
        hiddenWeights, _, Hidden_firstMomentWeight, _, Hidden_secondMomentWeight, _ = self._Adams(Hidden_weightGradients, None, hiddenWeights, None, i + 1, Hidden_firstMomentWeight, None, Hidden_secondMomentWeight, None, alpha, beta1, beta2, epsilon)
        
        return AllOutputs, inputWeights, hiddenWeights, biases, outputWeights, outputBiases

    def _Adams(self, weightGradients, biasGradients, weights, biases, timeStamp, firstMomentWeight, firstMomentBias, secondMomentWeight, secondMomentBias, alpha, beta1, beta2, epsilon):
        for i in range(len(weights)):
            firstMomentWeight[i] = beta1 * np.array(firstMomentWeight[i]) + (1 - beta1) * weightGradients[i]
            secondMomentWeight[i] = beta2 * np.array(secondMomentWeight[i]) + (1 - beta2) * (weightGradients[i] ** 2)

            firstMomentWeightHat = firstMomentWeight[i] / (1 - beta1 ** timeStamp)
            secondMomentWeightHat = secondMomentWeight[i] / (1 - beta2 ** timeStamp)

            weights[i] -= alpha * firstMomentWeightHat / (np.sqrt(secondMomentWeightHat) + epsilon)
        
        if(biases is not None):
            for i in range(len(biases)):
                firstMomentBias[i] = beta1 * np.array(firstMomentBias[i]) + (1 - beta1) * np.array(biasGradients[i])
                secondMomentBias[i] = beta2 * np.array(secondMomentBias[i]) + (1 - beta2) * (np.array(biasGradients[i]) ** 2)

                firstMomentBiasHat = firstMomentBias[i] / (1 - beta1 ** timeStamp)
                secondMomentBiasHat = secondMomentBias[i] / (1 - beta2 ** timeStamp)

                biases[i] -= alpha * firstMomentBiasHat / (np.sqrt(secondMomentBiasHat) + epsilon)
        return weights, biases, firstMomentWeight, firstMomentBias, secondMomentWeight, secondMomentBias

    def _initialiseGradients(self, weights, biases):
        weightGradients, biasGradients = [], []
        for i in weights:
            w = []
            for j in i:
                w.append(np.zeros_like(j, dtype=np.float64))
            weightGradients.append(w)
        for i in biases:
            biasGradients.append(np.zeros_like(i, dtype=np.float64))
        return weightGradients, biasGradients

    def _addGradients(self, batchSize, gradients, w):
        for i in range(len(gradients)):
            gradients[i] += np.array(w[i]) / batchSize

        return gradients

    def _initialiseMoment(self, weights, biases):
        momentWeight = []
        momentBias = []
        for i in weights:
            w = []
            for j in i:
                w.append(np.zeros_like(j))
            momentWeight.append(w)
        for i in biases:
            momentBias.append(np.zeros_like(i))
        return momentWeight, momentBias

    def _InitialiseEverything(self, inputWeights, hiddenWeights, biases, outputWeights, outputBiases):
        Output_firstMomentWeight, Output_firstMomentBias = self._initialiseMoment(outputWeights, outputBiases)
        Output_secondMomentWeight, Output_secondMomentBias = self._initialiseMoment(outputWeights, outputBiases)
        Output_weightGradients, Output_biasGradients = self._initialiseGradients(outputWeights, outputBiases)

        Input_firstMomentWeight, Biases_firstMomentBias = self._initialiseMoment(inputWeights, biases)
        Input_secondMomentWeight, Biases_secondMomentBias = self._initialiseMoment(inputWeights, biases)
        Input_weightGradients, Biases_biasGradients = self._initialiseGradients(inputWeights, biases)

        Hidden_firstMomentWeight, _ = self._initialiseMoment(hiddenWeights, outputBiases)
        Hidden_secondMomentWeight, _ = self._initialiseMoment(hiddenWeights, outputBiases)
        Hidden_weightGradients, _ = self._initialiseGradients(hiddenWeights, outputBiases)
        return Output_firstMomentWeight, Output_firstMomentBias, Output_secondMomentWeight, Output_secondMomentBias, Output_weightGradients, Output_biasGradients, Input_firstMomentWeight, Biases_firstMomentBias, Input_secondMomentWeight, Biases_secondMomentBias, Input_weightGradients, Biases_biasGradients, Hidden_firstMomentWeight, Hidden_secondMomentWeight, Hidden_weightGradients
    
