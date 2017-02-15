# coding=utf-8
from csv import QUOTE_MINIMAL
from csv import writer

from keras.utils.np_utils import to_categorical
from numpy import asarray

from LoggerUtils import LoggerUtils
from Utils import scale_image
from learning.Metrics import supported_metrics

log = LoggerUtils.get_logger('LearningEvaluator')


def categorize(class_values):
    return to_categorical(class_values, 2)


def scale(img_list, size):
    scaled = asarray([scale_image(i, size) for i in img_list])
    return scaled.reshape(scaled.shape[:1] + (1,) + scaled.shape[1:])


def metric_value(metric, expected, actual):
    return metric[1](expected, actual) * metric[2]


def metric_string(metric_values):
    return '\n'.join(
        ['{}: {}'.format(k, v) for k, v in
         zip([i[0] for i in supported_metrics], metric_values)])


def execute(dataset, models, iterations, csvwriter):
    csvwriter.writerow(['Iteration', 'Model']
                       + [x[0] for x in supported_metrics])

    for i in range(1, iterations + 1):
        log.info('Bootstrap iteration {}'.format(i))
        (x_train, y_train), (x_test, y_test) = dataset.bootstrap_iter()
        for model in models:
            log.debug('Model {}'.format(type(model).__name__))

            classifier = model.build()
            classifier.compile(loss='binary_crossentropy',
                               optimizer='Adadelta')

            x_train_scaled = scale(x_train, model.size)
            x_test_scaled = scale(x_test, model.size)
            y_train_categorized = categorize(y_train)

            log.info("Training network")
            classifier.fit(x_train_scaled, y_train_categorized,
                           batch_size=1,
                           nb_epoch=1,
                           verbose=1,
                           shuffle=False)

            result = list(classifier.predict_classes(x_test_scaled,
                                                     batch_size=32))
            metric_values = [metric_value(x, y_test, result)
                             for x in supported_metrics]
            metrics = [str(i), type(model).__name__] + metric_values

            log.info('Iteration: {}, model: {}, {}'
                     .format(i, type(model).__name__,
                             metric_string(metric_values)))

            csvwriter.writerow(metrics)


def execute_learning(dataset, models, iterations, out_file):
    with open(out_file, 'w', newline='') as result_file:
        csvwriter = writer(result_file,
                           delimiter=',',
                           quotechar='"',
                           quoting=QUOTE_MINIMAL)
        execute(dataset, models, iterations, csvwriter)
