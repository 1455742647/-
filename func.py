import tensorflow as tf
def load_img(path_to_img):             #图片加载以及缩放
    max_dim = 1200               #可修改，显存，1824MB
    img = tf.io.read_file(path_to_img)
    img = tf.image.decode_image(img, channels=3)       #解码
    img = tf.image.convert_image_dtype(img, tf.float32)  #归一化

    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    long_dim = max(shape)
    scale = max_dim / long_dim

    new_shape = tf.cast(shape * scale, tf.int32)         #缩放

    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]
    return img

def gram_matrix(input_tensor):            #用到了爱因斯坦求和约束
    result = tf.linalg.einsum('bijc,bijd->bcd', input_tensor, input_tensor)
    input_shape = tf.shape(input_tensor)
    num_locations = tf.cast(input_shape[1]*input_shape[2], tf.float32)
    return result/(num_locations)

def clip_0_1(image):             #值截断，限制到0，1
    return tf.clip_by_value(image, clip_value_min=0.0, clip_value_max=1.0)

def high_pass_x_y(image):            #模糊，防止图像像素点变化尖锐，相邻像素梯度
    x_var = image[:,:,1:,:] - image[:,:,:-1,:]
    y_var = image[:,1:,:,:] - image[:,:-1,:,:]

    return x_var, y_var

def total_variation_loss(image):   #像素之间过渡 平滑
    x_deltas, y_deltas = high_pass_x_y(image)
    return tf.reduce_mean(x_deltas**2) + tf.reduce_mean(y_deltas**2)