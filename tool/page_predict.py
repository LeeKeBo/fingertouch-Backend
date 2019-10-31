# coding: utf-8
import tensorflow as tf
import cv2
import numpy as np


class PageModel:
    def __init__(self, model_path, resize_height=224, resize_weight=224, depths=3):
        # 读取模型
        output_graph_def = tf.GraphDef()
        # 打开.pb模型
        with open(model_path, "rb") as f:
            output_graph_def.ParseFromString(f.read())
            tensors = tf.import_graph_def(output_graph_def, name="")
        self.__sess = tf.Session()
        self.__sess.run(tf.global_variables_initializer())
        graph = tf.get_default_graph()
        self.__image_tensor = graph.get_tensor_by_name("input:0")
        self.__keep_prob = graph.get_tensor_by_name("keep_prob:0")
        self.__is_training = graph.get_tensor_by_name("is_training:0")
        self.__output = graph.get_tensor_by_name("MobilenetV1/Logits/SpatialSqueeze:0")
        # 将输出结果进行softmax分布,再求最大概率所属类别
        self.__score = tf.nn.softmax(self.__output, name='pre')
        self.__class_id = tf.argmax(self.__score, 1)
        # 模型的输入规格
        self.__resize_height = resize_height  # 指定存储图片高度
        self.__resize_width = resize_weight  # 指定存储图片宽度
        self.__depths = depths

    def read_image(self, image_path, normalization=True, gau=False):
        """
        读取图片数据,默认返回的是uint8,[0,255]
        :param gau:
        :param image_path:  image file path
        :param resize_height: 0即为not resize
        :param resize_width:
        :param normalization:是否归一化到[0.,1.0]
        :return: 返回的图片数据
        """
        bgr_image = cv2.imread(image_path)
        if len(bgr_image.shape) == 2:  # 若是灰度图则转为三通道
            print("Warning:gray image", image_path)
            bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_GRAY2BGR)
        if gau:
            bgr_image = cv2.GaussianBlur(bgr_image, (3, 3), 0)

        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)  # 将BGR转为RGB
        # show_image(image_path,rgb_image)
        # rgb_image=Image.open(image_path)
        if self.__resize_height > 0 and self.__resize_width > 0:
            rgb_image = cv2.resize(rgb_image, (self.__resize_width, self.__resize_height))
        rgb_image = np.asanyarray(rgb_image)
        if normalization:
            # 不能写成:rgb_image=rgb_image/255
            rgb_image = rgb_image / 255.0
        # show_image("src resize image",image)
        return rgb_image

    def inference(self, file_path):
        # 输入的图片数据
        image = self.read_image(file_path)
        image = image[np.newaxis, :]
        pre_score, pre_label = self.__sess.run([self.__score, self.__class_id], feed_dict={self.__image_tensor: image,
                                                                                           self.__keep_prob: 1.0,
                                                                                           self.__is_training: False})
        return pre_score, pre_label


if __name__ == '__main__':
    pass
