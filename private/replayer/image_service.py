from os import path
from requests import get
from pathlib import Path as pathlib
from tarfile import open as taropen
from shutil import rmtree

class ImageService:
    _PUBLIC_IMG_PATH = r'../../public/image'
    _SPECIAL_IMG_PATH = r'../streamer/obs'

    def update_images(self, server_version):
        # https://ddragon.leagueoflegends.com/cdn/dragontail-8.11.1.tgz
        dragontail = 'dragontail-{}.tgz'.format(server_version)
        url = 'https://ddragon.leagueoflegends.com/cdn/{}'.format(dragontail)
        upgrade_folder = 'update/{}'.format(server_version)
        pathlib(upgrade_folder).mkdir(parents=True, exist_ok=True)
        download_path = path.join(upgrade_folder, dragontail)
        response = get(url, stream=True, verify=False)
        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        tar = taropen(download_path)
        tar.extractall(path=upgrade_folder)
        tar.close()
        raise NotImplementedError
        rmtree(upgrade_folder)


    def background_img_path(self):
        return path.join(
            self._SPECIAL_IMG_PATH,
            'hintergrund_schrift.png'
        )

    def banner_img_path(self):
        return path.join(
            self._SPECIAL_IMG_PATH,
            'banner_clean.png'
        )

    def logo_img_path(self):
        return path.join(
            self._SPECIAL_IMG_PATH,
            'lolvvv_logo.png'
        )

    def wallpaper_img_path(self):
        return path.join(
            self._SPECIAL_IMG_PATH,
            'wallpaper_clips.jpg'
        )

    def twitch_img_path(self):
        return path.join(
            self._SPECIAL_IMG_PATH,
            'twitch_logo.png'
        )

    def vvv_logo_path(self):
        return path.join(
            self._SPECIAL_IMG_PATH,
            'vvv_logo.jpeg'
        )

    def champ_small_img_path(self, champ_key: str):
        return path.join(
            self._SPECIAL_IMG_PATH,
            'champion',
            'champion_small',
            '{}.png'.format(champ_key)
        )

    def champbanner_img_path(self, champ_key: str):
        return path.join(
            self._SPECIAL_IMG_PATH,
            'champion_banner',
            '{}.jpg'.format(champ_key)
        )

    def perk_img_path(self, perk_id: int):
        return path.join(
            self._PUBLIC_IMG_PATH,
            '..',
            'perks',
            '{}.png'.format(perk_id)
        )

    def perk_small_img_path(self, perk_id: int):
        return path.join(
            self._SPECIAL_IMG_PATH,
            'perks_small',
            '{}.png'.format(perk_id)
        )

    def pro_med_img_path(self, image_name:str):
        return path.join(
            self._PUBLIC_IMG_PATH,
            'pros',
            'medium',
            image_name
        )

    def team_med_img_path(self, image_name:str):
        return path.join(
            self._PUBLIC_IMG_PATH,
            'teams',
            'medium',
            image_name
        )

