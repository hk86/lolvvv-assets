import datetime
import locale
from os import path
from pathlib import Path
from typing import Dict, Any

from scipy.signal import fftconvolve
from scipy.signal.windows import gaussian

from image_service import ImageService
from ingame_champ import BlueIngameChamp, RedIngameChamp, IngameChamp
from summoner.fact_team import FactTeamId
from numpy import sqrt, sum, min, max, asarray, double, array, ones, shape, set_printoptions
from resizeimage import resizeimage  # pip install python-resize-image
from PIL import Image


class IngamePosition:
    def __init__(self, image_service=None):
        if image_service is not None:
            self._image_service = image_service
        else:
            self._image_service = ImageService()
        self._in_game_champ = None

    def init_champs(self, lol_screenshot: Image):
        self._in_game_champ = {
            FactTeamId.BLUE: [],
            FactTeamId.RED: []
        }
        for in_team_idx in range(5):
            blue_champ = BlueIngameChamp(in_team_idx, lol_screenshot)
            red_champ = RedIngameChamp(in_team_idx, lol_screenshot)
            self._in_game_champ[FactTeamId.BLUE].append(blue_champ)
            self._in_game_champ[FactTeamId.RED].append(red_champ)

    def get_in_game_champ(self, champ_key: str, team_id: FactTeamId) -> IngameChamp:
        set_printoptions(formatter={"float_kind": lambda x: "%g" % x})
        if self._in_game_champ is None:
            raise AssertionError("you have to assign a lol_screenshot first")
        team = self._in_game_champ[team_id]
        champ_img = Image.open(self._image_service
                               .champ_small_img_path(champ_key))
        compare_value: Dict[float, IngameChamp] = {}
        for in_game_champ in team:
            comp_index = float(sum(self._pic_compare(in_game_champ.icon, champ_img)))
            compare_value[comp_index] = in_game_champ
        best_match = sorted(compare_value.items(), reverse=True)[0]
        if best_match[0] > 1.0:
            return best_match[1]
        else:
            debug_folder = "/debug/{}_{}".format(champ_key, datetime.now().strftime("%m%d-%H%M%S"))
            print("Couldn't find ingame champ position creating files {}".format(debug_folder))
            Path(debug_folder).mkdir(parents=True, exist_ok=True)
            champ_img_path = path.join(debug_folder, '{}.png'
                                       .format(champ_key))
            Image.save(champ_img_path, "PNG")
            for in_game_champ in team:
                comp_index = float(sum(self._pic_compare(in_game_champ.icon, champ_img)))
                in_game_champ_path = path.join(debug_folder,
                                       "{}_{}".format(in_game_champ.in_team_idx,
                                                      locale.format_string('%.3f', comp_index)))
                in_game_champ.icon.save(in_game_champ_path, "PNG")

    @staticmethod
    def _equalize_pics(im1: Image, im2: Image):
        if im1.size == im2.size:
            return im1, im2
        if im1.size < im2.size:
            im2 = resizeimage.resize_cover(im2, im1.size)
        else:
            im1 = resizeimage.resize_cover(im1, im2.size)
        return im1, im2

    def _pic_compare(self, im1: Image, im2: Image):
        im1, im2 = self._equalize_pics(im1, im2)
        num_metrics = 2
        sim_index = [2 for _ in range(num_metrics)]
        # Create a 2d gaussian for the window parameter
        win = array([gaussian(11, 1.5)])
        win2d = win * win.T
        for band1, band2 in zip(im1.split(), im2.split()):
            b1 = asarray(band1, dtype=double)
            b2 = asarray(band2, dtype=double)
            # SSIM
            res, smap = self._ssim(b1, b2, win2d)
            m = [res, self._nrmse(b1, b2)]
            for i in range(num_metrics):
                sim_index[i] = min([m[i], sim_index[i]])
        return sim_index

    @staticmethod
    def _ssim(im1, im2, window, k=(0.01, 0.03), l=255):
        """See https://ece.uwaterloo.ca/~z70wang/research/ssim/"""
        # Check if the window is smaller than the images.
        for a, b in zip(window.shape, im1.shape):
            if a > b:
                return None, None
        # Values in k must be positive according to the base implementation.
        for ki in k:
            if ki < 0:
                return None, None

        c1 = (k[0] * l) ** 2
        c2 = (k[1] * l) ** 2
        window = window / sum(window)

        mu1 = fftconvolve(im1, window, mode='valid')
        mu2 = fftconvolve(im2, window, mode='valid')
        mu1_sq = mu1 * mu1
        mu2_sq = mu2 * mu2
        mu1_mu2 = mu1 * mu2
        sigma1_sq = fftconvolve(im1 * im1, window, mode='valid') - mu1_sq
        sigma2_sq = fftconvolve(im2 * im2, window, mode='valid') - mu2_sq
        sigma12 = fftconvolve(im1 * im2, window, mode='valid') - mu1_mu2

        if c1 > 0 and c2 > 0:
            num = (2 * mu1_mu2 + c1) * (2 * sigma12 + c2)
            den = (mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2)
            ssim_map = num / den
        else:
            num1 = 2 * mu1_mu2 + c1
            num2 = 2 * sigma12 + c2
            den1 = mu1_sq + mu2_sq + c1
            den2 = sigma1_sq + sigma2_sq + c2
            ssim_map = ones(shape(mu1))
            index = (den1 * den2) > 0
            ssim_map[index] = (num1[index] * num2[index]) / (den1[index] * den2[index])
            index = (den1 != 0) & (den2 == 0)
            ssim_map[index] = num1[index] / den1[index]

        mssim = ssim_map.mean()
        return mssim, ssim_map

    @staticmethod
    def _nrmse(im1, im2):
        a, b = im1.shape
        rmse = sqrt(sum((im2 - im1) ** 2) / float(a * b))
        max1 = max(im1)
        max2 = max(im2)
        max_val = max([max1, max2])
        min_val = min([min(im1), min(im2)])
        return 1 - (rmse / (max_val - min_val))
