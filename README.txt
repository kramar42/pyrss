
Python: RSS Reader
https://github.com/kramar42/pyrss

Для портирование на другой помпьютер нужно:
	django_1.4.1
	sqlite_2.8.17

	в файле setting.py изменить переменные на локальные значения:
	    :62 PATH_TO_PYRSS
	    :86 TEMPLATE_DIRS

cd pyrss; ./manage.py runserver

Страница логина:
    localhost:8000/

Тестовый пользователь:
	login: Test
	pass:  Test

	login: login
	pass:  pass
 
Примеры RSS лент для тестирования:
	# Эти долго закачиваются
    http://rss.cnn.com/rss/cnn_topstories.rss
    http://rss.cnn.com/rss/cnn_latest.rss

    # Хабр побыстрее. Меньше елементов на ленту
    habrahabr.ru/rss
    habrahabr.ru/rss/hubs

Done:
	Перед добавлением новой заметки идет проверка на наличие "http://"
	Если нет такой рассылки или страница недоступка - сообщение.

	Новые локальные файлы при добавлении ленты с дублирующими статьями, не создаються, а используются уже имеющиеся.

	Если локальный файл не открываеться - сообщение с предложение обновить ленту.

	Пагинация елементов:
	    ленты - по 10 на страницу
	    разделы из ленты - по 5

	Пользователи не пересекаються контентом.

	Реализован простейший поиск.

Didn't done:
	Я не закачивал локально XML feed. Нету смысла - вся информация храниться в базе данных. По той же причине не менял в нем линки в итемах на имена локальных файлов.

	При отображении содержимого ленты (/feed/\d+), entry.description браузер не понимает теги. Это потому, что скобки и другие спецсимволы преобразовуются (на этапе загрузки и сохранение, наверное) в &lt; и &gt; знаки.

	Исходные документы МОГУТ изменяться, но приложение должно корректно обновлять локальный документ при изменении удаленного.
	Не знаю как это сделать без скачивания всех документов и сравнения с локальными копиями, что очень долго.
