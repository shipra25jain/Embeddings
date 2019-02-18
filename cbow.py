# -*- coding: utf-8 -*-
"""CBOW.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yb4I57iKwAFmC8IczaJ7N5qn2_vGZ0n3
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
torch.manual_seed(111)

USE_CUDA = torch.cuda.is_available()
device = torch.device("cuda" if USE_CUDA else "cpu")

from google.colab import drive
drive.mount('/content/gdrive')

# context_size = 2 means 2 words in left and 2 words in left of target word are known
context_size = 2
embedding_dim = 10

import os
corpus_name = "text8"
corpus = os.path.join("/content/gdrive/My Drive/Colab Notebooks/embeddings/data", corpus_name)


with open(corpus) as f:
    dataLines = f.read()

import re
from collections import Counter
def preprocess(text):
    text = text.lower()
    # Replace punctuation with tokens so we can use them in our model
    text = text.replace('.', ' <PERIOD> ')
    text = text.replace(',', ' <COMMA> ')
    text = text.replace('"', ' <QUOTATION_MARK> ')
    text = text.replace(';', ' <SEMICOLON> ')
    text = text.replace('!', ' <EXCLAMATION_MARK> ')
    text = text.replace('?', ' <QUESTION_MARK> ')
    text = text.replace('(', ' <LEFT_PAREN> ')
    text = text.replace(')', ' <RIGHT_PAREN> ')
    text = text.replace('--', ' <HYPHENS> ')
    text = text.replace('?', ' <QUESTION_MARK> ')
    # text = text.replace('\n', ' <NEW_LINE> ')
    text = text.replace(':', ' <COLON> ')
    words = text.split()
    # Remove all words with  5 or fewer occurences
    word_counts = Counter(words)
    trimmed_words = [word for word in words if word_counts[word] > 5]

    return trimmed_words

train_corpus = preprocess(dataLines)
# extracting pair of three consecutive words i.e. trigrams
contextWindow = [([train_corpus1[i],train_corpus1[i+1],train_corpus1[i+2],train_corpus1[i+3],train_corpus1[i+4]]) for i in range(len(train_corpus1)-4)]
# vocab is set of unique words
vocab = set(train_corpus)
# dictionary to map index to corresponding word and vice-versa
word2index = {word:i for i,word in enumerate(vocab)}
index2word = {i:word for i,word in enumerate(vocab)}

# embeddings trained by continuous bag-of-words approach
class cbowEmbeddings(nn.Module):
  
  def __init__(self,vocabSize, embDim, hiddenSize):
    super(cbowEmbeddings,self).__init__()
    self.embeddings = nn.Embedding(vocabSize, embDim)
    self.linear1 = nn.Linear(embDim, hiddenSize)
    self.linear2 = nn.Linear(hiddenSize, hiddenSize)
    self.linear3 = nn.Linear(hiddenSize, vocabSize)
    
  def forward(self,inputs):
    embeds = sum(self.embeddings(inputs)).view((1,-1))
    hid1 = F.relu(self.linear1(embeds))
    hid2 = F.relu(self.linear2(hid1))
    logProb = F.log_softmax(self.linear3(hid2),dim=1)
    return logProb

# can predict the middle target word given 4 surrounding words
def predict(contextWords,word2index,index2word):
  cntIndex = torch.tensor([word2index[w] for w in contextWords], dtype=torch.long)
  logProb = model(cntIndex).data.numpy()
  outputWord = index2word[logProb[0].index(max(logProb[0]))]
  return outputWord

losses = []
lossFn = nn.NLLLoss()
model = cbowEmbeddings(len(vocab),embedding_dim,128)
optimizer = optim.SGD(model.parameters(),lr=0.001)

#training
for epoch in range(10):
  totalLoss = 0
  for ctx1,ctx2,target,ctx3,ctx4 in contextWindow:
    ctx = [ctx1,ctx2,ctx3,ctx4]
    ctxIndex = torch.tensor([word2index[w] for w in ctx], dtype=torch.long)
    model.zero_grad()
    logProb = model(ctxIndex)
    loss = lossFn(logProb, torch.tensor([word2index[target]], dtype = torch.long))
    loss.backward()
    optimizer.step()
    totalLoss += loss.item()
  print(totalLoss)
#   losses.append(totalLoss)
# print(losses)

