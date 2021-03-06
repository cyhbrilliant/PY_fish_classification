import tensorflow as tf
import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import vgg19_trainable_640360 as vgg19
import os
os.environ['CUDA_VISIBLE_DEVICES']='1'

file = h5py.File('H5fish_test3.h5','r')
DATA_ALL = file['DATA_ALL'][:]



#Network Strat
def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.001)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def batch_norm(inputs, is_training,is_conv_out=True,decay = 0.999):
    scale = tf.Variable(tf.ones([inputs.get_shape()[-1]]))
    beta = tf.Variable(tf.zeros([inputs.get_shape()[-1]]))
    pop_mean = tf.Variable(tf.zeros([inputs.get_shape()[-1]]), trainable=False)
    pop_var = tf.Variable(tf.ones([inputs.get_shape()[-1]]), trainable=False)
    if is_training:
        if is_conv_out:
            batch_mean, batch_var = tf.nn.moments(inputs,[0,1,2])
        else:
            batch_mean, batch_var = tf.nn.moments(inputs,[0])
        train_mean = tf.assign(pop_mean,pop_mean * decay + batch_mean * (1 - decay))
        train_var = tf.assign(pop_var,pop_var * decay + batch_var * (1 - decay))
        with tf.control_dependencies([train_mean, train_var]):
            return tf.nn.batch_normalization(inputs,
                batch_mean, batch_var, beta, scale, 0.001)
    else:
        return tf.nn.batch_normalization(inputs,
            pop_mean, pop_var, beta, scale, 0.001)



Xp = tf.placeholder(tf.float32, [None, 360, 640, 3])
Yp = tf.placeholder(tf.float32, [None, 8])


Wconv1=weight_variable([7,7,3,64])
Bconv1=bias_variable([64])
conv1=tf.nn.conv2d(Xp,Wconv1,strides=[1,2,2,1],padding='SAME')+Bconv1
conv1_bn=tf.nn.relu(batch_norm(conv1,False))

Wconv2=weight_variable([3,3,64,64])
Bconv2=bias_variable([64])
conv2=tf.nn.conv2d(conv1_bn,Wconv2,strides=[1,1,1,1],padding='SAME')+Bconv2
conv2_bn=tf.nn.relu(batch_norm(conv2,False))

Wconv3=weight_variable([5,5,64,128])
Bconv3=bias_variable([128])
conv3=tf.nn.conv2d(conv2_bn,Wconv3,strides=[1,2,2,1],padding='SAME')+Bconv3
conv3_bn=tf.nn.relu(batch_norm(conv3,False))


Wconv4=weight_variable([3,3,128,128])
Bconv4=bias_variable([128])
conv4=tf.nn.conv2d(conv3_bn,Wconv4,strides=[1,1,1,1],padding='SAME')+Bconv4
conv4_bn=tf.nn.relu(batch_norm(conv4,False))

Wconv5=weight_variable([3,3,128,128])
Bconv5=bias_variable([128])
conv5=tf.nn.conv2d(conv4_bn,Wconv5,strides=[1,1,1,1],padding='SAME')+Bconv5
conv5_bn=tf.nn.max_pool(tf.nn.relu(batch_norm(conv5,False)),ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')


Wconv6=weight_variable([3,3,128,256])
Bconv6=bias_variable([256])
conv6=tf.nn.conv2d(conv5_bn,Wconv6,strides=[1,1,1,1],padding='SAME')+Bconv6
conv6_bn=tf.nn.relu(batch_norm(conv6,False))

Wconv7=weight_variable([3,3,256,256])
Bconv7=bias_variable([256])
conv7=tf.nn.conv2d(conv6_bn,Wconv7,strides=[1,1,1,1],padding='SAME')+Bconv7
conv7_bn=tf.nn.max_pool(tf.nn.relu(batch_norm(conv7,False)),ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')

Wconv8=weight_variable([3,3,256,512])
Bconv8=bias_variable([512])
conv8=tf.nn.conv2d(conv7_bn,Wconv8,strides=[1,1,1,1],padding='SAME')+Bconv8
conv8_bn=tf.nn.relu(batch_norm(conv8,False))

Wconv9=weight_variable([3,3,512,512])
Bconv9=bias_variable([512])
conv9=tf.nn.conv2d(conv8_bn,Wconv9,strides=[1,1,1,1],padding='SAME')+Bconv9
conv9_bn=tf.nn.max_pool(tf.nn.relu(batch_norm(conv9,False)),ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')


Wconv10=weight_variable([3,3,512,512])
Bconv10=bias_variable([512])
conv10=tf.nn.conv2d(conv9_bn,Wconv10,strides=[1,1,1,1],padding='SAME')+Bconv10
conv10_bn=tf.nn.relu(batch_norm(conv10,False))

Wconv11=weight_variable([3,3,512,512])
Bconv11=bias_variable([512])
conv11=tf.nn.conv2d(conv10_bn,Wconv11,strides=[1,1,1,1],padding='SAME')+Bconv11
conv11_bn=tf.nn.max_pool(tf.nn.relu(batch_norm(conv11,False)),ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')
conv11_bn_line=tf.reshape(conv11_bn,shape=[-1,30720])


Wdense17=weight_variable([30720,4096])
Bdense17=bias_variable([4096])
dense17=tf.nn.relu(tf.matmul(conv11_bn_line,Wdense17)+Bdense17)

Wdense18=weight_variable([4096,1024])
Bdense18=bias_variable([1024])
dense18=tf.nn.relu(tf.matmul(dense17,Wdense18)+Bdense18)

Wdense19=weight_variable([1024,256])
Bdense19=bias_variable([256])
dense19=tf.nn.relu(tf.matmul(dense18,Wdense19)+Bdense19)

Wdense20=weight_variable([256,8])
Bdense20=bias_variable([8])
OUT=tf.nn.softmax(tf.matmul(dense19,Wdense20)+Bdense20)

# loss=tf.reduce_mean(-tf.reduce_sum(Yp*tf.log(tf.clip_by_value(OUT,1e-10,1.0)),reduction_indices=[1]))
# TrainStep=tf.train.AdamOptimizer(0.0001).minimize(loss)
# correct_prediction = tf.equal(tf.argmax(OUT,1), tf.argmax(Yp,1))
# accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))


sess=tf.Session()
init=tf.initialize_all_variables()
sess.run(init)
saver = tf.train.Saver()
saver.restore(sess,'session_class8_self/session1.ckpt')

Test_out=[]
for i in range(40):
    print(i)
    Test_out.append(sess.run(OUT,feed_dict={Xp:DATA_ALL[i*25:(i+1)*25,:,:,:],Yp:np.zeros([25,8])}))

Test_out=np.array(Test_out)
Test_out=np.reshape(Test_out,[1000,8])

print(Test_out.shape)
# for i in range(1000):
#     print(i)

for i in range(1000):
    for j in range(8):
        if Test_out[i,j]>0.79:
            Test_out[i,j]=0.79
        if Test_out[i,j]<0.03:
            Test_out[i,j]=0.03
np.savetxt('testout.csv', Test_out, fmt='%s', delimiter=',')


