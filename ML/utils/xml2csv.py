import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--folder',
										'-f',
										help='Folder input path containing images that will be augmented. Make sure the folder has both a test and train path',
										required=True,
										type=str
										)

parser.add_argument('--dest',
										'-d',
										help='Folder destination for augmented image. (default: [folder input path])',
										type=str,
										default=None
										)

parser.add_argument('--pixel',
										'-p',
										help='Convert to pixel format. (default: decimal format)',
										action='store_true',
										default=None
										)	

args = parser.parse_args()

if not args.dest:
	args.dest = args.folder

imageIds = {}

def convert_to_decimal(size, value):
	if args.pixel: return value
	# return float("%.2f" % round((value/size), 2))
	return float(value/size)
	
def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            width = int(root.find('size')[0].text)
            height = int(root.find('size')[1].text)

            imageid = root.find('filename').text
            source = 'labelimg'
            labelname = '/m/06nrc'
            confidence = 1
            xmin = convert_to_decimal(width, int(member[4][0].text))
            xmax = convert_to_decimal(width, int(member[4][2].text))
            ymin = convert_to_decimal(height, int(member[4][1].text))
            ymax = convert_to_decimal(height, int(member[4][3].text))
            isoccluded = 0
            istruncated = int(member[2].text)
            isgroupof = 0
            isdepiction = 0
            isinside = 0
            id = labelname
            classname = member[0].text

            if labelname not in imageIds:
              imageIds[labelname] = classname

            value = (imageid, source, labelname, confidence, xmin, xmax, ymin, ymax, isoccluded, istruncated, isgroupof, isdepiction, isinside, id, classname)
            xml_list.append(value)
    column_name = [
			'ImageID',	'Source',	'LabelName',	'Confidence',	'XMin',	'XMax',	'YMin',	'YMax',	'IsOccluded',	'IsTruncated',	'IsGroupOf',	'IsDepiction',	'IsInside',	'id',	'ClassName'
		]
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def main():
	'''
    for directory in ['train','testing']:
        image_path = os.path.join(os.getcwd(), 'images/{}'.format(directory).format(directory))
        xml_df = xml_to_csv(image_path)
        xml_df.to_csv('data/{}_labels.csv'.format(directory), index=None)
        print('Successfully converted xml to csv.')
	''' 
	# Train Annotations
	image_path = os.path.join(os.getcwd(), f"{args.folder}/train")
	xml_df = xml_to_csv(image_path)
	xml_df.to_csv(f"{args.dest}/sub-train-annotations-bbox.csv", index=None)

	# Test Annotations
	image_path = os.path.join(os.getcwd(), f"{args.folder}/test")
	xml_df = xml_to_csv(image_path)
	xml_df.to_csv(f"{args.dest}/sub-test-annotations-bbox.csv",index=None)

	# Class Descriptions
	class_description_column_name = [
			'classid',	'classname'
	]
	
	# class_description_column_name = []
	class_description_xml_list = []
	for key in imageIds:
		# class_description_column_name = [key, imageIds[key]]
		class_description_xml_list.append((key, imageIds[key]))
    
	class_description_xml_df = pd.DataFrame(class_description_xml_list, columns=class_description_column_name)
	class_description_xml_df.to_csv(f"{args.dest}/class-descriptions-boxable.csv",index=None)
main()