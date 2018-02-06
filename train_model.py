import random
import uuid
import pickle
import itertools
import numpy as np
import matplotlib.pyplot as plt

from sklearn import svm, linear_model, neighbors
from const import TAG_MAP
from sklearn.metrics import confusion_matrix

NUM_VECTORS_PER_POINT = 2
VECTOR_SIZE = 300
NUM_TRAIN = 9
EPOCHS_TRAIN = 250
TOTAL_CHUNKS = 10

def _get_data_chunk(chunk_num):
    data, labels = [], []
    less_than_num = 0
    with open(f'questions_as_embeddings{chunk_num}.pkl', 'rb') as f:
        questions = pickle.load(f)
        for id, q in questions.items():
            num_tags = len(q['tags'])
            if num_tags != 1: continue
            tag = TAG_MAP[q['tags'][0]]
            test_point = np.zeros((NUM_VECTORS_PER_POINT * VECTOR_SIZE,))
            title = q['title']
            body = q['body']
            if len(body) < NUM_VECTORS_PER_POINT - 1:
                less_than_num += 1
            if title:
                test_point[0:VECTOR_SIZE] = title[0]
            for i in range(0, NUM_VECTORS_PER_POINT - 1):
                test_point[VECTOR_SIZE*(i+1):VECTOR_SIZE*(i+2)] = body[i % len(body)] # repeat vectors if not enough
            data.append(test_point)
            labels.append(tag)
        # print(f'Found {less_than_num} questions with not enough sentences in a chunk of size {len(questions)} ({less_than_num / len(questions) * 100}%) for chunk {chunk_num}')
    return np.array(data), np.array(labels)


def get_mean_and_stddev():
    mean, var = np.zeros((NUM_VECTORS_PER_POINT * VECTOR_SIZE,)), np.zeros((NUM_VECTORS_PER_POINT * VECTOR_SIZE,))
    for chunk_num in range(1, TOTAL_CHUNKS + 1):
        data, _ = _get_data_chunk(chunk_num)
        mean += np.mean(data, axis=0)
    mean /= TOTAL_CHUNKS
    for chunk_num in range(1, TOTAL_CHUNKS + 1):
        data, _ = _get_data_chunk(chunk_num)
        var += np.var(data, axis=0)
    var /= TOTAL_CHUNKS
    return mean, np.sqrt(var)


def get_normalized_chunk(chunk_num, mean, std_dev):
    data, labels = _get_data_chunk(chunk_num)
    data -= mean
    data /= std_dev
    return data, labels


def print_prediction_stats(model, mean, std_dev):
    test_data = []
    test_labels = []

    for i in range(NUM_TRAIN + 1, TOTAL_CHUNKS + 1):
        chunk_data, chunk_labels = get_normalized_chunk(i, mean, std_dev)
        test_data.extend(chunk_data)
        test_labels.extend(chunk_labels)

    predictions = model.predict(test_data)
    assert len(predictions) == len(test_labels)

    correct = 0
    for pred, actual in zip(predictions, test_labels):
        if pred == actual:
            correct += 1

    print(f'Model scored {correct} out of {len(predictions)} correct ({correct / len(predictions) * 100}%)')


def get_confustion_matrix(model):
    test_data = []
    test_labels = []

    for i in range(NUM_TRAIN + 1, TOTAL_CHUNKS + 1):
        chunk_data, chunk_labels = get_normalized_chunk(i, mean, std_dev)
        test_data.extend(chunk_data)
        test_labels.extend(chunk_labels)

    predictions = model.predict(test_data)
    return confusion_matrix(test_labels, predictions)


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


mean, std_dev = get_mean_and_stddev()

model = linear_model.SGDClassifier(warm_start=True)
# model = svm.SVC(kernel='linear') #
# model = neighbors.KNeighborsClassifier()
# EPOCHS_TRAIN = 1
print(model.get_params())

for _ in range(EPOCHS_TRAIN):
    chunk_nums = [x for x in range(1, NUM_TRAIN + 1)]
    random.shuffle(chunk_nums)
    for i in chunk_nums:
        train_data, train_labels = get_normalized_chunk(i, mean, std_dev)
        print(f'Fitting chunk {chunk_nums.index(i)+1}/{len(chunk_nums)}{" " * 40}', end='\r')
        model.partial_fit(train_data, train_labels, classes=[c for c in TAG_MAP.values()])
        # model.fit(train_data, train_labels)
        print(f'Fit chunk {chunk_nums.index(i)+1}/{len(chunk_nums)}{" " * 40}', end='\r')
    print(f'Trained {NUM_TRAIN} chunks. {_+1}th iteration out of {EPOCHS_TRAIN}.')
    print_prediction_stats(model, mean, std_dev)

conf_matrix = get_confustion_matrix(model)

plt.figure(figsize=(14,14))
plot_confusion_matrix(conf_matrix, TAG_MAP.keys(), title=f'Confusion Matrix: {EPOCHS_TRAIN} epochs on a {model}')
plt.savefig(f'confusion_matrix_{uuid.uuid4()}.pdf')
plt.show()

