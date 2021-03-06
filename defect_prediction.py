# -*- coding: utf-8 -*-
"""Defect Prediction

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19Swhz5jh6_vIdJM7ma9ozEsMlPbJdDGE
"""

from google.colab import drive
drive.mount('/content/drive')

# IMPORTING DATA MANIPULATION AND STANDARD LIBRARIES

import numpy as np
import pandas as pd
import cv2
import os
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split


# IMPORTING THE FRAMEWORK LIBRARIES
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense,Flatten,Activation,Dropout,AveragePooling2D,Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing.image import load_img
from sklearn.preprocessing import LabelBinarizer
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications import ResNet50V2
from tensorflow.keras.applications import resnet_v2
from sklearn.metrics import confusion_matrix, classification_report

# PATHS
labels_path = "drive/MyDrive/CV Hackathon/Training Data/Labels/Train_DefectType_PrithviAI.csv"
train_path = "drive/MyDrive/CV Hackathon/Training Data/Images Unzipped/Images/"

# CONSIDERING ONLY THOSE IMAGES WHICH EXISTS
labels = pd.read_csv(labels_path)
exist = []
for i in tqdm(labels['images id']):
    if os.path.exists(train_path+i):
      exist.append(i)
labels = labels[labels['images id'].isin(exist)]

# WE TOOK ONLY 250 IMAGES, BECAUSE ELSEWISE THE GPU MEMORY WAS GETTING EXHAUSTED
x=[]
y = []
i = 0
for file,label in tqdm(zip(labels['images id'].values[-300:],labels['defect_flag'].values[-300:])):
    if i < 250:
      img = cv2.imread(train_path + file)
      img = cv2.resize(img,(200,820))
      img = resnet_v2.preprocess_input(img)
      x.append(img)
      y.append(label)
      i = i+1
x = np.array(x).astype(np.float32)
y = np.array(y).astype(np.int32)

# SPLITTING THE DATA INTO TEST AND TRAIN SET
X_train, X_test, y_train, y_test = train_test_split(x,y, test_size=0.2,stratify=y, random_state=42)

# INAGE AUGMENTATION

img_gen=ImageDataGenerator(rotation_range=20,
                           width_shift_range=0.15,
                           height_shift_range=0.15,
                           fill_mode='nearest',
                           zoom_range=0.15,
                           shear_range=0.2,
                           horizontal_flip=True)

train_image_gen = img_gen.flow(X_train,y_train)
test_image_gen = img_gen.flow(X_test,y_test)

# MAKING MODEL USING RESNET 50
baseModel = ResNet50V2(weights="imagenet", include_top=False,input_tensor=Input(shape=(200, 820, 3)))
headModel = baseModel.output
headModel = AveragePooling2D(pool_size=(7, 7))(headModel)
headModel = Flatten(name="flatten")(headModel)
headModel = Dense(512, activation="relu")(headModel)
headModel = Dropout(0.8)(headModel)
headModel = Dense(1, activation="softmax")(headModel)

model = Model(inputs=baseModel.input, outputs=headModel)

# HYPERPARAMETER
lr = 0.0001
epochs = 40
opt = Adam(lr=lr, decay=lr/epochs)
model.compile(loss="binary_crossentropy", optimizer=opt,metrics=["accuracy"])

earlystop=EarlyStopping(monitor='val_loss',patience=5)

from sklearn.metrics import accuracy_score

accuracy = []
epoch = range(1,20,4)
for i in epoch:
    history=model.fit(train_image_gen,validation_data=test_image_gen,epochs=i,callbacks=[earlystop])
    y_pred = model.predict(test_image_gen)
    accuracy.append(accuracy_score(y_pred,y_test))

import matplotlib.pyplot as plt
epochs = range(1,20,4)
plt.plot(accuracy,epochs)
plt.show()

import seaborn as sns
plt.figure(figsize=(15,8))
sns.lineplot(epoch,accuracy)
plt.show()

y_pred

df = pd.DataFrame(y_pred)

df.to_csv("prediction2.csv",index = True)

