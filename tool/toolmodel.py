from . import FingerModel
from . import PageModel
from . import save_per
import time
import cv2


class ToolModel:
    def __init__(self, config):
        self.result_folder = config["RESULT_DIR"]
        self.finger_model = FingerModel(model_path=config["FINGER_MODEL"], )
        self.page_model = PageModel(model_path=config["PAGE_MODEL"])
        self.page = config["Label2Page"]

    def run(self, img_path, ):
        """
        :return:
        """
        # 图片预处理
        start = time.time()
        per_path = save_per(img_path, self.result_folder)
        end = time.time()-start
        print("img processing execute time:", end)
        # 手指位置识别
        start = time.time()
        out_put = self.finger_model.inference(per_path, SAVE=True)
        end = time.time() - start
        print("finger execute time:", end)
        # 图片页码识别
        start = time.time()
        pre_score, pre_label = self.page_model.inference(per_path)
        pre_label = list(pre_label)[0]
        pre_page = self.page[pre_label]
        end = time.time() - start
        print("page execute time:", end)
        # 所属具体区域划分

        # out_put: {'Finger':[手指坐标,...], 'corner':[], }
        if len(out_put['finger']) == 0:
            return None, pre_page
        else:
            return out_put['finger'][0], pre_page


if __name__ == '__main__':
    start = time.time()
    img = cv2.imread("/home/wen/py_project/ImageProcessing/img/222290.jpg")
    cv2.imwrite("/home/wen/py_project/ImageProcessing/img/tmp.jpg", img)
    end = time.time() - start
    print(end)  # 0.0046
