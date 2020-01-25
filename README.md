# Фондовый рынок
_Черновик. Подлежит доработке_

Решение предоставляет навигацию по российским акциям с возможностью получения курсовой стоимости за отрезок времени.

## Архитектура
Архитектура решения состоит из:
* [API](src/equities)  для получения данных с фондового рынка
* Поддержки множества возможных пользовательских интерфейсов получения данных
    * [CL](src/interface/cl) Командная строка
    * [WebServer](src/interface/webserver) Веб страница
* [Ядра](src/interface/core), которое предоставляет расширяемый механизм декларации различных команд. Для того что бы 
добавить новую команду достаточно отнаследоваться от абстрактного [класса](src/interface/core/commands/cmd.py), 
задать имя, описание, синтаксис команды и определить механику выполнения.

### Декларация новой команды на примере команды Эхо
ЧЕРНОВИК

## Примеры работы в интерфейсе командной строки
ЧЕРНОВИК

## Примеры работы в интерфейсе веб страницы
ЧЕРНОВИК 




    