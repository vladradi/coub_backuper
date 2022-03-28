# Coub downloader & Viewer


![Screenshot](demo_images/1.PNG)
![Screenshot](demo_images/2.PNG)


Необходимый софт
* [python3.7+](https://www.python.org/downloads/)
* [pip](https://pythonru.com/baza-znanij/ustanovka-pip-dlja-python-i-bazovye-komandy)
* браузер

Рекомендуется во время установки поставить ✅ Add Python 3.x to PATH


#### 1. Установка зависимостей

Linux `python3 -m pip install -r requirements.txt`

Windows `python -m pip install -r requirements.txt`

### Help

```
python3 coub_backuper.py --help
Options:
  -h, --help            show this help message and exit
  -u CHANNELURL, --url=CHANNELURL
                        URL of the channel, default is None'
  -j JSONFILE, --json=JSONFILE
                        JSON file with coubs, default is None'
  -t TYPE, --type=TYPE  Type from from {coubs, reposts, all}, default is coubs
  -d DOWNLOADS, --downloads=DOWNLOADS
                        Download folder for coubs
```
#### 2. Вытягивание всех опубликованных коубов или репостов с канала

```
mkdir downloads/official
python3 coub_backuper.py -u https://coub.com/official -j official.json -d downloads/official 
```

Только коубы без репостов
```
mkdir downloads/mychannel
python3 coub_backuper.py -u https://coub.com/mychannel -j mychannel.json -d downloads/mychannel -t coubs 
```

#### 3. Вытягивание json объектов которые хранят информацию о коубах, которые вы лайкнули

1. Откройте в браузере coub.com, войдите в учетную запись
2. Откройте инструменты разработчика (обычно открывается при нажатии F12)
3. Перейдите во вкладку console
4. Вставьте код из файла browser_download_likes.js или browser_download_channel.js в консоль и дождитесь окончания его работы. Во время
работы скрипта сайт может работать некорректно. Не переходите по ссылкам во вкладке в 
которой работает данный скрипт
5. После окончания работы автоматически скачается файл со всеми метаданными кубов которые вы лайкнули.

Если файл не скачался то из консоли то скопируйте объект который находится под надписью 
`script done! please copy object below and save it to file.json! Right click on object -> Copy object`
откройте блокнот, вставьте текст из буфера обмена и сохраните в файл с названием likes.json

#### 3.1 Редактирование конфигурации

Откройте файл config.py и отредактируйте необходимые параметры.

#### 3.2 Запуск процесса скачивания кубов

1. Запустите в консоли `python3 coub_backuper.py <путь до json файла>`.
2. Дождитесь загрузки ваших коубов.

#### 4. Запустите локальный инстанс плеера для кубов

1. Запустите в консоли `python3 viewer.py <путь до json файла или папки с коубами>`.
2. Откройте в браузере [http://localhost:8888/](http://localhost:8888/)
3. Наслаждайтесь 😊
