from quacknet.Transformer.ResidualConnection import ResidualConnection
from quacknet.Transformer.FeedForwardNetwork import FeedForwardNetwork
from quacknet.Transformer.MultiHeadAttention import MultiAttentionHeadLayer
from quacknet.Transformer.NormLayer import NormLayer
from quacknet.Transformer.PositionalEncoding import PositionalEncoding
from quacknet.Transformer.OptimiserTransformer import TransformerOptimiser
from quacknet.Transformer.EmbeddingLayer import EmbeddingLayer
from quacknet.core.lossDerivativeFunctions import MSEDerivative
from quacknet.core.lossFunctions import MSELossFunction
import numpy as np

"""
Good website that explains transformers: https://poloclub.github.io/transformer-explainer/

Transformer layers (to add):
-   Embedding
-   Multi head attention
-   Positional encoding 
-   Feedforward Network
-   Norm layers
-   Residual connection

Maybe will add in future:
-   Decoder
-   tokenisation (e.g., turn words into vectors)

The library will have a default transformer architecture (the one from "Attention is All You Need" paper) 
and allow the user to add any layer in any order

Default transformer architecture [called transformer block] (only the encoder section):
-   Embedding
-   Positional Encoding
-   Multi Head Attention
-   Residual Connection
-   Layer Normalisation
-   Feed forward Network
-   Residual Connection
-   Layer Normalisation
"""

class Transformer:
    def __init__(self):
        pass

    def addLayers(self, layer): # gets a class and adds it to the layers list
        self.layers.append(layer)

    def forwardPropagation(self, inputData): # just place holder as of now
        input = inputData
        output = 0
        for layer in self.layers:
            if(layer == ResidualConnection):
                ResidualConnection.forwardPropagation(None, input, output)
                continue
            output = layer.forwardPropagation(input)

class TransformerBlock:
    def __init__(self, batchSize, sequenceLength, vocabSize, embedDimension, positionalEmbddingDimension, numberHeads, hiddenDimensionFFN, useResidual = True, useNorm = True):
        self.batchSize = batchSize
        self.sequenceLength = sequenceLength
        self.vocabSize = vocabSize
        self.embedDimension = embedDimension
        self.numberHeads = numberHeads
        self.hiddenDimensionFFN = hiddenDimensionFFN
        self.useResidual = useResidual
        self.useNorm = useNorm
        self.positionalEmbddingDimension = positionalEmbddingDimension

        self.embedding = EmbeddingLayer(
            vocabSize=vocabSize,
            embedDimension=embedDimension,
        )

        self.positionalEncoding = PositionalEncoding(
            maxDimension=positionalEmbddingDimension,
            embeddingSize=embedDimension
        )

        self.attention = MultiAttentionHeadLayer(
            batchSize=batchSize,
            sequenceLength=sequenceLength,
            embedDimension=embedDimension,
            numberOfHeads=numberHeads,
            QueryWeights=None,
            KeyWeights=None, 
            ValueWeights=None,
            outputWeight=None,
            outputBias=None,
        )

        self.FFN = FeedForwardNetwork(
            inputDimension=embedDimension,
            hiddenDimension=hiddenDimensionFFN,
            W1=None,
            b1=None,
            W2=None,
            b2=None,
        )

        if(useNorm == True):
            self.norm1 = NormLayer(embedDimension)
            self.norm2 = NormLayer(embedDimension)

        self.optimiserClass = TransformerOptimiser(self.forwardPropagation, self.backwardPropagation)

    def forwardPropagation(self, input):
        input = self.embedding.forwardPropagation(input)

        input = self.positionalEncoding.forwardPropagation(input)

        attentionOutput = self.attention.forwardPropagation(input)

        if(self.useResidual == True):
            attentionOutput = ResidualConnection.forwardPropagation(None, input, attentionOutput)
        if(self.useNorm == True):
            attentionOutput = self.norm1.forwardPropagation(attentionOutput)

        FNNOutput = self.FFN.forwardPropagation(attentionOutput)

        if(self.useResidual == True):
            FNNOutput = ResidualConnection.forwardPropagation(None, FNNOutput, attentionOutput)
        if(self.useNorm == True):
            FNNOutput = self.norm2.forwardPropagation(FNNOutput)

        return FNNOutput
    
    def backwardPropagation(self, output, labels):
        assert output.shape == (self.batchSize, self.sequenceLength, self.embedDimension), f"MSE Derivative expected derviative {(self.batchSize, self.sequenceLength, self.embedDimension)}, got {output.shape}"

        InputDerivative = MSEDerivative(output, labels, output.shape[-1])
        assert InputDerivative.shape == (self.batchSize, self.sequenceLength, self.embedDimension), f"MSE Derivative expected derviative {(self.batchSize, self.sequenceLength, self.embedDimension)}, got {InputDerivative.shape}"

        if(self.useNorm == True):
            InputDerivative, norm2GammaDerivative, norm2BetaDerivative = self.norm2.backwardPropagation(InputDerivative)
            assert InputDerivative.shape == (self.batchSize, self.sequenceLength, self.embedDimension), f"Norm2 expected derviative {(self.batchSize, self.sequenceLength, self.embedDimension)}, got {InputDerivative.shape}"

        if(self.useResidual == True):
            residual2 = InputDerivative
        
        InputDerivative, FFNWeightGradient1, FFNBiasGradient1, FFNWeightGradient2, FFNBiasGradient2 = self.FFN.backwardPropagation(InputDerivative)
        assert InputDerivative.shape == (self.batchSize, self.sequenceLength, self.embedDimension), f"FFN expected derviative {(self.batchSize, self.sequenceLength, self.embedDimension)}, got {InputDerivative.shape}"

        if(self.useResidual == True):
            InputDerivative += residual2
            assert InputDerivative.shape == (self.batchSize, self.sequenceLength, self.embedDimension), f"Residual1 expected derviative {(self.batchSize, self.sequenceLength, self.embedDimension)}, got {InputDerivative.shape}"

        if(self.useNorm == True):
            InputDerivative, norm1GammaDerivative, norm1BetaDerivative = self.norm1.backwardPropagation(InputDerivative)
            assert InputDerivative.shape == (self.batchSize, self.sequenceLength, self.embedDimension), f"Norm1 expected derviative {(self.batchSize, self.sequenceLength, self.embedDimension)}, got {InputDerivative.shape}"

        if(self.useResidual == True):
            residual1 = InputDerivative
            
        AttentionOutputWeightGradient, AttentionOutputBiasGradient, InputDerivative, AttentionQueryWeightDerivative, AttentionKeyWeightDerivative, AttentionValueWeightDerivative = self.attention.backwardPropagation(InputDerivative)
        assert InputDerivative.shape == (self.batchSize, self.sequenceLength, self.embedDimension), f"Attention expected derviative {(self.batchSize, self.sequenceLength, self.embedDimension)}, got {InputDerivative.shape}"

        if(self.useResidual == True):
            InputDerivative += residual1
            assert InputDerivative.shape == (self.batchSize, self.sequenceLength, self.embedDimension), f"Resiudal1 Derivative expected derviative {(self.batchSize, self.sequenceLength, self.embedDimension)}, got {InputDerivative.shape}"

        embeddingGradient = self.embedding.backwardPropagation(InputDerivative)

        Parameters =  {
            "Norm1_gamma": self.norm1.gamma, 
            "Norm1_beta": self.norm1.beta, 
            "Norm2_gamma": self.norm2.gamma, 
            "Norm2_beta": self.norm2.beta, 
            "FFN_W1": self.FFN.W1, 
            "FFN_b1": self.FFN.b1, 
            "FFN_W2": self.FFN.W2, 
            "FFN_b2": self.FFN.b2, 
            "ATT_WO": self.attention.outputWeight, 
            "ATT_BO": self.attention.outputBias, 
            "ATT_WQ": self.attention.QueryWeights, 
            "ATT_WK": self.attention.KeyWeights, 
            "ATT_WV": self.attention.ValueWeights,
            "Embed_W": self.embedding.weights,
        }
  
        Gradients =  {
            "Norm1_gamma": norm1GammaDerivative, 
            "Norm1_beta": norm1BetaDerivative, 
            "Norm2_gamma": norm2GammaDerivative, 
            "Norm2_beta": norm2BetaDerivative, 
            "FFN_W1": FFNWeightGradient1, 
            "FFN_b1": FFNBiasGradient1, 
            "FFN_W2": FFNWeightGradient2, 
            "FFN_b2": FFNBiasGradient2, 
            "ATT_WO": AttentionOutputWeightGradient, 
            "ATT_BO": AttentionOutputBiasGradient, 
            "ATT_WQ": AttentionQueryWeightDerivative, 
            "ATT_WK": AttentionKeyWeightDerivative, 
            "ATT_WV": AttentionValueWeightDerivative,
            "Embed_W": embeddingGradient,
        }

        for key in Gradients:    # without batches some parameters are (1, x, y) which becomes (x, y) so this turns them back into (x, y)
            if(Gradients[key].ndim == Parameters[key].ndim + 1 and Gradients[key].shape[0] == 1):
                Gradients[key] = np.squeeze(Gradients[key], axis=0)

        return Parameters, Gradients 
    
    def optimiser(self, inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon):
        if(useBatches == True):
            AllOutputs = self.optimiserClass._AdamsOptimiserWithBatches(inputData, labels, batchSize, alpha, beta1, beta2, epsilon)
        else:
            AllOutputs = self.optimiserClass._AdamsOptimiserWithoutBatches(inputData, labels, alpha, beta1, beta2, epsilon)
        return AllOutputs

    def train(self, inputData, labels, useBatches = False, batchSize = 16, alpha = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8):
        AllOutputs = self.optimiser(inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon)
        loss = MSELossFunction(AllOutputs, labels)
        return loss
