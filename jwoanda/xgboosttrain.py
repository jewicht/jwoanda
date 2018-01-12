try:
    import lzma
except ImportError:
    from backports import lzma
try:
    import cPickle as pickle
except:
    import pickle
import xgboost as xgb

def trainXGBoostMultiClass(name, X_train, y_train):
    model = xgb.XGBClassifier(max_depth=4, learning_rate=0.1, n_estimators=300)
    model.fit(X_train, y_train)

    with lzma.open(name, "wb", 5) as f:
        pickle.dump(model, f)
        f.close()
    
    return model

def trainXGBoostClassification(name, X_train, y_train):
    model = xgb.XGBRegressor(max_depth=4, learning_rate=0.1, n_estimators=300)
    model.fit(X_train, y_train)

    with lzma.open(name, "wb", 5) as f:
        pickle.dump(model, f)
        f.close()
    
    return model
