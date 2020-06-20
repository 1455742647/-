import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib as mpl
from tqdm import trange
import numpy as np
import time
import func
import model
from config import *
import os
import random

# 1.保存文件
# 2.读取文件
# 3.风格迁移
# 4.发送图片
def begin_style_trans(epochs,choose):
    path=r"C:\Users\Administrator\Desktop\style_trans-master\wechat\photo"  #待读取的文件夹，读取内容图片
    path_list=os.listdir(path)
    path_list.sort(reverse=True) #对读取的路径进行排序
    soure_file = ""
    for filename in path_list:
        soure_file = os.path.join(path, filename)
        break
    content_path = soure_file
    file="/"+str(choose)+".jpg"
    style_path = 'C:/Users/Administrator/Desktop/style_trans-master/风格迁移图片'+file


    mpl.rcParams['figure.figsize'] = (12, 12)    #视图大小
    mpl.rcParams['axes.grid'] = False           #网格显示


    print(file)
    print(style_path)

    content_image = func.load_img(content_path)        #读取图片
    style_image = func.load_img(style_path)

    content_layers = ['block5_conv1']           #内容层  层次高的卷积
    style_layers = ['block1_conv1',          #多层卷积，低阶
                    'block2_conv1',
                    'block3_conv1',
                    'block4_conv1',
                    'block5_conv1']

    num_content_layers = len(content_layers)      #求层数（风格层以及内容层）
    num_style_layers = len(style_layers)

    extractor = model.StyleContentModel(style_layers, content_layers)         #

    style_targets = extractor(style_image)['style']
    content_targets = extractor(content_image)['content']

    def style_content_loss(outputs):    #损失函数
        style_outputs = outputs['style'] # 用来表示style信息的网络层的输出，这里已经计算过Gram矩阵了
        content_outputs = outputs['content'] # 用来表示content信息的网络层的输出，内容信息不需要计算Gram
        style_loss = tf.add_n([tf.reduce_mean((style_outputs[name]-style_targets[name])**2)
                               for name in style_outputs.keys()])

        style_loss *= style_weight / num_style_layers  #均方误差，利用多层的风格损失，多层的风格损失是单层风格损失的加权累加，防止风格损失的数量级相比内容损失过大。

        content_loss = tf.add_n([tf.reduce_mean((content_outputs[name]-content_targets[name])**2)
                                 for name in content_outputs.keys()])
        content_loss *= content_weight / num_content_layers
        loss = style_loss + content_loss
        return loss

    opt = tf.optimizers.Adam(learning_rate=0.02, beta_1=0.99, epsilon=1e-1)
    image = tf.Variable(content_image + tf.random.truncated_normal(content_image.shape, mean=0.0, stddev=0.08), trainable=True)

    @tf.function()
    def train_step(image):#优化函数
        with tf.GradientTape() as tape:
            outputs = extractor(image)
            loss = style_content_loss(outputs)
            loss += total_variation_weight * func.total_variation_loss(image)

        grad = tape.gradient(loss, image)
        opt.apply_gradients([(grad, image)])
        image.assign(func.clip_0_1(image)) #最后进行一次0,1截断



    for n in trange (epochs * steps_per_epoch):         #开始训练，参数为训练的轮数。
        train_step(image)



    plt.imshow(image.read_value()[0])
    print (image.read_value()[0].shape)
    Eimg = tf.image.convert_image_dtype (image.read_value()[0], tf.uint8)
    Eimg = tf.image.encode_jpeg (Eimg)
    number=str(random.randint(1,99999999))
    tf.io.write_file ('C:/Users/Administrator/Desktop/style_trans-master/wechat/result/'+number+'.jpg', Eimg)
    return number