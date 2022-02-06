#!/usr/bin/env python3

import math

from PIL import Image

# VARIOUS FILTERS


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def apply_color_filter(color_image):
        image_red, image_green, image_blue = split_color_image(color_image)
        image_red_filter = filt(image_red)
        image_green_filter = filt(image_green)
        image_blue_filter = filt(image_blue)
        color_image_filter = combine_color_image(image_red_filter, image_green_filter, image_blue_filter)
        return color_image_filter
    return apply_color_filter


# HELPER FUNCTION FOR SPLITTING COLOR IMAGES INTO THREE CORRESPONDING GREYSCALE IMAGES
def split_color_image(image):
    """
    
    Parameters
    ----------
    image : dictionary
        has three keys: "width", "height", and 'pixels'. 'width' and 'height' are integers, and 'pixels' is 
        a list of tuples. Tuples contain three numbers, representing pixel values for red, green, and blue images,
        respectively.

    Returns
    -------
    a list with three dictionaries for red, green, and blue components of the image.

    """
    image_red = {'width': image['width'], 'height': image['height'], 'pixels':[]}
    image_green = {'width': image['width'], 'height': image['height'], 'pixels':[]}
    image_blue = {'width': image['width'], 'height': image['height'], 'pixels':[]}
    for i in image['pixels']:
        image_red['pixels'].append(i[0])
        image_green['pixels'].append(i[1])
        image_blue['pixels'].append(i[2])
    return image_red, image_green, image_blue

# HELPER FUNCTION FOR COMBINING THREE GREYSCALE IMAGES INTO ONE COLOR IMAGE
def combine_color_image(image_red, image_green, image_blue):
    """
    

    Parameters
    ----------
    image_red : dictionary
        has three keys: "width", "height", and 'pixels'. 'width' and 'height' are integers, and 'pixels' is 
        a list.
    image_green : dictionary
        has three keys: "width", "height", and 'pixels'. 'width' and 'height' are integers, and 'pixels' is 
        a list.
    image_blue : dictionary
        has three keys: "width", "height", and 'pixels'. 'width' and 'height' are integers, and 'pixels' is 
        a list.

    Returns
    -------
    a color image, combines three greyscale images (red, green, blue) and returns one image.

    """
    color_image = {'width': image_red['width'], 'height': image_red['height'], 'pixels': []}
    for i in range(image_red['width']*image_red['height']):
        color_image['pixels'].append((image_red['pixels'][i], image_green['pixels'][i], image_blue['pixels'][i]))
    return color_image
        
def make_blur_filter(n):
    def blur_filter(image):
        return blurred(image, n)
    return blur_filter


def make_sharpen_filter(n):
    def sharpen_filter(image):
        return sharpened(image, n)
    return sharpen_filter


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    
    output: filter function
    """
    def apply_filter_cascade(image):
        for f in filters:
            image = f(image)
        return image
    return apply_filter_cascade

# SEAM CARVING
# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    it uses five helper functions defined below. Reduces width of the image by ncols values.
    image must be color image
    """
    
    for i in range(ncols):
        image_greyscale = greyscale_image_from_color_image(image)
        image_energy = compute_energy(image_greyscale)
        image_cem = cumulative_energy_map(image_energy)
        image_seam = minimum_energy_seam(image_cem)
        image = image_without_seam(image, image_seam)
    return image


# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    
    input image must be a color image
    """
    outputPixels = []
    for pixel in image['pixels']:
        greyscalePixel = pixel[0]*0.299 + pixel[1]*0.587 + pixel[2]*0.114
        outputPixels.append(greyscalePixel)
    outputImage = {'width': image['width'], 'height': image['height'], 'pixels': outputPixels}
    outputImage = round_and_clip_image(outputImage)
    return outputImage


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    
    """
    outputImage = edges(grey)
    return outputImage


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy function),
    computes a "cumulative energy map" as described in the lab 1 writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    cumulativeEnergyMap = {'width': energy['width'], 'height': energy['height'], 'pixels': [0]*energy['height']*energy['width']}
    for x in range(energy['height']):
        for y in range(energy['width']):
            if x == 0:
                set_pixel(cumulativeEnergyMap, x, y, get_pixel(energy, x, y))
            else:
                adjacentPixels = [get_pixel(cumulativeEnergyMap, x-1, y-1), get_pixel(cumulativeEnergyMap, x-1, y), get_pixel(cumulativeEnergyMap, x-1, y+1)]
                Pixel = get_pixel(energy, x, y) + min(adjacentPixels)
                set_pixel(cumulativeEnergyMap, x, y, Pixel)
    return cumulativeEnergyMap

def minimum_energy_seam(c):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 1 writeup).
    """
    w = c['width']
    h = c['height']
    p = c['pixels']
    mes = [] #minimum energy seam
    mes.append(p.index(min(p[w*(h-1)::]), w*(h-1)))
    for i in range(h-1):
        index_lower = mes[-1]-w-1
        index_higher = mes[-1]-w+2
        if mes[-1]%w==0: #if the pixel is on the first column
            index_lower = mes[-1]-w
        elif (mes[-1]+1)%w==0: # if the pixel is on the last column
            index_higher = mes[-1]-w+1
        minimum = min(p[index_lower:index_higher])
        mes.append(p.index(minimum, index_lower, index_higher))
    return mes
                   
                   
def image_without_seam(im, s):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    NumberOfPixels = im['width']*im['height']
    NewImagePixels = []
    for i in range(NumberOfPixels):
        if i not in s:
            NewImagePixels.append(im['pixels'][i])
    NewImage = {'width': im['width']-1, 'height': im['height'], 'pixels': NewImagePixels}
    return NewImage


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()

emboss_kernel_3 = {'width':3, 'height':3, 'pixels':[
        1, 1, 0,
        1, 0, -1,
        0, -1, -1]
        }
emboss_kernel_5 = {'width':5, 'height':5, 'pixels':[
        1, 1,  1,  1, 0,
        1, 1,  1,  0, -1,
        1, 1,  0, -1, -1,
        1, 0, -1, -1, -1,
        0, -1, -1, -1, -1]
        }

def directional_emboss(image, kernel):
    """
    intput: image (in dictionary representation), kernel (in dictionary representation)
    output: image with emboss filter applied
    
    this function first splits the image into three components, and correlates each of the resulting images
    with the emboss kernel. Then, it adds pixel value of 128 to each of the pixels to turn image into greyscale.
    Finally, it rounds and clips pixels, and combines each of the colors to return the output image.
    """
    
    image_red, image_green, image_blue = split_color_image(image)
    image_red_output = correlate(image_red, kernel)
    image_green_output = correlate(image_green, kernel)
    image_blue_output = correlate(image_blue, kernel)
    pixels_red = image_red_output['pixels']
    pixels_green = image_green_output['pixels']
    pixels_blue = image_blue_output['pixels']
    for pixels in [pixels_red, pixels_green, pixels_blue]:
        for i in range(len(pixels)):
            pixels[i] = pixels[i] + 128
    image_red_output = round_and_clip_image(image_red_output)
    image_green_output = round_and_clip_image(image_green_output)
    image_blue_output= round_and_clip_image(image_blue_output)
    output = combine_color_image(image_red_output, image_green_output, image_blue_output)
    return output


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pass


#LAB0 Functions--------------------------------------------------------------------------------------
#LAB0 Functions--------------------------------------------------------------------------------------
#LAB0 Functions--------------------------------------------------------------------------------------
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
