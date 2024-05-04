from copy import deepcopy
from sklearn.model_selection import KFold
from sklearn.metrics import recall_score, accuracy_score, precision_score
from sklearn.base import clone
from hdp_model_trainer import HdpModelTrainer

class HdpModelEvaluator():
    def __init__(self, model, pipeline, random_state=100):
        self.__model = model
        self.__pipeline = pipeline
        self.__random_state = random_state
        
    def kfold_cross_val(self, X_train, y_train, threshold=0.5):
        kf = KFold(n_splits=5)
        accuracies = []
        precisions = []
        recalls = []
        for fold, (train_index, val_index) in enumerate(kf.split(X_train), 1):
            X_train_fold = X_train.iloc[train_index].copy()
            y_train_fold = y_train.iloc[train_index].copy()
            X_val_fold = X_train.iloc[val_index].copy()
            y_val_fold = y_train.iloc[val_index].copy() 
            pipeline = deepcopy(self.__pipeline)
            X_train_fold = pipeline.fit_transform(X_train_fold)
            X_val_fold = pipeline.transform(X_val_fold)
            trainer = HdpModelTrainer(clone(self.__model), self.__random_state)
            trainer.train(X_train_fold, y_train_fold, threshold)
            y_pred = trainer.predict(X_val_fold)
            accuracies.append(accuracy_score(y_val_fold, y_pred))
            precisions.append(precision_score(y_val_fold, y_pred, average="binary"))
            recalls.append(recall_score(y_val_fold, y_pred, average="binary"))
            
        return {"mean_accuracy": sum(accuracies)/len(accuracies),
                "mean_precision": sum(precisions)/len(precisions),
                "mean_recall": sum(recalls)/len(recalls)}

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
        
        return {"test_accuracy": accuracy_score(y_test_copy, y_pred), 
                "test_precision": precision_score(y_test_copy, y_pred, average="binary"),
                "test_recall": recall_score(y_test_copy, y_pred, average="binary")}
    