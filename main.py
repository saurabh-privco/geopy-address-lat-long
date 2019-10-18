import re
import os
import pdb
import sys
import time
import boto3
import xlsxwriter
from argparse import ArgumentParser
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from utilities import Logger


logger = Logger()
s3 = boto3.client('s3')

def read_input(input_path, type):

    """ Read the input file """

    if type == 'csv':
        data = pd.read_csv(os.path.join(input_path)).fillna('')
        return data
    if type == 'xlsx':
        data = pd.ExcelFile(os.path.join(input_path))
        print(data.sheet_names[0])
        df = data.parse(str(data.sheet_names[0]))
        return df

def s3_upload(output, s3, bucket, folder):

    """ Upload the data to s3 bucket """

    try:
	    for i in range(0, len(output)):
		    s3.put_object(
					    Bucket = bucket,
					    Body = str(output[i][1]).encode('utf-8'),
					    Key = '{}/{}/{}.txt'.format(folder, output[0][1], output[i][0]))

    except Exception as error:
	    logger.error('error {} while uploading for id {}'.format(error, id))


def _run():

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='path to the input file')
    parser.add_argument('-o', '--output', required=True,
                        help='path to the aws bucket to upload results in the format of bucket-name/folder-name')
    args = parser.parse_args()
    input_path = args.input
    output_path = args.output

    if len(output_path.split('/')) >= 2:
        bucket = output_path.split('/')[0]
        folder = '/'.join(output_path.split('/')[1:])
    else:
        print('Output aws bucket name not supported')
        sys.exit(0)

    column_names = ['id', 'address', 'city', 'state']
    user_input = input('Does the input file contains all the exact column names (Y/N)?\n' + \
                        str(column_names) + '\n')

    if user_input.lower() == 'y':
        type = input_path.split('/')[-1].split('\\')[-1].split('.')[1]
        if type not in ['xlsx', 'csv']:
            print('Input file format not supported. Please upload a xlsx or csv file')
            sys.exit(0)
        data = read_input(input_path, type)
        data.fillna('', inplace=True)
        geolocator = Nominatim()

        for row in data.itertuples():
            output = []
            try:
                url = row.headquarters_addr1 + ' ' + row.headquarters_city + ' ' + row.headquarters_state_code
                location = geolocator.geocode(url)
                time.sleep(2)
            except Exception as error:
                if 'time out' in str(error):
                    time.sleep(30)
                    location = geolocator.geocode(url)

            if location:
                if location.address:
                    try:
                        output.append(('id', row.id))
                        output.append(('address', location.address))
                        output.append(('latitute', location.latitude))
                        output.append(('longitude', location.longitude))
                        s3_upload(output, s3, bucket, folder)
                    except Exception:
                        logger.error(error)
                        pass
            else:
                logger.error('No location info for id {}'.format(row.id))

if __name__  == '__main__':
    sys.exit(_run())