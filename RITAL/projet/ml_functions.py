from sklearn import (linear_model, 
                     ensemble,
                     tree,
                     decomposition, 
                     naive_bayes, 
                     neural_network,
                     svm,
                     metrics,
                     preprocessing, 
                     model_selection, 
                     pipeline,)
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from xgboost import XGBClassifier

red_code = '\033[91m'
blue_code = '\033[94m'
green_code = '\033[92m'
yellow_code = '\033[93m'
reset_code = '\033[0m'

def analyze_logistic_regression(data, vectorizer):
    """
    Effectue une analyse de classification en utilisant un modèle de régression logistique.

    Args:
        data: DataFrame des données
        vectorizer: Un objet de vectorisation utilisé pour transformer les données textuelles en représentation numérique.

    Returns:
        acc: Accuracy
        f1: F1 score
        auc: Area under the ROC Curve
    """
    # Diviser les données en ensembles d'entraînement et de test
    X_text_train, X_text_test, y_train, y_test = model_selection.train_test_split(data['text'], data['label'], test_size=0.2, random_state=42)

    # Transformation des données d'entraînement en utilisant le vectoriseur
    X_train = vectorizer.fit_transform(X_text_train)
    # Transformation des données de test en utilisant le même vectoriseur
    X_test = vectorizer.transform(X_text_test)

    # Initialiser un modèle de régression logistique
    clf = linear_model.LogisticRegression(solver='lbfgs', max_iter=1000)
    # Entraîner le modèle sur les données d'entraînement
    clf.fit(X_train, y_train)

    # Prédire les étiquettes des données de test
    y_pred = clf.predict(X_test)

    # Prédire les probabilités des classes positives pour les données de test
    y_prob = clf.predict_proba(X_test)[:,1]
    
    # Calcul des métriques de performance
    fpr, tpr, thresholds = metrics.roc_curve(y_test, y_prob)
    auc = metrics.auc(fpr, tpr)
    f1 = metrics.f1_score(y_test, y_pred)
    acc = metrics.accuracy_score(y_test, y_pred)

    # Affichage du rapport de classification
    report = metrics.classification_report(y_test, y_pred)
    # print(report)

    print(f'{green_code}Accuracy :\t{acc}{reset_code}')
    print(f'{green_code}F1 score :\t{f1}{reset_code}')
    print(f'{green_code}AUC :\t\t{auc}{reset_code}')
    #return acc, f1, auc



def count_analyze_logistic_regression(data, **count_vectorizer_args):
    vectorizer = CountVectorizer(**count_vectorizer_args)
    return analyze_logistic_regression(data, vectorizer)



def tfidf_analyze_logistic_regression(data, **tfidf_vectorizer_args):
    vectorizer = TfidfVectorizer(**tfidf_vectorizer_args)
    return analyze_logistic_regression(data, vectorizer)