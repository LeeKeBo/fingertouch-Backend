import cv2
import os
import numpy as np


# 透视变换，点映射
def point_perspective(M, point):
    x = (M[0][0] * point[0] + M[0][1] * point[1] + M[0][2]) / (M[2][0] * point[0] + M[2][1] * point[1] + M[2][2])
    y = (M[1][0] * point[0] + M[1][1] * point[1] + M[1][2]) / (M[2][0] * point[0] + M[2][1] * point[1] + M[2][2])
    return [x, y]


# 预处理并找到书本轮廓
def find_contours(image, ):
    """
    :param image:
    :return: 预处理后的图，轮廓
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('gray', gray)
    # cv2.waitKey(0)

    # h, w = gray.shape[:2]
    # m = np.reshape(gray, [1, w * h])
    # mean = m.sum() / (w * h)
    # # print("mean:", mean)
    # ret, binary = cv2.threshold(gray, mean, 255, cv2.THRESH_BINARY)
    # binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 9, 4)

    ret, binary = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)  # 有黑布
    binary = cv2.bitwise_not(binary)
    # cv2.imshow('binary', binary)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
    dil = cv2.dilate(binary, kernel, iterations=2)
    # cv2.imshow('dilate', dil)

    ero = cv2.erode(dil, kernel, iterations=2)
    # cv2.imshow('erode', ero)

    binary = cv2.bitwise_not(ero)
    # cv2.imshow('binary', binary)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(9, 5))
    dil = cv2.dilate(binary, kernel, iterations=1)
    # cv2.imshow('dilate', dil)

    ero = cv2.erode(dil, kernel, iterations=1)
    # cv2.imshow('erode', ero)

    contours, heriachy = cv2.findContours(ero, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # draw_img = cv2.drawContours(image.copy(), contours, -1, (0, 0, 255), 1)
    # cv2.imshow('draw', draw_img)
    # cv2.waitKey(0)
    c = sorted(contours, key=cv2.contourArea, reverse=True)[0]

    # rect = cv2.minAreaRect(c)
    # W, H = rect[1][0:2]
    # box = np.int0(cv2.boxPoints(rect))
    # draw_img = cv2.drawContours(img.copy(), [box], -1, (0, 0, 255), 3)
    # # cv2.imshow('draw', draw_img)
    # cv2.waitKey(0)

    return ero, c


# 按线段长度排序
def len_line(elem):
    x1, y1, x2, y2 = elem[0]
    return (y1-y2)*(y1-y2)+(x1-x2)*(x1-x2)


# 书本左右直线方程
def find_l_r(b_image, ):
    """
    :param b_image:
    :return:
    """
    edge_can = cv2.Canny(b_image, 50, 150)
    # cv2.imshow('edge_can', edge_can)
    r, c = b_image.shape[:2]
    # 检测书边缘的直线
    lines = cv2.HoughLinesP(edge_can, 1, np.pi / 180, r//10, minLineLength=r//8, maxLineGap=r//50)
    if lines is None:
        return
    # print(len(lines))
    # 创建一个新图像，标注直线
    # line_img = np.ones(img.shape, dtype=np.uint8)
    # line_img = line_img * 255
    # 筛选直线
    lines = sorted(lines, key=len_line, reverse=True)
    real_line = []
    flag = 0  # 记录线在左还是右
    for line in lines:
        # 获取线段两端端点
        x1, y1, x2, y2 = line[0]
        # 只要两条线
        if len(real_line) == 2:
            break
        # 要求两线在左右
        elif len(real_line) == 1:
            if flag*(x1-c//2) > 0:
                continue
        # 计算斜率
        if x2 - x1 == 0:
            continue
        else:
            theta = (y2 - y1) / (x2 - x1)
        # 只要竖不要横
        if abs(theta) < 1:
            continue
        else:
            # print(theta)
            # cv2.line(line_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # 拟合直线
            x = [x1, x2]
            y = [y1, y2]
            poly = np.poly1d(np.polyfit(x, y, deg=1))
            # x = [y1, y2]
            # y = [x1, x2]
            # poly = np.poly1d(np.polyfit(x, y, deg=1))  # 方便根据y计算x值
            flag = x1 - c//2
            real_line.append(poly)
    # cv2.imshow("line_img", line_img)
    # cv2.waitKey(0)
    return real_line


# 书本4角坐标,
def find_4point_0(counter, l_r_fx, image, b=3.5):
    """
    # counter上偏离左右直线的点即为书角
    :param l_r_fx:
    :param b: 允许的偏离值,不整数，避免b-bias=0情况
    :param counter:
    :return:
    """
    point_4 = []
    r, c = image.shape[:2]
    # c1x + c2 - y = 0, 即 a = c1, b=-1
    c_1 = (l_r_fx[0].c[0] * l_r_fx[0].c[0] + 1) ** 0.5
    c_2 = (l_r_fx[1].c[0] * l_r_fx[1].c[0] + 1) ** 0.5
    # 上个点是近还是远
    flag_near = 0.5
    for i in range(len(counter)):
        # 判断哪条线近,计算点到直线的距离而不是直接用y值的差
        point = counter[i]
        y_1 = int(l_r_fx[0](point[0][0]))
        bias1 = int(abs(y_1 - point[0][1]) / c_1)
        y_2 = int(l_r_fx[1](point[0][0]))
        bias2 = int(abs(y_2 - point[0][1]) / c_2)
        if bias1 <= bias2:
            bias = bias1
            y = y_1
        else:
            bias = bias2
            y = y_2
        if y < 0:
            y = 0
        elif y >= r:
            y = r-1
        # 筛选
        if i == 0:
            flag_near = b-bias
            continue
        if flag_near*(b-bias) < 0:
            # point_4.append([point[0][0], y])  # 这里选直线上的点而不是轮廓点
            point_4.append([point[0][0], point[0][1]])
        # if abs(point[0][0]-320) < 10:
        #     y = y+1
        #     print("aaaa", y)
        flag_near = b - bias
    # 筛选不要的中间点
    point_ = []
    if len(point_4) == 4:
        point_ = point_4
    elif len(point_4) > 4:
        point_4.sort(key=lambda x: x[0], reverse=False)
        point_.append(point_4[0])
        point_.append(point_4[-1])
        mid = c//2
        for i in range(1, len(point_4)):
            if point_4[i][0] < mid:
                continue
            else:
                point_.append(point_4[i])
                point_.append(point_4[i-1])
                break
    # show
    # for p in point_:
    #     cv2.circle(image, (p[0], p[1]), 1, (0, 0, 255), 1, 8, 0)
    # # for x in range(img.shape[1]):
    # #     y_1 = int(l_r_line[0](x))
    # #     if 0 < y_1 < img.shape[0]:
    # #         cv2.circle(image, (x, y_1), 1, (0, 0, 255), 1, 8, 0)
    # #     y_2 = int(l_r_line[1](x))
    # #     if 0 < y_2 < img.shape[0]:
    # #         cv2.circle(image, (x, y_2), 1, (0, 0, 255), 1, 8, 0)
    # cv2.imshow("fit_line", image)
    # cv2.waitKey(0)
    return point_


# 直接根据最高点及最低点计算4个角
def find_4point(counter, l_r_fx, image):
    """
    # 找到书本轮廓最高点以及最低点直接算4个角即可
    :param counter:
    :param l_r_fx:  根据y值计算x值的方程，即反函数
    :return:
    """
    y_min = 100000
    y_max = 0
    for point in counter:
        if point[0][1] < y_min:
            y_min = point[0][1]
        if point[0][1] > y_max:
            y_max = point[0][1]
    point_4 = [[int(l_r_fx[0](y_max)), y_max], [int(l_r_fx[0](y_min)), y_min],
               [int(l_r_fx[1](y_max)), y_max], [int(l_r_fx[1](y_min)), y_min], ]
    # show
    # for p in point_4:
    #     cv2.circle(image, (p[0], p[1]), 1, (0, 0, 255), 1, 8, 0)
    # cv2.imshow("fit_line", image)
    # cv2.waitKey(0)
    return point_4


# 透视变化
def image_perspective(image, box, bias=5,):
    """
    :param image:
    :param box:
    :param bias:
    :return:
    """
    row, col = image.shape[:2]
    box = np.float32(box)
    box2 = np.float32([[col - bias, row - bias], [0 + bias, row - bias], [0 + bias, 0 + bias], [col - bias, 0 + bias], ])
    mat = cv2.getPerspectiveTransform(box, box2)
    result_img = cv2.warpPerspective(image, mat, (col, row))
    return result_img


def perspective_processing(img_path, ):
    """
    :param img_path:
    :return:
    """
    img = cv2.imread(img_path)
    r, c = img.shape[:2]
    p_img, counter = find_contours(img)
    l_r_line = find_l_r(p_img)
    if l_r_line is None or len(l_r_line) < 2:
        print("Failed to find the left or right borderline!", img_path)
        return img
    # point_4 = find_4point(counter, l_r_line, img)
    point_4 = find_4point_0(counter, l_r_line, img)

    # 保证点无越界
    for point in point_4:
        if point[0] < 0 or point[0] >= c:
            print("Failed to find 4 corner!", img_path)
            return img
        if point[1] < 0 or point[1] >= r:
            print("Failed to find 4 corner!", img_path)
            return img
    if len(point_4) < 4:
        print("Failed to find 4 corner!", img_path)
        return img
    # 处理角的顺序分布，从右下角顺时针
    tmp_list = point_4
    tmp_list.sort(key=lambda x: x[1], reverse=True)
    if tmp_list[0][0] < tmp_list[1][0]:
        tmp = tmp_list[0]
        tmp_list[0] = tmp_list[1]
        tmp_list[1] = tmp
    if tmp_list[2][0] > tmp_list[3][0]:
        tmp = tmp_list[2]
        tmp_list[2] = tmp_list[3]
        tmp_list[3] = tmp
    box = np.int0(tmp_list)
    img_per = image_perspective(image=img, box=box, )
    # cv2.imshow("img_per", img_per)
    # cv2.waitKey(0)
    return img_per


#
def save_per(img_path, result_path):
    result_path = os.path.join(result_path, img_path.split('/')[-1])
    img_per = perspective_processing(img_path)
    cv2.imwrite(result_path, img_per)
    return result_path
