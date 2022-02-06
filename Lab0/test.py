#!/usr/bin/env python3

import os
import lab
import pickle
import hashlib
import unittest

TEST_DIRECTORY = os.path.dirname(__file__)


def object_hash(x):
    return hashlib.sha512(pickle.dumps(x)).hexdigest()


class Lab0Test(unittest.TestCase):
    def compare_images(self, im1, im2):
        self.assertTrue(set(im1.keys()) == {'height', 'width', 'pixels'}, 'Incorrect keys in dictionary')
        self.assertEqual(im1['height'], im2['height'], 'Heights must match')
        self.assertEqual(im1['width'], im2['width'], 'Widths must match')
        self.assertEqual(len(im1['pixels']), im1['height']*im1['width'], 'Incorrect number of pixels')
        self.assertTrue(all(isinstance(i, int) for i in im1['pixels']), 'Pixels must all be integers')
        self.assertTrue(all(0<=i<=255 for i in im1['pixels']), 'Pixels must all be in the range from [0, 255]')
        pix_incorrect = (None, None)
        for ix, (i, j) in enumerate(zip(im1['pixels'], im2['pixels'])):
            if i != j:
                pix_incorrect = (ix, abs(i-j))
        self.assertTrue(pix_incorrect == (None, None), 'Pixels must match.  Incorrect value at location %s (differs from expected by %s)' % pix_incorrect)


class TestImage(Lab0Test):
    def test_load(self):
        result = lab.load_image('test_images/centered_pixel.png')
        expected = {
            'height': 11,
            'width': 11,
            'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
        self.compare_images(result, expected)


class TestInverted(Lab0Test):
    def test_inverted_1(self):
        im = lab.load_image('test_images/centered_pixel.png')
        result = lab.inverted(im)
        expected = {
            'height': 11,
            'width': 11,
            'pixels': [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 0, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
        }
        self.compare_images(result, expected)

    def test_inverted_2(self):
        # REPLACE THIS with your test case from section 3.1
        result = lab.inverted({'width': 4, 'height': 1, 'pixels': [9, 88, 153, 224]})
        expected = {'width': 4, 'height': 1, 'pixels': [246, 167, 102, 31]}
        self.compare_images(result, expected)
        #self.assertTrue(False)

    def test_inverted_images(self):
        for fname in ('mushroom', 'twocats', 'chess'):
            with self.subTest(f=fname):
                inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_invert.png' % fname)
                im = lab.load_image(inpfile)
                oim = object_hash(im)
                result = lab.inverted(im)
                expected = lab.load_image(expfile)
                self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')
                self.compare_images(result, expected)


class TestFilters(Lab0Test):
    def test_blurred(self):
        for kernsize in (1, 3, 7):
            for fname in ('mushroom', 'twocats', 'chess'):
                with self.subTest(k=kernsize, f=fname):
                    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_blur_%02d.png' % (fname, kernsize))
                    input_img = lab.load_image(inpfile)
                    input_hash = object_hash(input_img)
                    result = lab.blurred(input_img, kernsize)
                    expected = lab.load_image(expfile)
                    self.assertEqual(object_hash(input_img), input_hash, "Be careful not to modify the original image!")
                    self.compare_images(result, expected)

    def test_blurred_black_image(self):
        # REPLACE THIS with your 1st test case from section 5.1
        blackImage = {'height':6, 'width':5, 'pixels': [0]*30}
        for n in [5, 9]:
            blurredImage = lab.blurred(blackImage, n)
            self.compare_images(blackImage, blurredImage)
        #self.assertTrue(False)

    def test_blurred_centered_pixel(self):
        # REPLACE THIS with your 2nd test case from section 5.1
        centeredPixel = lab.load_image('test_images/centered_pixel.png')
        blurredImage1 = lab.blurred(centeredPixel, 1)
        blurredImage3 = lab.blurred(centeredPixel, 3)
        #calculating expected image
        expectedImage1 = {
            'height': 11,
            'width': 11,
            'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
        expectedImage3 = {
            'height': 11,
            'width': 11,
            'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 28, 28, 28, 0, 0, 0, 0,
                       0, 0, 0, 0, 28, 28, 28, 0, 0, 0, 0,
                       0, 0, 0, 0, 28, 28, 28, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
        self.compare_images(expectedImage1, blurredImage1)
        self.compare_images(expectedImage3, blurredImage3)
        #self.assertTrue(False)

    def test_sharpened(self):
        for kernsize in (1, 3, 9):
            for fname in ('mushroom', 'twocats', 'chess'):
                with self.subTest(k=kernsize, f=fname):
                    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_sharp_%02d.png' % (fname, kernsize))
                    input_img = lab.load_image(inpfile)
                    input_hash = object_hash(input_img)
                    result = lab.sharpened(input_img, kernsize)
                    expected = lab.load_image(expfile)
                    self.assertEqual(object_hash(input_img), input_hash, "Be careful not to modify the original image!")
                    self.compare_images(result, expected)

    def test_edges(self):
        for fname in ('mushroom', 'twocats', 'chess'):
            with self.subTest(f=fname):
                inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_edges.png' % fname)
                input_img = lab.load_image(inpfile)
                input_hash = object_hash(input_img)
                result = lab.edges(input_img)
                expected = lab.load_image(expfile)
                self.assertEqual(object_hash(input_img), input_hash, "Be careful not to modify the original image!")
                self.compare_images(result, expected)

    def test_edges_centered_pixel(self):
        centeredPixel = {
            'height': 11,
            'width': 11, 
            'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        resultEdges = lab.edges(centeredPixel)
        expectedEdges = {
            'height': 11,
            'width': 11, 
            'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0,
                       0, 0, 0, 0, 255, 0, 255, 0, 0, 0, 0,
                       0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        self.compare_images(resultEdges, expectedEdges)
        #self.assertTrue(False)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
