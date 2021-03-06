# -*- coding: utf-8 -*-
"""Copy of ML Ass2 Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kHP97Ity-ePuU3fyZE3v93z_ZB4R7RSf

# Decision Tree

## Building the Decision Tree
"""

# Import all libaries that will be used to create the decision tree
import numpy as np
import pandas as pd
import re
from sklearn.model_selection import train_test_split
from pandas.api.types import is_numeric_dtype


def averaged_values(array):
  """
    The function returns an array that averages each adjacent number 
    used to set thresholds
    :param array: all values in the a continuous attribute
  """
  length = len(array) - 1
  mean = lambda x, y: (x + y) / 2
  return [mean(array[i], array[i+1]) for i in range(length)]


def entropy(samples):
  """
  The function calculates the entropy for input examples
  :param samples: target values with different class labels
  """    
  if len(samples) < 2:    # a trivial case
    return 0  
  freq = np.array(samples.value_counts(normalize = True))    
  # freq contains relative frequencies of the unique values
  return -(freq * np.log2(freq + 1e-6)).sum()   # 1e-6 is used to avoid log2(0)


def information_gain(samples, target, attr):
  """
  The function calculates the information gain for input samples
  :param samples: all input examples in the split_table
  :param target: the target variable name
  :param attr: the attribute name in the split_table
  """
  values= samples[attr].value_counts(normalize = True)  
  # value_counts() with the normalize parameter gets the unique values 
  # and their corresponding frequencies
  split_entropy = 0
  for v, freq in values.iteritems(): # iteritems() iterates (index, value) pairs 
    index = samples[attr] == v   
    # gets the index where values in the given 
    # attribute is the same as v
    samples_t = samples[target]
    sub_ent = entropy(samples_t[index])  
    split_entropy += freq * sub_ent
    
  total_entropy = entropy(samples[target])
  return total_entropy - split_entropy


class TreeNode:
  def __init__(self, samples, target, current_depth, max_depth=6):
    self.decision = None    # Undecided
    self.samples = samples    # All training examples   
    self.target = target    # Target name
    self.children = {}    # Sub nodes
    # recursive, those child nodes have the same type (TreeNode)
    self.split_attribute = None    # Splitting feature
    self.current_depth = current_depth    # The current number of splitting times
    self.max_depth = max_depth    # The maximum number of splitting times
    

  def make(self):
    """
      The function builds the tree structure to make decisions or to make 
      children nodes (tree branches) to do further inquiries
    """
    target = self.target
    samples = self.samples
    max_depth = self.max_depth
    current_depth = self.current_depth

    y_uniq = samples[target].unique()     
    if len(samples) == 0:    # If the data is empty when this node is arrived
      self.decision = 0    # Exist and make an arbitrary decision       
      return
    elif len(y_uniq) == 1:   # Only one class label
      self.decision = y_uniq[0]
      return
    elif current_depth >= max_depth:    # Reach the max depth
      self.decision = samples[target].mode()[0]   # Exist and get the most frequent value
      return
    else:
      split_table = pd.DataFrame()
      best_g = -1

      for attr in samples.keys():   # Check each feature to split
        if attr == target:
          continue
        elif is_numeric_dtype(samples[attr]):   # Check whether continuous attribute
          attr_val = samples[attr].sort_values()
          val_uniq = attr_val.unique()
          average_val = averaged_values(val_uniq)
          for val in average_val:
            name = attr + " > " + str(val)  # Feature name > threshold
            split_table[name] = samples[attr] > val
        else:
          split_table[attr] = samples[attr]

      split_table[target] = samples[target]

      for st_attr in split_table.keys():  
        if st_attr == target:
          continue
        info_gain = information_gain(split_table, target, st_attr)
        if info_gain > best_g:
          best_g = info_gain
          self.split_attribute = st_attr
        
      values_unique = split_table[self.split_attribute].unique()
      for value in values_unique:
        ind = split_table[self.split_attribute] == value
        self.children[value] = TreeNode(samples[ind], target, current_depth+1)
        # For the continuous attribute, the value attribute contains True / False
        self.children[value].make()


  def pretty_print(self, prefix=" "):
    """
      The function prints the structure of the decision tree
    """
    if self.split_attribute is not None:
      for k, ch in self.children.items():
        ch.pretty_print(f"{prefix} If {self.split_attribute} is {k}, ")

    else:
      print(f"{prefix} The result is: {self.decision}")


  def predict(self, sample):
    """
      The function predict the class value based on values of data attributes
      in the same example
    """
    if self.decision is not None:
      return self.decision

    else:
      sub_string = " > "    
      if sub_string not in self.split_attribute:    # For categorical attributes 
        attr_val = sample[self.split_attribute]
        c_child = self.children[attr_val]
        return c_child.predict(sample)
      else:    # For continuous attributes
        # Split two parts (feature name & threshold)
        col, val = re.split(" > ", self.split_attribute)  
        val = float(val)    
        # Compare the test value and the threshold
        n_child = self.children[float(sample[col]) > val]
        return n_child.predict(sample)


class Tree: 
  def __init__(self):
    self.root = None
  
  def fit(self, samples, target):
    self.root = TreeNode(samples, target, 0)
    self.root.make()

"""# Model Evaluation

## Libraries Used for Evaluation
"""

from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix

"""## Iris Dataset (Continuous Data)

### Prepare Data
"""

from sklearn.datasets import load_iris
iris = load_iris()  # Load iris dataset
samples_iris = pd.DataFrame(iris["data"], columns = iris["feature_names"])
samples_iris["species"] = iris["target"]
if samples_iris.isnull().values.any():   # Check is there any null value
  # has null values, drop the line consisting of null values
  samples_iris = samples_iris.dropna(axis=0)

"""### Evaluted by Iris Dataset"""

samples_i_train, samples_i_test = train_test_split(samples_iris, train_size=0.8, random_state=42)
t = Tree()
t.fit(samples_i_train, "species")  

print()
print("The structure of the decision tree:")
t.root.pretty_print(" ")

train_part = list()
for ind, data in samples_i_train.iterrows():
  p_train = t.root.predict(data)
  train_part.append(p_train)
type_train = samples_i_train["species"]
actual_train_i = type_train.values.tolist()

pred_i_array = list()
for ind, data in samples_i_test.iterrows():
  pred = t.root.predict(data)
  pred_i_array.append(pred)
type_i = samples_i_test["species"]
actual_iris = type_i.values.tolist()

print()
print("The accuracy for the training set:", accuracy_score(actual_train_i, train_part))
print("The performance of the decision tree for the test data:")
print("Confusion Matrix:")
print(confusion_matrix(actual_iris, pred_i_array))
print("The accuracy for the test set:", accuracy_score(actual_iris, pred_i_array))
print("The macro F1 score for the test set:", f1_score(actual_iris, pred_i_array, average="macro"))

"""### Estimate the Accuracy and the Macro F1 Score over 50 Trainings"""

accuracy_array = []
f1_array = []
for i in range(0, 50):  # i = 0, 1, 2, ... , 49
  samples_i_train, samples_i_test = train_test_split(samples_iris, train_size=0.8, random_state=i)  
  tree = Tree()
  tree.fit(samples_i_train, "species")
  
  pred_i_array = list()
  for ind, data in samples_i_test.iterrows():
    pred = tree.root.predict(data)
    pred_i_array.append(pred)
  type_i = samples_i_test["species"]
  actual_iris = type_i.values.tolist()
  acc = accuracy_score(actual_iris, pred_i_array)
  accuracy_array.append(acc)
  f1_s = f1_score(actual_iris, pred_i_array, average="macro")
  f1_array.append(f1_s)

print("Average accuracy:", np.array(accuracy_array).mean())
print("Average macro f1 score:", np.array(f1_array).mean())

"""## Modified Version of Iris Dataset (Categorical + Continuous Data)

### Prepare Data
"""

samples_iris_c = pd.DataFrame(iris["data"], columns = iris["feature_names"])
samples_iris_c["species"] = iris["target"]
# Split the petal length and petal width into three groups: small, medium and large
samples_iris_c["petal length (cm)"]=pd.qcut(samples_iris_c["petal length (cm)"], 
                                q=3, labels=["small","medium","large"]).astype(str)
samples_iris_c["petal width (cm)"]=pd.qcut(samples_iris_c["petal width (cm)"], 
                                q=3, labels=["small","medium","large"]).astype(str)

"""### Evaluated by New Iris Dataset"""

samples_i_ctrain, samples_i_ctest = train_test_split(samples_iris_c, train_size=0.8, random_state=42)
tc = Tree()
tc.fit(samples_i_ctrain, "species")

print()
print("The structure of the decision tree:")
tc.root.pretty_print(" ")

train_part_c = list()
for cind, cdata in samples_i_ctrain.iterrows():
  p_train_c = tc.root.predict(cdata)
  train_part_c.append(p_train_c)
type_train_c = samples_i_ctrain["species"]
actual_train_i_c = type_train_c.values.tolist()

pred_i_carray = list()
for ind, data in samples_i_ctest.iterrows():
  pred = tc.root.predict(data)
  pred_i_carray.append(pred)
type_ic = samples_i_ctest["species"]
actual_ciris = type_ic.values.tolist()

print()
print("The accuracy for the training set:", accuracy_score(actual_train_i_c, train_part_c))
print("The performance of the decision tree for test data:")
print("Confusion Matrix:")
print(confusion_matrix(actual_ciris, pred_i_carray))
print("The accuracy for the test set:", accuracy_score(actual_ciris, pred_i_carray))
print("The macro f1 score for the test set:", f1_score(actual_ciris, pred_i_carray, average="macro"))

"""### Estimate the Accuracy and the Macro F1 Score over 50 Trainings"""

accuracy_array_c = []
f1_array_c = []
for i in range(0, 50):
  samples_i_train_c, samples_i_test_c = train_test_split(samples_iris_c, train_size=0.8, random_state=i)  
  tree_ = Tree()
  tree_.fit(samples_i_train_c, "species")

  pred_i_array_c = list()
  for ind, data in samples_i_test_c.iterrows():
    pred = tree_.root.predict(data)
    pred_i_array_c.append(pred)
  type_i_c = samples_i_test_c["species"]
  actual_iris_c = type_i_c.values.tolist()
  c_acc = accuracy_score(actual_iris_c, pred_i_array_c)
  accuracy_array_c.append(c_acc)
  f1_s_c = f1_score(actual_iris_c, pred_i_array_c, average="macro")
  f1_array_c.append(f1_s_c)

print("Average accuracy:", np.array(accuracy_array_c).mean())
print("Average macro f1 score:", np.array(f1_array_c).mean())

"""## Wine Dataset

### Prepare Data
"""

from sklearn.datasets import load_wine
wine = load_wine()
samples_wine = pd.DataFrame(wine["data"], columns = wine["feature_names"])
samples_wine["type"] = wine["target"]
if samples_wine.isnull().values.any():
  samples_wine = samples_wine.dropna(axis=0)

"""### Evaluated by Wine Dataset"""

samples_w_train, samples_w_test = train_test_split(samples_wine, train_size=0.8, random_state=42)
dt = Tree()
dt.fit(samples_w_train, "type")

print()
print("The structure of the decision tree:")
dt.root.pretty_print(" ")

train_part_w = list()
for wind, wdata in samples_w_train.iterrows():
  p_train_ = dt.root.predict(wdata)
  train_part_w.append(p_train_)
type_train_w = samples_w_train["type"]
actual_train_w = type_train_w.values.tolist()

pred_w_array = list()
for ind, data in samples_w_test.iterrows():
  pred = dt.root.predict(data)
  pred_w_array.append(pred)

type_w = samples_w_test["type"]
actual_wine = type_w.values.tolist()

print()
print("The accuracy for the training set:", accuracy_score(actual_train_w, train_part_w))
print("The performance of the decision tree for the test set:")
print("Confusion Matrix:")
print(confusion_matrix(actual_wine, pred_w_array))
print("The accuracy for the test set:", accuracy_score(actual_wine, pred_w_array))
print("The macro f1 score for the test set:", f1_score(actual_wine, pred_w_array, average="macro"))

"""### Evaluated by Wine Dataset (train_size = 0.65)"""

samples_w_train_, samples_w_test_ = train_test_split(samples_wine, train_size=0.65, random_state=42)
dt1 = Tree()
dt1.fit(samples_w_train_, "type")

print()
print("The structure of the decision tree:")
dt1.root.pretty_print(" ")

train_part_w_ = list()
for wind_, wdata_ in samples_w_train_.iterrows():
  p_train_w = dt.root.predict(wdata_)
  train_part_w_.append(p_train_w)
type_train_w_ = samples_w_train_["type"]
actual_train_w_ = type_train_w_.values.tolist()

pred_w_array_ = list()
for ind, data in samples_w_test_.iterrows():
  pred = dt.root.predict(data)
  pred_w_array_.append(pred)

type_w_ = samples_w_test_["type"]
actual_wine_ = type_w_.values.tolist()

print()
print("The accuracy for the training set:", accuracy_score(actual_train_w_, train_part_w_))
print("The performance of the decision tree for the test set:")
print("Confusion Matrix:")
print(confusion_matrix(actual_wine_, pred_w_array_))
print("The accuracy for the test set:", accuracy_score(actual_wine_, pred_w_array_))
print("The macro f1 score for the test set:", f1_score(actual_wine_, pred_w_array_, average="macro"))

"""### Estimate the Accuracy and the Macro F1 Score over 50 Training Times (train_size = 0.65)"""

accuracy_array = []
f1_array = []
for i in range(0, 50):
  samples_w_train, samples_w_test = train_test_split(samples_wine, train_size=0.65, random_state=i)  
  tree_wine = Tree()
  tree_wine.fit(samples_w_train, "type")
  pred_w_array = list()
  for ind, data in samples_w_test.iterrows():
    pred = tree_wine.root.predict(data)
    pred_w_array.append(pred)
  type_w = samples_w_test["type"]
  actual_wine = type_w.values.tolist()
  acc = accuracy_score(actual_wine, pred_w_array)
  accuracy_array.append(acc)
  f1_s = f1_score(actual_wine, pred_w_array, average="macro")
  f1_array.append(f1_s)

print ("Average accuracy:", np.array(accuracy_array).mean())
print("Average macro f1 score:", np.array(f1_array).mean())