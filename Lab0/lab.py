#!/usr/bin/env python3

import sys
import math
import base64
import tkinter

from io import BytesIO
from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y):
    if x<0:
        x = 0
    if x>=image['height']:
        x = image['height'] - 1
    if y<0:
        y = 0
    if y>=image['width']:
        y = image['width'] - 1
    return image['pixels'][int(image['width']*x + y)]


def set_pixel(image, x, y, c):
    image['pixels'][image['width']*x + y] = c


def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    kernel is represented in the same way as an image is represented: it is a
    dictionary with three keys: width, height, and pixels. pixel is a list of 
    image pixels ordered in row-major order. I wanted to choose this method of
    representation to make use of some of the functions we have already implemented for
    this dictionary representation of images.
    """
    output = {'height': image['height'], 'width': image['width'], 'pixels':image['pixels'][:]}
    for x in range(image['height']):
        for y in range(image['width']):
            newcolor = 0
            for i in range(kernel['height']):
                for j in range(kernel['width']):
                    newcolor += get_pixel(kernel, i, j)*get_pixel(image, x-(kernel['width']-1)/2+i, y-(kernel['width']-1)/2+j)
            set_pixel(output, x, y, newcolor)
    return output
#centeredPixel = load_image('test_images/centered_pixel.png')
kernel_identity = {'height':3, 'width':3, 'pixels':[0,0,0,0,1,0,0,0,0]}
kernel_translation = {'height':5, 'width':5, 'pixels': [0,0,0,0,0, 0,0,0,0,0, 1,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0]}
kernel_average = {'height':3, 'width':3, 'pixels': [0,0.2,0, 0.2,0.2,0.2, 0,0.2,0]}

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i in range(len(image['pixels'])):
        if image['pixels'][i] < 0:
            image['pixels'][i] = 0
        elif image['pixels'][i] >255:
            image['pixels'][i] = 255
        image['pixels'][i] = round(image['pixels'][i])
    return image
#kernel9_pixels = [0]*81
#kernel9_pixels[18] = 1
#kernel9 = {'height':9, 'width': 9, 'pixels': kernel9_pixels}
    

# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel_boxblur = boxblur_kernel(n)

    # then compute the correlation of the input image with that kernel
    imageBlurred = correlate(image, kernel_boxblur)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(imageBlurred)

def sharpened(i, n):
    """
    i: image
    n: size of the blur kernel
    applies sharpening to the image according to the following formula: O = 2I - Blur(n)
    """
    sharpenKernel = {'width':n, 'height':n, 'pixels':[-1/n**2]*n**2}
    sharpenKernel['pixels'][int((n**2-1)/2)] = 2+sharpenKernel['pixels'][int((n**2-1)/2)]
    sharpenedImage = correlate(i, sharpenKernel)
    return round_and_clip_image(sharpenedImage)
     
def edges(i):
    """
    i: image that is represented as a dictionary with the following keys: 'width', 'height', 'pixels'
    this function correlates the input image with Sobel operators Kx and Ky, and returns an image, where edges are
    emphasized.
    """
    Kx = {'width':3, 'height':3, 'pixels': [-1, 0, 1, -2, 0, 2, -1, 0, 1]}
    Ky = {'width':3, 'height':3, 'pixels': [-1, -2, -1, 0, 0, 0, 1, 2, 1]}
    i_Kx = correlate(i, Kx)
    i_Ky = correlate(i, Ky)
    output = {'width': i['width'], 'height': i['height'], 'pixels': i['pixels'][:]}
    for x in range(i['height']):
        for y in range(i['width']):
            newPixel = math.sqrt(get_pixel(i_Kx, x, y)**2 + get_pixel(i_Ky, x, y)**2)
            set_pixel(output, x, y, newPixel)
    output = round_and_clip_image(output)
    return output
    
# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES
    
def boxblur_kernel(n):
    return {'width':n, 'height':n, 'pixels':[1/n**2]*n**2}


def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pass
