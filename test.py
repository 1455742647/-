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

epochs=10
style_photo=31


path = r"C:\Users\Administrator\Desktop\style_trans-master\wechat\photo"  # 待读取的文件夹
path_list = os.listdir(path)
path_list.sort(reverse=True)  # 对读取的路径进行排序
soure_file = ""
for filename in path_list:
    soure_file = os.path.join(path, filename)
    break
print(soure_file)

mpl.rcParams['figure.figsize'] = (12, 12)  # 视图大小
mpl.rcParams['axes.grid'] = False  # 网格显示


content_path = soure_file
file = "/" + str(style_photo) + ".jpg"
print(file)
style_path = 'C:/Users/Administrator/Desktop/style_trans-master/风格迁移图片' + file
print(style_path)

content_image = func.load_img(content_path)  # 读取图片
style_image = func.load_img(style_path)

# #ResNet152模型
# content_layers = ['conv4_block5_2_conv']  # 内容层  层次高的卷积
# style_layers = ['conv2_block2_1_conv',  # 多层卷积，低阶
#                  'conv2_block1_2_conv',]


content_layers = ['block5_conv1']  # 内容层  层次高的卷积
style_layers = ['block1_conv1',  # 多层卷积，低阶
                'block2_conv1',
                'block3_conv1',
                'block4_conv1',
                'block5_conv1']
print(style_layers)
num_content_layers = len(content_layers)  # 求层数（风格层以及内容层）
num_style_layers = len(style_layers)

extractor = model.StyleContentModel(style_layers, content_layers)  #

style_targets = extractor(style_image)['style']
content_targets = extractor(content_image)['content']


def style_content_loss(outputs):  # 损失函数
    style_outputs = outputs['style']  # 用来表示style信息的网络层的输出，这里已经计算过Gram矩阵了
    content_outputs = outputs['content']  # 用来表示content信息的网络层的输出，内容信息不需要计算Gram
    style_loss = tf.add_n([tf.reduce_mean((style_outputs[name] - style_targets[name]) ** 2)
                           for name in style_outputs.keys()])

    style_loss *= style_weight / num_style_layers

    content_loss = tf.add_n([tf.reduce_mean((content_outputs[name] - content_targets[name]) ** 2)
                             for name in content_outputs.keys()])
    content_loss *= content_weight / num_content_layers
    loss = style_loss + content_loss
    return loss


opt = tf.optimizers.Adam(learning_rate=0.02, beta_1=0.99, epsilon=1e-1)
image = tf.Variable(content_image + tf.random.truncated_normal(content_image.shape, mean=0.0, stddev=0.08),
                    trainable=True)


@tf.function()
def train_step(image):
    with tf.GradientTape() as tape:
        outputs = extractor(image)
        loss = style_content_loss(outputs)
        loss += total_variation_weight * func.total_variation_loss(image)

    grad = tape.gradient(loss, image)
    opt.apply_gradients([(grad, image)])
    image.assign(func.clip_0_1(image))

for n in trange (epochs * steps_per_epoch):         #开始训练，参数为训练的轮数。
    train_step(image)



plt.imshow(image.read_value()[0])
plt.show()
print(image.read_value()[0].shape)
Eimg = tf.image.convert_image_dtype(image.read_value()[0], tf.uint8)
Eimg = tf.image.encode_jpeg(Eimg)
number = str(random.randint(1,99999999))
tf.io.write_file('C:/Users/Administrator/Desktop/style_trans-master/wechat/result/' + number + "style_photo="+str(style_photo)+'.jpg', Eimg)