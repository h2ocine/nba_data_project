from sklearn import (
    linear_model, 
    ensemble,
    tree,
    decomposition, 
    naive_bayes, 
    neural_network,
    svm,
    metrics,
    preprocessing, 
    model_selection, 
    pipeline,
)
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, auc, roc_curve
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer
from gensim.models import Word2Vec
from gensim.models.keyedvectors import KeyedVectors
import numpy as np



red_code = '\033[91m'
blue_code = '\033[94m'
green_code = '\033[92m'
yellow_code = '\033[93m'
reset_code = '\033[0m'


# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------


class Word2VecVectorizer:
    def __init__(self, word2vec_model):
        self.word2vec_model = word2vec_model

    def transform(self, data):
        vectors = []
        for sentence in data:
            sentence_vector = np.mean([self.word2vec_model[word] for word in sentence if word in self.word2vec_model], axis=0)
            vectors.append(sentence_vector)
        return np.array(vectors)


class GloVeVectorizer:
    def __init__(self, glove_vectors):
        self.glove_vectors = glove_vectors

    def transform(self, data):
        vectors = []
        for sentence in data:
            sentence_vector = np.mean([self.glove_vectors[word] for word in sentence if word in self.glove_vectors], axis=0)
            vectors.append(sentence_vector)
        return np.array(vectors)
    


# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------


def analyze(data, vectorizer, model):
    """
    Effectue une analyse en utilisant le modèle spécifié.

    Args:
        data: DataFrame des données
        vectorizer: Un objet de vectorisation utilisé pour transformer les données textuelles en représentation numérique.
        model: Le modèle d'entraînement utilisé pour la classification.

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

    # Entraîner le modèle sur les données d'entraînement
    model.fit(X_train, y_train)

    # Prédire les étiquettes des données de test
    y_pred = model.predict(X_test)

    # Prédire les probabilités des classes positives pour les données de test
    # Prédire les probabilités des classes positives pour les données de test
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
    else:
        # Utiliser la décision de fonction de décision si le modèle ne prend pas en charge predict_proba
        y_prob = model.decision_function(X_test)

    # Calcul des métriques de performance
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    auc = metrics.auc(fpr, tpr)
    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)

    # Affichage du rapport de classification
    report = metrics.classification_report(y_test, y_pred)
    # print(report)

    print(f'{green_code}Accuracy :\t{acc}{reset_code}')
    print(f'{green_code}F1 score :\t{f1}{reset_code}')
    print(f'{green_code}AUC :\t\t{auc}{reset_code}')
    #return acc, f1, accuracy


# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
    

def logistic_regression_analyze(data, vectorizer):
    # Initialiser un modèle de régression logistique
    clf = linear_model.LogisticRegression(solver='lbfgs', max_iter=1000)

    # Utiliser la fonction "analyze" avec le modèle de régression logistique
    return analyze(data, vectorizer, clf)

# -------------------------------------------------------------------
# -------------------------------------------------------------------

def svm_analyze(data, vectorizer):
    # Initialiser un modèle SVM
    clf = SVC()

    # Utiliser la fonction "analyze" avec le modèle SVM
    return analyze(data, vectorizer, clf)

# -------------------------------------------------------------------
# -------------------------------------------------------------------

def decision_tree_analyze(data, vectorizer):
    # Initialiser un modèle d'arbre de décision
    clf = DecisionTreeClassifier()

    # Utiliser la fonction "analyze" avec le modèle d'arbre de décision
    return analyze(data, vectorizer, clf)

# -------------------------------------------------------------------
# -------------------------------------------------------------------

def random_forest_analyze(data, vectorizer):
    # Initialiser un modèle de forêt aléatoire
    clf = RandomForestClassifier()

    # Utiliser la fonction "analyze" avec le modèle d'arbre de décision
    return analyze(data, vectorizer, clf)


# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
# ------------------------------------------------------------------- ------------------------------------------------------------------- -------------------------------------------------------------------
    


def count_analyze(data, analyze_function, **count_vectorizer_args):
    vectorizer = CountVectorizer(**count_vectorizer_args)
    return analyze_function(data, vectorizer)

def tfidf_analyze(data, analyze_function, **tfidf_vectorizer_args):
    vectorizer = TfidfVectorizer(**tfidf_vectorizer_args)
    return analyze_function(data, vectorizer)

def word2vec_analyze(data, analyze_function, word2vec_model_path):
    word2vec_model = Word2Vec.load(word2vec_model_path)
    vectorizer = Word2VecVectorizer(word2vec_model)
    return analyze_function(data, vectorizer)

def glove_analyze(data, analyze_function, glove_vectors_path):
    glove_vectors = KeyedVectors.load_word2vec_format(glove_vectors_path, binary=False)
    vectorizer = GloVeVectorizer(glove_vectors)
    return analyze_function(data, vectorizer)

def hashing_analyze(data, analyze_function, **hashing_vectorizer_args):
    vectorizer = HashingVectorizer(**hashing_vectorizer_args)
    return analyze_function(data, vectorizer)


