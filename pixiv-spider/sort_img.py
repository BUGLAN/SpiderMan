import os

path = './images'


def sort():
    files = os.listdir(path)
    pics = []
    for f in files:
        if os.path.getsize(os.path.join(path, f)) > 1024 * 1024:
            pics.append(os.path.join(path, f))
    return pics


def move_pics(pics: list):
    for pic in pics:
        os.rename(pic, os.path.join(
            '/home/lan/wrappers', os.path.basename(pic)))
    print('all done')


if __name__ == '__main__':
    pics = sort()
    move_pics(pics)
