import os

from golem_verificator.imgrepr import PILImgRepr
from golem_verificator.imgverifier import ImgStatistics, \
    ImgVerifier
from golem_verificator.verifier import SubtaskVerificationState
from tests.test_utils.assertlogs import LogTestCase
from tests.test_utils.pep8_conformance_test import Pep8ConformanceTest


# to run from console: go to the folder with images and type:
# $ pyssim base_img_name.png '*.png'
# !!! WARNING !!!
# PILImgRepr().load_from_file() runs
# self.img = self.img.convert('RGB') which may change the result!!!

# you can always check the file's color map by typing:
# $ file myImage.png
# myImage.png: PNG image data, 150 x 200, 8-bit/color RGB, non-interlaced


class TestImageVerifier(LogTestCase, Pep8ConformanceTest):
    PEP8_FILES = ['imgverifier.py']

    def test_pilcrop_vs_luxrender_croppingwindow(self):
        # arrange
        folder_path = os.path.join("tests", "pilcrop_vs_cropwindow_test")

        img0 = PILImgRepr()
        img0.load_from_file(os.path.join(
            folder_path, '0.209 0.509 0.709 0.909.png'))
        cropping_window0 = (0.209, 0.509, 0.709, 0.909)

        img1 = PILImgRepr()
        img1.load_from_file(os.path.join(
            folder_path, '0.210 0.510 0.710 0.910.png'))
        cropping_window1 = (0.210, 0.510, 0.710, 0.910)

        img2 = PILImgRepr()
        img2.load_from_file(os.path.join(
            folder_path, '0.211 0.511 0.711 0.911.png'))
        cropping_window2 = (0.211, 0.511, 0.711, 0.911)

        answer_img0 = PILImgRepr()
        answer_img0.load_from_file(
            os.path.join(folder_path,
                         'answer 0.209 0.509 0.709 0.909.png'))

        answer_img1 = PILImgRepr()
        answer_img1.load_from_file(
            os.path.join(folder_path,
                         'answer 0.210 0.510 0.710 0.910.png'))

        answer_img2 = PILImgRepr()
        answer_img2.load_from_file(
            os.path.join(folder_path,
                         'answer 0.211 0.511 0.711 0.911.png'))

        img_verifier = ImgVerifier()

        # act
        cropped_img0 = img_verifier.crop_img_relative(
            img0, cropping_window0)
        cropped_img0.img.save(
            os.path.join(folder_path, 'cropped' + cropped_img0.get_name()))

        cropped_img1 = img_verifier.crop_img_relative(
            img1, cropping_window1)
        cropped_img1.img.save(
            os.path.join(folder_path, 'cropped' + cropped_img1.get_name()))

        cropped_img2 = img_verifier.crop_img_relative(
            img2, cropping_window2)
        cropped_img2.img.save(os.path.join(folder_path,
                                           'cropped' + cropped_img2.get_name()))

        # assert
        import hashlib
        assert hashlib.md5(
            answer_img0.to_pil().tobytes()).hexdigest() == hashlib.md5(
            cropped_img0.to_pil().tobytes()).hexdigest()

        assert hashlib.md5(
            cropped_img1.to_pil().tobytes()).hexdigest() == hashlib.md5(
            answer_img1.to_pil().tobytes()).hexdigest()

        assert hashlib.md5(
            cropped_img2.to_pil().tobytes()).hexdigest() == hashlib.md5(
            answer_img2.to_pil().tobytes()).hexdigest()

 