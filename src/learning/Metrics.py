# coding=utf-8
from sklearn.metrics import accuracy_score
from sklearn.metrics import auc
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_curve

epsilon = 10e-8


def get_basic_info(true, pred):
    conf_matrix = confusion_matrix(true, pred)

    tp = conf_matrix[0][0]
    tn = conf_matrix[1][1]

    fp = conf_matrix[1][0]
    fn = conf_matrix[0][1]

    return tp, tn, fp, fn


def matthews_correlation(true, pred):
    return matthews_corrcoef(true, pred)


def precision(true, pred):
    return precision_score(true, pred)


def recall(true, pred):
    return recall_score(true, pred)


def specificity(true, pred):
    tp, tn, fp, fn = get_basic_info(true, pred)
    return tn / (fp + tn + epsilon)


def accuracy(true, pred):
    return accuracy_score(true, pred)


def npv(true, pred):
    tp, tn, fp, fn = get_basic_info(true, pred)
    return tn / (tn + fn + epsilon)


def fmeasure(true, pred):
    return f1_score(true, pred)


def roc_auc(true, pred):
    fpr, tpr, _ = roc_curve(true, pred)
    return auc(fpr, tpr)


supported_metrics = [
    ('accuracy (ACC)', accuracy, 100.0),
    ('area under ROC curve (AUC)', roc_auc, 1.0),
    ('recall (SENS)', recall, 100.0),
    ('specificity (SPEC)', specificity, 100.0),
    ('precision (PPV)', precision, 100.0),
    ('negative predictive value (NPV)', npv, 100.0),
    ('fmeasure (F1)', fmeasure, 100.0),
    ('matthews correlation (MCC)', matthews_correlation, 100.0),
]
