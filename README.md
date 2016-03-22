# selectel

Коллекия скриптов для работы с https://selectel.ru (vps provider), использует novaclient. 

## Начало работы:
Идем сюда: https://habrahabr.ru/company/selectel/blog/242001/, выполняем установку и настройку, все до пункта "Просмотр информации о сетях"
Для работы с квотами понадобиться создать ключ: https://support.selectel.ru/keys/, дальше симпортировать его как OS_SELECTEL_TOKEN:

`
export OS_SELECTEL_TOKEN=ТОКЕН
`

`nova.py` - создание серверов с автоматическим увеличением квот если не хватает.

`report.py` - Создание отчетов по серверам, в формате csv.
