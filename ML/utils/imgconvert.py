#!/usr/bin/env python

from glob import glob                                                           
import cv2
import argparse
import re

parser = argparse.ArgumentParser()

parser.add_argument('--folder',
										'-f',
										help='Folder input path containing images that will be augmented. Make sure the folder has both a test and train path',
										required=True,
										type=str
										)

args = parser.parse_args()

wrongformats = []
wrongformats = [*glob(f'{args.folder}/*.png')]
wrongformats = [*wrongformats, *glob(f'{args.folder}/*.jpeg')]
print('wrongformats: ', wrongformats)

for img_name in wrongformats:
    print('img_name: ', img_name)
    new_img_name = re.sub('png|jpeg$', 'jpg', img_name)
    img = cv2.imread(img_name)
    cv2.imwrite(new_img_name, img)