from functools import reduce
from typing import Any, Dict, List
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.ml.tuning import CrossValidatorModel
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def get_df_with_weight_column(df: DataFrame) -> DataFrame:
    """
    Add a column to the dataframe with the weight of each instance, inversely
    proportional to their frequency in the dataframe.

    Parameters
    ----------
    df : DataFrame
        The dataframe to which the weight column will be added.
    
    Returns
    -------
    DataFrame
        The dataframe with the weight column added.
    """
    temp = df.groupby('label').count()
    new_df = df.join(temp, 'label', how = 'leftouter')
    num_labels = df.select(F.countDistinct(df.label)).first()[0]
    df = new_df.withColumn('weightCol', (new_df.count()/(num_labels * new_df['count'])))
    df = df.drop(F.col('count'))
    return df

def get_df_with_fold_column(df, n_folds: int) -> DataFrame:
    """
    Add a column to the dataframe with the fold of each instance that
    indicates the fold number of the k-fold cross validation.

    Parameters
    ----------
    df : DataFrame
        The dataframe to which the fold column will be added.
    n_folds : int
        The number of folds to be used in the k-fold cross validation.

    Returns
    -------
    DataFrame
        The dataframe with the fold column added.
    """
    dfs_by_label = []
    df = df.withColumn('idx_main', F.monotonically_increasing_id())

    dates = df.select('Date').distinct().collect()

    labels = df.select('label').distinct().collect()
    sorted_labels = sorted([row['label'] for row in labels])

    for d in dates:
        for label in sorted_labels:
            sub_df = df.filter(df.label == label).filter(df.Date == d.Date)

            instances_per_fold = sub_df.count() / n_folds

            sub_df = sub_df.withColumn('idx', F.monotonically_increasing_id())
            sub_df = sub_df.withColumn('foldCol', (F.col('idx') / instances_per_fold).cast('int'))
            sub_df = sub_df.drop('idx')
            dfs_by_label.append(sub_df)

    df = reduce(DataFrame.unionByName, dfs_by_label)
    df = df.orderBy('idx_main')
    return df.drop('idx_main')

def _get_labels_f1_by_threshold(
    preds: DataFrame,
    thresholds: List[float]
    ) -> Dict[float, Dict[float, float]]:
    """
    Get the F1 scores for each label for each threshold.

    Parameters
    ----------
    preds : DataFrame
        The dataframe with the predictions.
    thresholds : list of float
        The thresholds to be used.

    Returns
    -------
    { float: { float: float } }
        The F1 scores for each label for each threshold.
    """
    labels_f1_by_threshold = {}

    # Loop through the labels.
    for c in preds.select('label').distinct().collect():
        labels_f1_by_threshold[c.label] = {}
        # Set the labels as binary.
        probs = preds.withColumn(
            'label',
            F.when(F.col('label') == c.label, 1.).otherwise(0.))
        # Get the probability of the current label.
        probs = probs.select('label', 'probability').rdd.map(
            lambda row: (
                float(row['probability'][int(c.label)]),
                float(sum(list(row['probability'][:int(c.label)]) + list(row['probability'][int(c.label)+1:]))),
                float(row['label'])))
        probs = probs.toDF(['probability', 'other_probabilities', 'label'])

        # Loop through the thresholds:
        for t in thresholds:
            # Set the predictions for the current threshold.
            pr = probs.withColumn(
                'prediction',
                F.when(
                    F.col('probability') / t >= F.col('other_probabilities') / .5, 1.).otherwise(0.))
            # Get the metrics of the current threshold.
            metrics = MulticlassMetrics(pr.select('prediction', 'label').rdd)
            # Append the F1 scores.
            labels_f1_by_threshold[c.label][t] = metrics.fMeasure(1.)

    return labels_f1_by_threshold

def get_metrics(
    preds: DataFrame,
    normalize_confusion_matrix: bool = False
    ) -> Dict[str, Any]:
    """
    Get the metrics of the given predictions.

    Parameters
    ----------
    preds : DataFrame
        The dataframe with the predictions.
    normalize_confusion_matrix : bool, optional
        Whether to normalize the confusion matrix or not, by default False.

    Returns
    -------
    { str: Any }
        The metrics of the given predictions.
    """
    # Get the metrics.
    metrics = MulticlassMetrics(preds.select('prediction', 'label').rdd)

    # Get the accuracy.
    accuracy = metrics.accuracy

    # Get the confusion matrix.
    confusion_matrix = metrics.confusionMatrix().toArray()
    if normalize_confusion_matrix:
        confusion_matrix = confusion_matrix / (confusion_matrix.sum(axis=0))

    # Get the F1 scores.
    f1_scores = {}
    for c in preds.select('label').distinct().orderBy('label').collect():
        f1 = metrics.fMeasure(c.label)
        f1_scores[c.label] = f1

    # Get the macro F1 score.
    macro_f1 = sum(f1_scores.values()) / len(f1_scores.values())

    return {
        'accuracy': accuracy,
        'F1 macro': macro_f1,
        'F1 scores': f1_scores,
        'confusion matrix': confusion_matrix }

def get_average_validation_results(
    fit: CrossValidatorModel,
    df: DataFrame,
    apply_threshold_selection: bool,
    thresholds: List[float] = np.linspace(0., 1., 10, endpoint=False)[1:]
    ) -> Dict[str, Any]:
    """
    Get the average validation results of the given CrossValidatorModel.
    

    Parameters
    ----------
    fit : CrossValidatorModel
        The CrossValidatorModel to get the average validation results.
    df : DataFrame
        The dataframe to be used in the validation.
    apply_threshold_selection : bool
        Whether to apply threshold selection or not.
    thresholds : list of float, optional
        The thresholds to be used in the threshold selection, by default
        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9].

    Returns
    -------
    { str: Any }
        The average validation results of the given CrossValidatorModel.
    """
    accuracies = []
    f1_macros = []
    f1s = []
    confusion_matrices = []
    labels_f1_by_threshold = []

    # Get index of best model in terms of hyperparameters.
    best_model_index = np.argmax(fit.avgMetrics)

    # Loop thrugh the folds.
    for i, m in enumerate(fit.subModels):
        # Get the validation dataframe for the given fold.
        sub_df = df.where(F.col('foldCol') == i)

        # Get the prediction of the given fold.
        preds = m[best_model_index].transform(sub_df)

        res = get_metrics(preds)
        accuracies.append(res['accuracy'])
        f1_macros.append(res['F1 macro'])
        f1s.append(res['F1 scores'])
        confusion_matrices.append(res['confusion matrix'])

        # Get F1s by thresholds.
        if apply_threshold_selection:
            labels_f1_by_threshold.append(
                _get_labels_f1_by_threshold(preds, thresholds))

    # Average the metrics.
    avg_accuracy = sum(accuracies) / len(accuracies)
    avg_f1_macro = sum(f1_macros) / len(f1_macros)
    avg_confusion_matrix = sum(confusion_matrices) / len(confusion_matrices)
    avg_confusion_matrix = avg_confusion_matrix / (avg_confusion_matrix.sum(axis=0))
    avg_f1s = {}
    for c in df.select('label').distinct().collect():
        values = [f1[c.label] for f1 in f1s]
        avg_f1s[c.label] = sum(values) / len(values)

    avg_labels_f1_by_threshold = {}
    if apply_threshold_selection:
        for c in df.select('label').distinct().orderBy('label').collect():
            avg_labels_f1_by_threshold[c.label] = {}
            for t in thresholds:
                values = [f1_t[c.label][t] for f1_t in labels_f1_by_threshold]
                avg_labels_f1_by_threshold[c.label][t] = sum(values) / len(values)

    return {
        'average accuracy': avg_accuracy,
        'average F1 macro': avg_f1_macro,
        'average F1 scores': avg_f1s,
        'average confusion matrix': avg_confusion_matrix,
        'average F1 scores by threshold': avg_labels_f1_by_threshold }

def print_results(
    accuracy: float,
    f1_macro: float,
    f1s: Dict[float, float],
    confusion_matrix: np.ndarray
    ) -> None:
    """
    Print the results of the given metrics.

    Parameters
    ----------
    accuracy : float
        The accuracy.
    f1_macro : float
        The F1 macro.
    f1s : { float: float }
        The F1 scores by label.
    confusion_matrix : ndarray
        The confusion matrix.
    """
    print(f'Accuracy: {accuracy:.3f}')
    print(f'F1 Macro: {f1_macro:.3f}')
    print('F1 scores:')
    for k, v in f1s.items():
        print(f'\tLabel {int(k)}: {v:.3f}')

    sns.heatmap(confusion_matrix, annot=True)
    plt.xlabel('Prediction')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()
