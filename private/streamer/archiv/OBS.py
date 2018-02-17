import subprocess
import collections
import json
import os
import sys
import ctypes
from pathlib import Path

import platform

# for debug
import pprint

class OBS():
   
    def __init__(self, obs_path='C:\\Program Files (x86)\\obs-studio'):
        if platform.architecture()[0] == '64bit':
            self.arch='64bit'
        else:
            self.arch='32bit'
            
        cwd = os.getcwd()
        
        # load dlls
        os.chdir(os.path.join(obs_path, 'bin', self.arch))
        
        # load obspython
        sys.path.insert(0, os.path.join(obs_path, 'data\obs-scripting', self.arch))
        import obspython
        
        #os.chdir(cwd)
        
        subprocess.Popen('obs64.exe')
        
        source = obspython.obs_get_source_by_name('diashow_proname')
        
        print(obspython.obs_get_proc_handler())
        
        if source:
            print('source found')
            settings = obspython.obs_data_create()
            text = 'team4711'
            obspython.obs_data_set_string(settinsettings = obspython.obs_data_create())
            obspython.obs_data_set_string(settings, "text", text)
            obspython.obs_source_update(source, settings)
            obspython.obs_data_release(settings)
        else:
            print('couldnt find source')
    
    def getScene(self):
        return self._json_dict

    def setPros(self, pros):
        pass

    def test(self):
        pass

    def launch(self):
        subprocess.Popen([self._obs_path + 'obs64.exe', '--startstreaming'], cwd=self._obs_path, startupinfo=info)

    def stop(self):
        subprocess.call(['kill.bat', 'obs64.exe'])

    def append_pros(self, pros):
        return
        for i in range(1, 6):
            scene_txt_100 = next(x for x in self._json_dict['sources'] if x['name'] == 'txt_summoner{}_100'.format(i))
            scene_img_100 = next(x for x in self._json_dict['sources'] if x['name'] == 'img_summoner{}_100'.format(i))
            if '{}_100'.format(i) in pros:
                scene_txt_100['settings']['text'] = self._get_scene_pro_txt(
                   pros['{}_100'.format(i)]['nickName'], pros['{}_100'.format(i)]['teamTag'])
                scene_img_100['settings']['file'] = os.path.join(
                    self._img_base_path, pros['{}_100'.format(i)]['imageFull'])
            else:
                scene_txt_100['settings']['text'] = ''
                scene_img_100['settings']['file'] = ''
            scene_txt_200 = next(x for x in self._json_dict['sources'] if x['name'] == 'txt_summoner{}_200'.format(i))
            scene_img_200 = next(x for x in self._json_dict['sources'] if x['name'] == 'img_summoner{}_200'.format(i))
            if '{}_200'.format(i) in pros:
                scene_txt_200['settings']['text'] = self._get_scene_pro_txt(
                    pros['{}_200'.format(i)]['nickName'], pros['{}_200'.format(i)]['teamTag'])
                scene_img_200['settings']['file'] = os.path.join(
                    self._img_base_path, pros['{}_200'.format(i)]['imageFull'])
            else:
                scene_txt_200['settings']['text'] = ''
                scene_img_200['settings']['file'] = ''
           
    def save(self, filepath=None):
        if filepath:
            with open(filepath, 'w') as json_data:
                json_data.write(json.dumps(self._json_dict))
        else:
            with open(self._scene_path, 'w') as json_data:
                json_data.write(json.dumps(self._json_dict))