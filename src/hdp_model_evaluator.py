from copy import deepcopy
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import recall_score
from sklearn.base import clone
from hdp_model_trainer import HdpModelTrainer

class HdpModelEvaluator():
    def __init__(self, model, pipeline, random_state=100):
        self.__model = model
        self.__pipeline = pipeline
        self.__random_state = random_state
        
    def kfold_cross_val(self, X_train, y_train, threshold=0.5):
        recalls = []
        for i in tqdm(range(10)):
            kf = StratifiedKFold(n_splits=10)
            X_train_shuffled = X_train.sample(frac=1).copy()
            y_train_shuffled = y_train.iloc[X_train_shuffled.index].copy()
            X_train_shuffled = X_train_shuffled.reset_index(drop=True)
            y_train_shuffled = y_train_shuffled.reset_index(drop=True)
            for fold, (train_index, val_index) in tqdm(enumerate(kf.split(X_train_shuffled, y_train_shuffled), 1)):
                X_train_fold = X_train_shuffled.iloc[train_index].copy()
                y_train_fold = y_train_shuffled.iloc[train_index].copy()
                X_val_fold = X_train_shuffled.iloc[val_index].copy()
                y_val_fold = y_train_shuffled.iloc[val_index].copy() 
                pipeline = deepcopy(self.__pipeline)
                X_train_fold = pipeline.fit_transform(X_train_fold)
                X_val_fold = pipeline.transform(X_val_fold)
                trainer = HdpModelTrainer(clone(self.__model), self.__random_state)
                trainer.train(X_train_fold, y_train_fold, threshold)
                y_pred = trainer.predict(X_val_fold)
                recalls.append(recall_score(y_val_fold, y_pred, average="binary"))
        
        return {"mean_recall": sum(recalls)/len(recalls), "std_recall": np.std(recalls), "recalls": recalls}

    def test_scores(self, X_train, y_train, X_test, y_test, threshold=0.5):
        X_train_copy = X_train.copy()
        X_test_copy = X_test.copy()
        y_train_copy = y_train.copy()
        y_test_copy = y_test.copy()
        pipeline = deepcopy(self.__pipeline)
        X_train_copy = pipeline.fit_transform(X_train_copy)
        X_test_copy = pipeline.transform(X_test_copy)
        trainer = HdpModelTrainer(clone(self.__model), self.__random_state)
        trainer.train(X_train_copy, y_train_copy, threshold)
        y_pred = trainer.predict(X_test_copy)
        
        return {"test_recall": recall_score(y_test_copy, y_pred, average="binary")}
    