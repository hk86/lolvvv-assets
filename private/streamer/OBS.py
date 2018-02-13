import collections
import json
import os


class OBS():
   
   def __init__(self, filepath, img_base_path):
       self._filepath = filepath
       self._img_base_path = img_base_path
       self.reload()
       
   def reload(self):
       with open(self._filepath) as json_data:
           self._json_dict = json.load(json_data, object_pairs_hook=collections.OrderedDict)
           
   def append_pros(self, pros):
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
           
   def _get_scene_pro_txt(self, nickName, teamTag):
       if teamTag:
           return '[{}] {}'.format(teamTag, nickName)
       else:
           return '{}'.format(pro['nickName'])
           
   def save(self, filepath=None):
       if filepath:
           with open(filepath, 'w') as json_data:
               json_data.write(json.dumps(self._json_dict))
       else:
           with open(self._filepath, 'w') as json_data:
               json_data.write(json.dumps(self._json_dict))