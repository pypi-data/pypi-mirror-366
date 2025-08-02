import numpy as np

class TransformerOptimiser:
    def __init__(self, forwardPropagation, backwardPropagation):
        self.firstMoment = {}
        self.secondMoment = {}
        self.t = 0
        self.forwardPropagation = forwardPropagation
        self.backwardPropagation = backwardPropagation

    def _AdamsOptimiserWithBatches(self, inputData, labels, batchSize, alpha, beta1, beta2, epsilon):     
        AllOutputs = []
        for i in range(0, len(inputData), batchSize):
            batchData = inputData[i:i+batchSize]
            batchLabels = labels[i:i+batchSize]
            acculumalatedGradients = {}
            Parameters = None
            for j in range(len(batchData)):
                output = self.forwardPropagation(batchData[j])
                AllOutputs.append(output)
                Parameters, Gradients  = self.backwardPropagation(output, batchLabels[j])
                
                for key in Gradients:
                    if key not in acculumalatedGradients:
                        acculumalatedGradients[key] = Gradients[key]
                    else:
                        acculumalatedGradients[key] += Gradients[key]

            for key in acculumalatedGradients:
                acculumalatedGradients[key] /= batchSize

            Parameters = self._Adams(Parameters, acculumalatedGradients, alpha, beta1, beta2, epsilon)
        return AllOutputs

    def _AdamsOptimiserWithoutBatches(self, inputData, labels, alpha, beta1, beta2, epsilon):   
        AllOutputs = []
        for i in range(len(inputData)):
            output = self.forwardPropagation(inputData[i])
            AllOutputs.append(output)
            Parameters, Gradients  = self.backwardPropagation(output, labels[i])
            Parameters = self._Adams(Parameters, Gradients, alpha, beta1, beta2, epsilon)
        return AllOutputs

    def _Adams(self, Parameters, Gradients, alpha, beta1, beta2, epsilon):
        if not self.firstMoment:
            for key in Gradients:
                self.firstMoment[key] = np.zeros_like(Gradients[key])
                self.secondMoment[key] = np.zeros_like(Gradients[key])

        self.t += 1
        for key in Parameters:
            g = Gradients[key]

            self.firstMoment[key] = beta1 * self.firstMoment[key] + (1 - beta1) * g
            self.secondMoment[key] = beta2 * self.secondMoment[key] + (1 - beta2) * (g ** 2)

            firstMomentWeightHat = self.firstMoment[key] / (1 - beta1 ** self.t)
            secondMomentWeightHat = self.secondMoment[key] / (1 - beta2 ** self.t)

            Parameters[key] -= alpha * firstMomentWeightHat / (np.sqrt(secondMomentWeightHat) + epsilon)
        
        return Parameters
    