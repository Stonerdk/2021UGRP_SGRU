import cv2
import numpy as np
import os
import math
import argparse
import natsort
from PIL import Image
from webtoon_crawler import webcrawling


def linkimg(inputdir, episodedir):
    path = os.path.join(inputdir, episodedir)
    imglist = os.listdir(path)

    # sorted with image name
    imgtype = imglist[0][-4:]
    sortedimg = [int(img[0:-4]) for img in imglist]
    sortedimg.sort()

    # entire height of new image
    entire_height = 0
    for img in sortedimg:
        _img = cv2.imread(os.path.join(path, str(img) + imgtype))
        print(os.path.join(path, str(img) + imgtype))
        height, width, _ = _img.shape
        entire_height += height

    # create new image
    newimg = np.zeros((entire_height, width, 3), np.uint8)

    # linking all crawling image
    hp = 0
    for img in sortedimg:
        _img = cv2.imread(os.path.join(path, str(img) + imgtype))
        height, width, _ = _img.shape
        try:
            newimg[hp:(hp + height), :, :] = _img[:]
        except:
            _, w, _ = newimg.shape
            _img = cv2.resize(_img, dsize=(w, height))
            newimg[hp:(hp + height), :, :] = _img[:]
        hp += height

    # cv2.imwrite("all_cut_.png", newimg)
    return newimg


def cutdetector_rough(inputimg, outputdir, episodedir, episodenum): #outputdir: roughcutdir(cuts), episodedir: elist
    if not os.path.exists('./' + outputdir):
        os.mkdir('./' + outputdir)
    if not os.path.exists('./' + outputdir + '/' + episodedir):
        os.mkdir('./' + outputdir + '/' + episodedir)

    spt, ept = 0, 0
    val = 0
    cutnum = 1
    for row in range(len(inputimg[:,0,:])):
        if (len(np.unique(inputimg[row, :, :])) != 1) & (val == 0):
            spt = row
            val = 1
        elif (len(np.unique(inputimg[row, :, :])) == 1) & (val == 1):
            ept = row
            val = 0

        if (spt != 0) and (ept != 0) and ((ept - spt - 1) > 0):
            newimg = np.zeros((ept - spt - 1, len(inputimg[0,:,:]), 3), np.uint8)
            newimg[:] = inputimg[spt:ept - 1, :, :]
            cv2.imwrite('./' + outputdir + '/' + episodedir + '/' + episodenum + '_' + str(cutnum) + '.png', newimg)
            spt, ept = 0, 0
            cutnum = cutnum + 1


def cutdetector(inputdir, outputdir, episodenum, dest_size): #inputdir: roughcutdir, outputdir: cutdir
    imglist = os.listdir('./' + inputdir)
    sortedimglist = natsort.natsorted(imglist)
    print('all file length', len(sortedimglist))

    if not os.path.exists('./' + outputdir):
        os.mkdir('./' + outputdir)

    if '.DS_Store' in sortedimglist:
        sortedimglist.remove('.DS_Store')
        print('.DS_Store erased!')

    cutnum = 1
    for k in range(len(sortedimglist)):
        try:
            print('{} image processing: {}'.format(k + 1, sortedimglist[k]))
            image = cv2.imread('./' + inputdir + '/{}'.format(sortedimglist[k]), cv2.IMREAD_UNCHANGED)
            print('./' + inputdir + '/{}'.format(sortedimglist[k]))
            if sortedimglist[k] == 'actual':
                continue
            height, width, channel = image.shape

            output = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            canny = cv2.Canny(gray, 3000, 2000, apertureSize=5, L2gradient=True)

            lines = []

            lines = cv2.HoughLines(canny, 0.8, np.pi / 180, 200, srn=100, stn=200, min_theta=0, max_theta=np.pi)


            y_list = []

            if isinstance(lines, np.ndarray):
                for i in lines:
                    rho, theta = i[0][0], i[0][1]

                    if not math.isnan(rho) and not math.isnan(theta):
                        a, b = np.cos(theta), np.sin(theta)
                        x0, y0 = a * rho, b * rho

                        scale = image.shape[0] + image.shape[1]

                        x1 = int(x0 + scale * -b)
                        y1 = int(y0 + scale * a)
                        x2 = int(x0 - scale * -b)
                        y2 = int(y0 - scale * a)

                        if y1 == y2 and 0 <= y1 <= height:
                            cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            y_list.append(y1)

            if y_list != []:
                output = output[min(y_list):max(y_list), 0:width]
                # plt.axis('off')
                # plt.imshow(output)
                # plt.show()
                try:                    
                    crop = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
                    
                    h=crop.shape[0]
                    w=crop.shape[1]
                    if h>w:
                        dst=crop[int((h - w) / 2) : int((h + w) / 2), 0 : w]
                    else:
                        dst=crop[0 : h, int((w - h) / 2) : int((h + w) / 2)]
                    scale = cv2.resize(dst,(dest_size,dest_size),interpolation=cv2.INTER_LINEAR)
                    cv2.imwrite('./' + outputdir +'/'+ episodenum + '_' + str(cutnum) +'.png',scale)
                    cutnum += 1
                except:
                    print("cv2.cvtColor error!")
                    f = open("error_list.txt", 'a')
                    f.write('./' + inputdir + '/{}'.format(imglist[k]) + "\n")
            else:
                print('no image cut')
            print()
        except:
            print('error: ', 'Process finished with exit code -1073741819 (0xC0000005)')
            continue

def cut_raw_images(crawling_dir, roughcut_dir, cut_dir):
    episodelist = os.listdir(crawling_dir)
    for elist in episodelist:
        try:
            print(elist)
            episodenum = elist[7:]
            linkedIMG = linkimg(crawling_dir, elist)
            cutdetector_rough(linkedIMG, roughcut_dir, elist, episodenum)
            cutdetector(roughcut_dir + '/' + elist, cut_dir, episodenum, 512)
        except:
            continue