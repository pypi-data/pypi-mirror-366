import cv2
import numpy
import matplotlib.pyplot as plot
import os

def sharpness_score(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()

    print(f'Sharpness score: {score:.3f}')

    return score

def default_sharpness_filter(image):
    return sharpness_score(image) > 100

def no_quality_filter(image):
    return True

def default_denoise(image):
    image = cv2.bilateralFilter(image, d = 15, sigmaColor = 100, sigmaSpace = 100)
    image = cv2.bilateralFilter(image, d = 15, sigmaColor = 100, sigmaSpace = 100)

    blurred_image = cv2.GaussianBlur(image, (3, 3), sigmaX = 1)

    blur_subtraction = -0.85
    image = cv2.addWeighted(image, 1 - blur_subtraction, blurred_image, blur_subtraction, 0)

    return image

def no_denoise(image):
    return image

class KZStack:
    def __init__(self):
        self.image_filepaths = []
        self.biases = None
        self.final_image = None
        self.filter = None

    def get_image_filepaths(self, stack_path, include_subdirectories = False):
        '''
        Load the path of the images to use.
        '''

        for root, dirs, files in os.walk(stack_path):
            if not include_subdirectories:
                dirs.clear()

            for name in files:
                self.image_filepaths.append(os.path.join(root, name))

            self.image_filepaths.sort(reverse = True)

        return self.image_filepaths

    def add_biases(self, biases_path):
        '''
        Add the biases for your camera, if you have them.
        '''

        self.biases = cv2.imread(biases_path)

        return self.biases

    def stack_accumulate(self, quality_filter = default_sharpness_filter, MAX_IMAGES = None, GAMMA = 2.2, ND = 1):
        '''
        Stacks images together, brightening the overall picture.

        Parameters:
            quality_filter: a function that takes in an image and outputs whether or not to use it
            MAX_IMAGES: the maximum amount of images to use
            GAMMA: an effect to undo what many cameras do, set to 1 if you would not like to use it
            ND: simulates an ND filter, multiplies individual images by 1 / ND (NOT STOPS!)
        '''

        self.final_image = None
        self.image_count = 0

        while self.image_filepaths and (MAX_IMAGES is None or self.image_count < MAX_IMAGES):
            image_path = self.image_filepaths.pop(-1)
            image = cv2.imread(image_path)

            if self.final_image is None:
                self.final_image = numpy.zeros_like(image, dtype = 'float32')

            if quality_filter(image):
                image = (image ** GAMMA) / ND
                image = numpy.nan_to_num(image, nan = 0, posinf = 255, neginf = 0)
                self.final_image += image
                self.image_count += 1

            else:
                print(f'Bad Image: {image_path}')

        return self.final_image, self.image_count

    def stack_maximum(self, quality_filter = default_sharpness_filter, MAX_IMAGES = None):
        '''
        Stacks images together, taking the maximum pixel value at each position. Treat GAMMA as 2.2 for post-processing.

        Parameters:
            quality_filter: a function that takes in an image and outputs whether or not to use it
            MAX_IMAGES: the maximum amount of images to use
        '''

        self.final_image = None
        self.image_count = 0

        while self.image_filepaths and (MAX_IMAGES is None or self.image_count < MAX_IMAGES):
            image_path = self.image_filepaths.pop(-1)
            image = cv2.imread(image_path)

            if self.final_image is None:
                self.final_image = numpy.zeros_like(image, dtype = 'float32')

            if quality_filter(image):
                image = numpy.nan_to_num(image, nan = 0, posinf = 255, neginf = 0)
                self.final_image += numpy.maximum(self.final_image, image)
                self.image_count += 1

            else:
                print(f'Bad Image: {image_path}')

        self.final_image = self.final_image ** 2.2

        return self.final_image, self.image_count

    def stack_average(self, quality_filter = default_sharpness_filter, MAX_IMAGES = None, FINAL_ND = 1):
        '''
        Stacks images together, averaging the pixel values at each position (accumulate ND = 0, / image count). Treat GAMMA as 2.2 for post-processing.

        Parameters:
            quality_filter: a function that takes in an image and outputs whether or not to use it
            MAX_IMAGES: the maximum amount of images to use
            (GAMMA): treat it as 2.2
            FINAL_ND: simulates an ND filter on the final image, multiplies individual images by 1 / ND
        '''

        self.final_image, self.image_count = self.stack_accumulate(quality_filter = quality_filter, MAX_IMAGES = MAX_IMAGES, GAMMA = 1, ND = 0)

        self.final_image /= self.image_count

        self.final_image *= 1 / FINAL_ND

        self.final_image = self.final_image ** 2.2

        return self.final_image

    def post_process_final_image(self, denoise_function = default_denoise, GAMMA = 2.2):
        '''
        Post-process the final image, denoising it and redoing the gamma effect.

        Parameters:
            denoise_function: a function that takes in an image and outputs a denoised version
            GAMMA: the opposite of what was used to reverse the effect, should be 2.2 unless you changed it
        '''

        self.original_image = self.final_image.copy()
        self.final_image = denoise_function(self.final_image)

        self.final_image = numpy.clip(self.final_image, 0, None)
        self.final_image = self.final_image ** (1 / GAMMA)

        if self.biases is not None:
            self.final_image -= self.biases

        self.final_image = numpy.clip(self.final_image, 0, 255)
        self.final_image = self.final_image.astype(numpy.uint8)

        return self.final_image

    def save_final_image(self, save_path):
        cv2.imwrite(save_path, self.final_image)

    def show_final_image(self):
        image_rgb = cv2.cvtColor(self.final_image, cv2.COLOR_BGR2RGB)

        plot.figure(figsize = (16, 9))
        plot.imshow(image_rgb)
        plot.axis('off')
        plot.tight_layout(pad = 0)

        plot.show()