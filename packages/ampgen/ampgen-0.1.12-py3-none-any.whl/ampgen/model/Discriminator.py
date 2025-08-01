import os
import argparse
import pandas as pd
import xgboost
from ampgen.model.features import get_pre_features
from sklearn.model_selection import train_test_split

def get_trained_model(model_path):
    # 如果已经存在模型文件，就直接加载
    model = xgboost.XGBClassifier()
    model.load_model(model_path)
    print(f"Loaded model from {model_path}")
    return model

def classify_sequences(model_path, sequences):
    # 加载候选序列特征
    candidate_data = get_pre_features(sequences)
    X = candidate_data.iloc[:, 1:].values
    model = get_trained_model(model_path)
    # 预测并拼回原始表格
    preds = model.predict(X)
    result = pd.DataFrame({"Sequence": sequences,"type": preds})

    return result

if __name__ == '__main__':
    pass