from PIL import Image
import numpy as np
import math
import argparse


def write_data(img, data, filename):
    byte_array = bytearray()
    byte_array.extend(bytes(filename.rjust(12, '0'), 'utf-8'))
    byte_array.extend(len(data).to_bytes(4, 'little'))
    byte_array.extend(data)
    height, width, channels = img.shape
    data_size = len(byte_array)
    byte = 0
    nib = 0
    for i in range(0, height):
        for j in range(0, width):
            for c in range(0, channels):
                print([i, j, c, byte, nib])
                img[i, j, c] = (img[i, j, c] & 0xFC | ((byte_array[byte] >> nib * 2) & 0x03))
                nib += 1
                nib %= 4
                if nib == 0:
                    byte += 1
                if byte >= data_size:
                    return


def extract_data(img):
    filename_byte_array = bytearray()
    filesize_byte_array = bytearray()
    byte_array = bytearray()
    height, width, channels = img.shape
    data_size = 16
    byte = 0
    nib = 0
    byte_dat = 0
    for i in range(0, height):
        for j in range(0, width):
            for c in range(0, channels):
                print([i, j, c, byte, nib])
                byte_dat = byte_dat | (img[i, j, c] & 0x03) << nib * 2
                nib += 1
                nib %= 4
                if nib == 0:
                    if byte < 12:
                        filename_byte_array.append(byte_dat)
                    elif byte < 16:
                        filesize_byte_array.append(byte_dat)
                        if byte == 15:
                            data_size = int.from_bytes(filesize_byte_array, 'little') + 16
                    else:
                        byte_array.append(byte_dat)
                    byte_dat = 0
                    byte += 1
                if byte >= data_size:
                    return byte_array, filename_byte_array.decode()


parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="input file name",
                    type=str)
parser.add_argument("output_file", nargs='*', default='nothing', help="output file name",
                    type=str)
parser.add_argument("-d", "--decode", help="decode file",
                    action="store_true")
parser.add_argument("-e", "--encode", help="encode file",
                    action="store_true")

args = parser.parse_args()
input_filename = args.input_file
if len(input_filename) > 12:
    print("input filename cannot be longer than 12 letters")
    exit()
output_filename = args.output_file

if args.encode:

    img = Image.open("encode_image.jpg")
    img = np.array(img)
    max_bytes_size = math.floor(img.shape[0] * img.shape[1] * img.shape[2] * 2 / 8)

    with open(input_filename, mode='rb') as file:
        file_content = file.read()

    if len(file_content) > max_bytes_size - 12:
        print("File is too large be encoded.")
        exit()

    write_data(img, file_content, input_filename)
    img = Image.fromarray(img)
    # img.save(f'{output_filename}.bmp')
    filename = ''.join(output_filename)
    img.save(filename + '.bmp')

    exit()

if args.decode:
    img = Image.open(input_filename)
    img = np.array(img)
    data, filename = extract_data(img)

    with open(filename, "wb") as file:
        file.write(data)
