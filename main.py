import requests
import json


class PhotosVKOnYaDisk:
    """
    Класс позволяет получать информацию о фото из VK, сохранять полученные фото на Яндекс Диске,
    и сохранять информацию о них в json файле.
    Необходимо указать название папки, которая создастся на Яндекс Диске.
    Можно изменить количество фотографий(по умолчанию 5), о чем задастся вопрос.
    Можно выбрать альбом VK из которого нужно сохранить фото.
    """
    API_BASE_URL_VK = 'https://api.vk.com/method'
    API_BASE_URL_YA = 'https://cloud-api.yandex.net'

    def __init__(self, user_id_vk, token_ya, token_vk, count_photo=5):
        self.user_id_vk = user_id_vk
        self.token_ya = token_ya
        self.token_vk = token_vk
        self.count_photo = count_photo

    def get_photos_info(self):
        """
        Возвращает список словарей с информацией о фото из VK.
        Нужно ответить на вопросы, сколько загрузить фото и из какого альбома.
        :return: список словарей
        """
        question = input('По умолчанию загрузится 5 фотографий. '
                         'Хотите изменить количество?(Y/y - да, любая клавиша - нет): ')
        if question.upper() == 'Y':
            self.count_photo = int(input('Введите количество фотографий: '))
        album = input('Из какого альбома хотите скачать фото'
                      '(wall - фото со стены, profile — фотографии профиля, saved — сохраненные фотографии)? ')
        while album not in ['wall', 'profile', 'saved']:
            album = input('Вы ввели некорректное значение. Попробуйте еще раз: ')
        params = {
            'owner_id': self.user_id_vk,
            'album_id': album,
            'extended': 1,
            'count': self.count_photo,
            'photo_sizes': 1,
            'access_token': self.token_vk,
            'v': '5.199'
                    }
        response = requests.get(f'{self.API_BASE_URL_VK}/photos.get', params=params)
        photos_list_info = response.json().get('response', {}).get('items')

        return photos_list_info

    def create_folder_on_yad(self):
        """
        Создает папку на Яндекс Диске и возвращает ее название
        :return: Имя папки
        """

        name_folder = input('Введите имя папки Яндекс Диска в которую сохранить фото: ')
        url_folder = f'{self.API_BASE_URL_YA}/v1/disk/resources'
        headers = {
            'Authorization': f'OAuth {self.token_ya}'
        }
        params = {
            'path': name_folder
        }

        requests.put(url_folder, headers=headers, params=params)

        return name_folder

    def _save_info_in_json(self, data, count_photo):
        """
        Создает json файл c информацией о загруженных фото
        :param data: список словарей с информацией о загруженных файлах
        :param count_photo: количество фотографий
        :return: None
        """
        with open('data_file.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"Информация о {count_photo} загруженных фото сохранена в файле 'data_file.json'.")

    def upload_foto_to_yad(self, photo_list):
        """
        Загружает фото на Яндекс Диск
        :param photo_list: Список словарей с информацией о фото из VK
        :return: None
        """
        if len(photo_list) == 0:
            print('В указанном альбоме нет фото!')
            self._save_info_in_json(photo_list, 0)
            return
        photo_list_info_for_json = []
        name_folder = self.create_folder_on_yad()
        list_names = []
        for i, photo in enumerate(photo_list):
            photo_name = f"{photo.get('likes', {}).get('count')}.jpg"
            if photo_name in list_names:
                photo_name = f"{photo.get('likes', {}).get('count')}_{photo.get('id')}.jpg"
            list_names.append(photo_name)
            url = f'{self.API_BASE_URL_YA}/v1/disk/resources/upload'
            headers = {
                'Authorization': f'OAuth {self.token_ya}'
                    }
            params = {
                'path': f'{name_folder}/{photo_name}',
                    }

            response = requests.get(url, params=params, headers=headers)
            url_upload = response.json().get('href')

            url_max_size = ''
            size = ''
            max_size = 0

            for elem in photo.get('sizes'):
                if int(elem.get('height')) * int(elem.get('width')) > max_size:
                    url_max_size = elem.get('url')
                    size = elem.get('type')
                    max_size = int(elem.get('height')) * int(elem.get('width'))

            response = requests.get(url_max_size)
            requests.put(url_upload, files={'file': response.content})
            print(f'Загружено {i + 1} фото из {len(photo_list)}')
            photo_list_info_for_json.append({
                        'file_name': photo_name,
                        'size': size
                        })

        self._save_info_in_json(photo_list_info_for_json, len(photo_list_info_for_json))


user_id_vk_ = input('Введите id пользователя VK: ')
token_ya_ = input('Введите токен Яндекс Диска: ')
token_vk_ = input('Введите токен VK: ')

if __name__ == '__main__':
    obj_1 = PhotosVKOnYaDisk(user_id_vk_, token_ya_, token_vk_)
    photo_info = obj_1.get_photos_info()
    obj_1.upload_foto_to_yad(photo_info)
