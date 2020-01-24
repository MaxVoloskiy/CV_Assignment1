import argparse
import cv2


def remove_borders(img_path, output_path):

    image = cv2.imread(img_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, image_thr = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, h = cv2.findContours(image_thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    x1c = image.shape[1]
    y1c = image.shape[0]
    x2c = 0
    y2c = 0
    for с in contours:
        x1, y1, w, h = cv2.boundingRect(с)
        x2 = x1 + w
        y2 = y1 + h
        if x1 < x1c:
            x1c = x1
        if y1 < y1c:
            y1c = y1
        if x2 > x2c:
            x2c = x2
        if y2 > y2c:
            y2c = y2
    image = image[y1c:y2c, x1c:x2c]
    cv2.imwrite(output_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='input', default='images/1.png')
    parser.add_argument('-o', dest='output', default='output/1.png')
    args = parser.parse_args()
    remove_borders(args.input, args.output)
