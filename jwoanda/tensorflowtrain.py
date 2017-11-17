import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import preprocessing

import tensorflow as tf

from tensorflow.contrib.learn.python import learn as tflearn

def tfdnntrain(name, X_train, y_train):

    #scaler = preprocessing.StandardScaler()
    scaler = preprocessing.RobustScaler()
    scaler.fit(X_train)
    
    feature_columns = tflearn.infer_real_valued_columns_from_input(X_train)
    classifier = tflearn.DNNRegressor(hidden_units=[10, 20, 10], feature_columns=feature_columns)
    classifier.fit(scaler.transform(X_train), y_train, steps=2000, batch_size=1)

    return scaler, classifier

# class RNN:
#     def __init__(self):

#         # Parameters
#         learning_rate = 0.001
#         training_iters = 100000
#         batch_size = 128
#         display_step = 10
        
#         # Network Parameters
#         n_input = 28 # MNIST data input (img shape: 28*28)
#         n_steps = 28 # timesteps
#         self.n_hidden = 128 # hidden layer num of features
#         n_classes = 10 # MNIST total classes (0-9 digits)

#         # tf Graph input
#         self.x = tf.placeholder("float", [None, n_steps, n_input])
#         self.y = tf.placeholder("float", [None, n_classes])

#         # Define weights
#         self.weights = {
#             'out': tf.Variable(tf.random_normal([self.n_hidden, n_classes]))
#         }
#         self.biases = {
#             'out': tf.Variable(tf.random_normal([n_classes]))
#         }


#         def RNN(x, weights, biases):

#             # Prepare data shape to match `rnn` function requirements
#             # Current data input shape: (batch_size, n_steps, n_input)
#             # Required shape: 'n_steps' tensors list of shape (batch_size, n_input)

#             # Permuting batch_size and n_steps
#             x = tf.transpose(x, [1, 0, 2])
#             # Reshaping to (n_steps*batch_size, n_input)
#             x = tf.reshape(x, [-1, n_input])
#             # Split to get a list of 'n_steps' tensors of shape (batch_size, n_input)
#             x = tf.split(x, n_steps, 0)

#             # Define a lstm cell with tensorflow
#             lstm_cell = rnn.BasicLSTMCell(self.n_hidden, forget_bias=1.0)

#             # Get lstm cell output
#             outputs, states = rnn.static_rnn(lstm_cell, x, dtype=tf.float32)
            
#             # Linear activation, using rnn inner loop last output
#             return tf.matmul(outputs[-1], weights['out']) + biases['out']

#         def run(self):
        
#             pred = RNN(self.x, self.weights, self.biases)

#             # Define loss and optimizer
#             cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
#             optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

#             # Evaluate model
#             correct_pred = tf.equal(tf.argmax(pred,1), tf.argmax(y,1))
#             accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

#             # Initializing the variables
#             init = tf.global_variables_initializer()

#             # Launch the graph
#             with tf.Session() as sess:
#                 sess.run(init)
#                 step = 1
#                 # Keep training until reach max iterations
#                 while step * batch_size < training_iters:
#                     batch_x, batch_y = mnist.train.next_batch(batch_size)
#                     # Reshape data to get 28 seq of 28 elements
#                     batch_x = batch_x.reshape((batch_size, n_steps, n_input))
#                     # Run optimization op (backprop)
#                     sess.run(optimizer, feed_dict={x: batch_x, y: batch_y})
#                     if step % display_step == 0:
#                         # Calculate batch accuracy
#                         acc = sess.run(accuracy, feed_dict={x: batch_x, y: batch_y})
#                         # Calculate batch loss
#                         loss = sess.run(cost, feed_dict={x: batch_x, y: batch_y})
#                         print("Iter " + str(step*batch_size) + ", Minibatch Loss= " + \
#                               "{:.6f}".format(loss) + ", Training Accuracy= " + \
#                               "{:.5f}".format(acc))
#                     step += 1
#                 print("Optimization Finished!")

#                 # Calculate accuracy for 128 mnist test images
#                 test_len = 128
#                 test_data = mnist.test.images[:test_len].reshape((-1, n_steps, n_input))
#                 test_label = mnist.test.labels[:test_len]
#                 print("Testing Accuracy:", \
#                       sess.run(accuracy, feed_dict={x: test_data, y: test_label}))



# myrnn = RNN()
# RNN.run()
