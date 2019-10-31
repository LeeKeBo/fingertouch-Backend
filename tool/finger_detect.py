import tensorflow as tf
from PIL import Image
import numpy as np
import os
import cv2
import time

gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)
# config = tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True)
# config = tf.compat.v1.ConfigProto(allow_soft_placement=True)
# config.gpu_options.allow_growth = True


class FingerModel:
    def __init__(self, model_path, result_folder='', bias=[0, 0, 0, 0]):
        """
        :param model_path:
        :param result_folder:
        :param bias: [top_b, bottom_b, left_b, right_b]
        """
        # 读取模型
        output_graph_def = tf.GraphDef()
        # 打开.pb模型
        with open(model_path, "rb") as f:
            output_graph_def.ParseFromString(f.read())
            tensors = tf.import_graph_def(output_graph_def, name="")
        self.__sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True))
        self.__sess.run(tf.global_variables_initializer())
        graph = tf.get_default_graph()
        self.__image_tensor = graph.get_tensor_by_name("image_tensor:0")
        self.__detection_boxes = graph.get_tensor_by_name("detection_boxes:0")
        self.__detection_scores = graph.get_tensor_by_name("detection_scores:0")
        self.__detection_classes = graph.get_tensor_by_name("detection_classes:0")
        self.__num_detections = graph.get_tensor_by_name("num_detections:0")
        self.result_folder = result_folder
        # 截取子图时，离底部边的上偏差和下偏差
        self.top_b = bias[0]
        self.bottom_b = bias[1]
        self.left_b = bias[2]
        self.right_b = bias[3]

    def load_image_into_numpy_array(self, image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape(
            (im_height, im_width, 3)).astype(np.uint8)

    def set_bias(self, bias):
        self.top_b = bias[0]
        self.bottom_b = bias[1]
        self.left_b = bias[2]
        self.right_b = bias[3]

    # 截取出指尖附近的图像框
    def get_patch(self, finger, image_path):
        """
        :param finger: [[xmin, ymin], [xmax, ymax]]
        :param image_path:
        :return:
        """
        xmin = finger[0][0]
        xmax = finger[1][0]
        ymax = finger[1][1]
        img = cv2.imread(image_path)
        # 防止越界处理
        y1 = ymax - self.top_b if (ymax - self.top_b) > 0 else 0
        y2 = ymax + self.bottom_b if (ymax + self.bottom_b) < img.shape[0] else img.shape[0]
        x1 = xmin - self.left_b if (xmin - self.left_b) > 0 else 0
        x2 = xmax + self.right_b if (xmax + self.right_b) < img.shape[1] else img.shape[1]
        img_patch = img[y1:y2, x1:x2]  # x,y为常见坐标轴, 截取的行对应y, 截取的列对应x
        img_patch = cv2.resize(img_patch, (0, 0), fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
        return img_patch

    # 保存推断的结果到图片上
    def save_inference(self, img_path, output):
        img = cv2.imread(img_path)
        for finger in output["finger"]:
            cv2.rectangle(img, finger[0], finger[1], (0, 0, 255), 1, 8, 0)
        for corner in output["corner"]:
            cv2.circle(img, corner, 2, (0, 255, 0), 1, 8, 0)
        cv2.imwrite(img_path, img)

    def inference(self, img_path, bias=None, SAVE=False):
        if bias is not None:
            self.set_bias(bias)
        # 输入的图片数据
        image = Image.open(img_path)
        width, height = image.size
        image_np = self.load_image_into_numpy_array(image)
        image_np_expanded = np.expand_dims(image_np, axis=0)
        # 推理
        (boxes, scores, classes, num) = self.__sess.run(
            [self.__detection_boxes, self.__detection_scores, self.__detection_classes, self.__num_detections],
            feed_dict={self.__image_tensor: image_np_expanded})
        s_boxes = boxes[scores > 0.5]
        s_classes = classes[scores > 0.5]
        s_scores = scores[scores > 0.5]
        # 结果分析
        output = {'corner': [], 'finger': []}
        if len(s_classes) == 0:
            return output
        for i in range(len(s_classes)):
            # print('s_class:', s_classes[i])
            y_1 = s_boxes[i][0] * height
            x_1 = s_boxes[i][1] * width
            y_2 = s_boxes[i][2] * height
            x_2 = s_boxes[i][3] * width
            # 分个大小才知道对应位置
            if y_1 > y_2:
                ymax = int(round(y_1))
                ymin = int(round(y_2))
            else:
                ymax = int(round(y_2))
                ymin = int(round(y_1))
            if x_1 > x_2:
                xmax = int(round(x_1))
                xmin = int(round(x_2))
            else:
                xmax = int(round(x_2))
                xmin = int(round(x_1))
            if s_classes[i] == 1.0:
                output['finger'].append(((xmin, ymin), (xmax, ymax)))
            elif s_classes[i] == 2.0:
                y = (y_1 + y_2) / 2
                x = (x_1 + x_2) / 2
                output['corner'].append((x, y))
        if SAVE:
            self.save_inference(img_path=img_path, output=output)
        return output


if __name__ == '__main__':
    pass
