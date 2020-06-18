'''
x1,x2输入,2个cell,每个cell5个隐含单元，以最后一个单元的输出作为softamx的输入


'''
import tensorflow as tf
import numpy as np

tf.reset_default_graph()

sentences = [ "i like a dog", "i love a coffee", "i hate a milk"]

word_list = " ".join(sentences).split()
word_list = list(set(word_list))
word_dict = {w: i for i, w in enumerate(word_list)}
number_dict = {i: w for i, w in enumerate(word_list)}
n_class = len(word_dict) # 7




# TextRNN Parameter
n_step = 3  # number of cells(= number of Step)
n_hidden = 5  # number of hidden units in one cell

def make_batch(sentences):
    input_batch = []
    target_batch = []
    for sen in sentences:
        word = sen.split()
        input = [word_dict[n] for n in word[:-1]]
        target = word_dict[word[-1]]
        input_batch.append(np.eye(n_class)[input])
        target_batch.append(np.eye(n_class)[target])
    return input_batch,target_batch

# model
X=tf.placeholder(tf.float32,[None,n_step,n_class])  # 2,5
print(tf.shape(X))
Y=tf.placeholder(tf.float32,[None,n_class]) # 7

W=tf.Variable(tf.random_normal([n_hidden,n_class]))
b=tf.Variable(tf.random_normal([n_class]))

# RNN
# cell=tf.nn.rnn_cell.BasicRNNCell(n_hidden)

# LSTM
# cell = tf.nn.rnn_cell.BasicLSTMCell(n_hidden)

# GRU
cell = tf.nn.rnn_cell.GRUCell(n_hidden)
'''
tf.nn.dynamic_rnn(
    cell,
    inputs,
    sequence_length=None,
    initial_state=None,
    dtype=None,
    parallel_iterations=None,
    swap_memory=False,
    time_major=False,
    scope=None
)

outputs:
    如果time_major==True，outputs形状为 [n_step, batch_size, n_hidden ]（要求rnn输入与rnn输出形状保持一致）
    如果time_major==False（默认），outputs形状为 [ batch_size, n_step, n_hidden ]

state:
    state是最终的状态，也就是序列中最后一个cell输出的状态
    一般情况下state的形状为 [batch_size, n_hidden]
    但当输入的cell为BasicLSTMCell时，state的形状为[2，batch_size, cell.output_size ]，其中2也对应着LSTM中的cell state和hidden state
'''
# 单向
outputs_1,states = tf.nn.dynamic_rnn(cell,X,dtype=tf.float32)


# outputs:[batch_size,n_step,n_hidden]
outputs_ = tf.transpose(outputs_1,[1,0,2]) # [n_step, batch_size, n_hidden]
outputs = outputs_[-1]
# model = tf.nn.softmax(tf.matmul(outputs,W)+b)
model = tf.matmul(outputs,W)+b
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=model, labels=Y))
optimizer = tf.train.AdamOptimizer(0.001).minimize(cost)

prediction = tf.cast(tf.argmax(model, 1), tf.int32)

# Training
init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)

input_batch, target_batch = make_batch(sentences)



for epoch in range(5000):
    _, loss = sess.run([optimizer, cost], feed_dict={X: input_batch, Y: target_batch})
    if (epoch + 1) % 1000 == 0:
        print('Epoch:', '%04d' % (epoch + 1), 'cost =', '{:.6f}'.format(loss))

input = [sen.split()[:2] for sen in sentences]

predict = sess.run([prediction], feed_dict={X: input_batch})
print([sen.split()[:2] for sen in sentences], '->', [number_dict[n] for n in predict[0]])


