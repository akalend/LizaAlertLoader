## 'Типы данных редис'


### **List**
Первый тип, который мы обсудим -- `list`. Как следует из названия, он является абстракцией для работы
со списками. Важный нюанс заключается в том, что внутри Redis это реализовано не как массив, а именно
как связанные списки (linked lists) -- для максимально эффективных операций вставки, удаления и обхода
элементов. Классические массивы, несмотря на свою простоту, заслуживают отдельного рассмотрения.
На скорость обращения к элементам по индексу при серьёзном размере списка начинает влиять
их фактическая дальность от "головы" ("левого" края) и "хвоста" ("правого" края) -- так что при таком
сценарии лучше подойдёт `sorted set`, который мы рассмотрим чуть позже.

`List` отлично подходит для реализации очередей, стеков и прочих подобных структур, в которых важен
порядок элементов, а основные манипуляции происходят по "краям" последовательности.

Значениями элементов `list` могут быть только строки, то есть в терминологии протокола ответы команд
представляют элементы в виде `bulk string` (в соответствующих случаях -- `array of bulk strings`).

Семантика относящихся к этому типу команд очень проста, а создатель воспользовался ещё и тем, что
"list" и "left" начинаются с одной буквы. Все _синхронные_ команды про список начинаются с "L" или "R":
    * "L" -- общая операция (напр. `LLEN`) или операция про "левый" конец (напр. `LPUSH`)
    * "R" -- операция про "правый" конец (напр. `RPOP`)
Это должно помочь вам лучше понимать суть операции при первом же взгляде на её название. А вообще,
надо сказать, что номенклатура команд в Redis несколько нестандартна не только для списков; думаю,
все гораздо больше привыкли к тому, что вставка в начало/конец -- это unshift/push, а извлечение
элемента слева/справа -- это shift/pop. Тем не менее, с пониманием обычно приходит осознание
простого факта: "сделано не так, как я привык" не означает "сделано плохо".

Основные команды для работы со списками:
* [`RPUSH key element [element ...]`](https://redis.io/commands/rpush)<br>
    Добавляет каждый перечисленный элемент в конец (`R` -- "справа") указанного списка.
    Вставка происходит последовательно, начиная с первого аргумента `element`: результатом команды
    `RPUSH mylist a b c d e` будет список вида `..., a, b, c, d, e`.<br>
    Комплементарная команда [`LPUSH key element [element ...]`](https://redis.io/commands/lpush) так же
    отвечает за вставку элементов, но в начало списка (`L` -- слева). Так как аргументы тоже
    обрабатываются, начиная с первого, то вызвав `LPUSH somelist x y z` мы получим список вида
    `z, y, x, ...`.<br>
    Варианты [`LPUSHX key element [element ...]`](https://redis.io/commands/lpushx) и
    [`RPUSHX key element [element ...]`](https://redis.io/commands/rpushx) позволяют обеспечить
    дополнительное условие: вставка произойдёт только если список уже содержит элементы.

* [`LLEN key`](https://redis.io/commands/llen)<br>
    Возвращает длину списка. При отсутствии записи по указанному ключу возвращается `0`. Если
    запись содержит другой тип, то, естественно, это приведёт к ошибке, как и во всех случаях
    несовместимости команды и типа данных.

* [`LINSERT key BEFORE|AFTER pivot element`](https://redis.io/commands/linsert)<br>
    Для списка, доступного по ключу `key` вставляет `element` перед или после (`BEFORE`
    или `AFTER`, соответственно) указанного элемента `pivot`. Если список пуст (ключ отсутствует),
    операция не выполняется, а ответом будет `-1`, иначе возвращает количество элементов
    списка после вставки.

* [`LINDEX key index`](https://redis.io/commands/lindex)<br>
    Читает и возвращает элемент с указанным индексом. Индексы устроены очень просто: для списка из
    `N` элементов каждый из них доступен по двум индексам: в зависимости от того, какой конец списка
    используется в качестве отправной точки. Индексы от `0` до `N - 1` (включительно) отвечают,
    соответственно, за элементы с первого (левого) до последнего (правого); отрицательные индексы
    позволяют оттолкнуться от противоположного конца: `-1` соответствует последнему (правому),
    `-2` -- предпоследнему и так далее до `-N`, индексирующему самый левый элемент. Выглядит сложно,
    но стоит однажды это понять и у вас больше никогда не возникнет проблем с этой схемой -- не
    только в контексте Redis, но и где бы то ни было ещё. Кстати, команды `RINDEX` не существует:
    в ней нет необходимости, так как описанная схема индексации позволяет обращаться к списку
    с обоих концов.

* [`LRANGE key start stop`](https://redis.io/commands/lrange)<br>
    Более общая реализация `LINDEX`, позволяющая прочитать срез списка: слева направо от элемента
    с индексом `start` до элемента с индексом `stop` -- включительно. Ответом будет
    array of bulk strings (даже если вы явно читаете единственный элемент, например,
    `LRANGE mylist 0 0`). Один или оба индекса могут быть отрицательными, работая соответствующим
    образом, а выход за пределы диапазона не будет ошибкой, но `stop` должен быть "правее" или
    совпадать со `start`, иначе ответом будет пустой массив. К примеру, имея `a, b, c, d, e` в ключе
    `mykey`, запрос `LRANGE mykey 1 3`, как и запрос `LRANGE mykey 1 -2` вернёт `b, c, d`, но
    в ответе на `LRANGE mykey -2 -4` вы не увидите элементов.<br>
    Должно быть очевидно, что получить полное содержимое списка можно командой `LRANGE key 0 -1`:
    для этого не обязательно знать его размер.

* [`LPOP key [count]`](https://redis.io/commands/lpop)<br>
    Извлекает (не только читает, но и удаляет) элемент в начале списка и возвращает его в виде
    bulk string; при наличии аргумента `count` извлекает указанное количество, возвращая всё в виде
    array of bulk strings (даже если `count == 1`), порядок элементов в ответе будет совпадать
    с порядком внутри списка перед извлечением. Команда [`RPOP key [count]`](https://redis.io/commands/rpop),
    как можно догадаться по уже известной нам семантике, аналогичным образом работает с концом списка,
    при указании `count` так же возвращая array of bulk strings, но в обратном по отношению
    к оригинальному списку порядке.

* [`LTRIM key start stop`](https://redis.io/commands/ltrim)<br>
    `LTRIM` выполняет обрезку списка, оставляя в нём только элементы из указанного между индексами
    `start` и `stop` диапазона (включительно). Логика диапазона работает аналагично `LRANGE`.
    Результат всегда `OK` -- если, конечно, обращение идёт к записи, хранящей список (или к несуществующей).

* [`LREM key count element`](https://redis.io/commands/lrem)<br>
    При `count = 0` удаляет из списка все соответствующие `element` значения, иначе удаляет не
    более, чем абсолютное значение `count`, но направление зависит от знака:
    * Если `count > 0`, поиск происходит слева направо
    * Если `count < 0`, поиск происходит справа налево

Этого достаточно для полноценной работы с отдельным списком, но Redis -- это не только ценный
мех, но и возможность оперировать разными списками в нескольких ключах. Если предыдущее предложение
чем-то вас смутило, напишите об этом отзыв: так можно будет понять, какой процент участников практикума
читает его достаточно внимательно.

* [`RPOPLPUSH source destination`](https://redis.io/commands/rpoplpush)<br>
    Атомарно извлекает крайний правый элемент из списка `source`, добавляет его в начало (слева)
    списка `destination` и возвращает значение этого элемента. Если `source` пуст, операция не
    выполняется, а в ответе будет **null bulk string**. Естественно, `source` и `destination` могут
    совпадать, в этом случае произойдёт циклический сдвиг всех элементов "вправо" -- самый "правый"
    элемент будет перенесён в "левый" конец списка.<br>
    В версии 6.2.0 появилась более универсальная команда
    [`LMOVE source destination LEFT|RIGHT LEFT|RIGHT`](https://redis.io/commands/lmove) и для
    новых реализаций стоит выбирать именно её.

Выше я говорил про семантику команд и `RPOPLPUSH` уже не должно выглядеть каким-то набором букв, а
вполне себе означает "взять справа, вставить слева". Как вы думаете, если бы имена подобных команд
основывались на более широко распространённых договорённостях и именем было бы, например,
`POPUNSHIFT` -- это было бы понятнее?


Более конкретные примеры применения этой структуры данных:
* Естественно, простейшая очередь и стек: `RPUSH` для вставки, `LPOP` (очередь) или `RPOP` (стек)
    для извлечения элементов. Кстати, чтобы дождаться появления чего-то в очереди, не обязательно
    опрашивать её в цикле, лучше использовать _блокирующие_ версии команд. Но, обо всём -- по порядку,
    _блокирующие_ команды мы рассмотрим в разделе 8+3.
* Список событий: `LPUSH` отвечает за добавление элементов в начало, с помощью `LRANGE` -- читаем
    элементы от свежих к старым.
* С небольшой доработкой предыдущего примера получается список, поддерживающий количество
    элементов в заданных рамках: достаточно вместо одиночного `LPUSH` использовать `LPUSH`+`LTRIM`.


### **Set**
`Set` -- абстракция набора ("множества" в математических терминах) уникальных строк без уточнения
порядка хранения. Интересным следствием того, как реализована уникализации элементов является то,
что при вставке нет необходимости предварительно отдельно проверять существование элемента:
если его нет, он будет добавлен, если есть -- просто "найден", вставка не будет произведена.

Команды про `set` имеют очевидный префикс "S".

* [`SADD key member [member ...]`](https://redis.io/commands/sadd)<br>
    Добавляет элемент(ы) в набор. Отвечает количеством созданных элементов.

* [`SREM key member [member ...]`](https://redis.io/commands/srem)<br>
    Удаляет элемент(ы), существующие среди перечисленных. Возвращает количество затронутых элементов.

* [`SMOVE source destination member`](https://redis.io/commands/smove)<br>
    Если указанный элемент `member` не существует в наборе `source`, то ничего не произойдёт и ответом
    будет `0`. Иначе этот элемент будет удалён из `source` и добавлен в `destination`, при этом вернётся `1`
    (даже если такой элемент уже есть в `destination`).

* [`SCARD key`](https://redis.io/commands/scard)<br>
    Возвращает количество элементов в наборе. `CARD` -- это сокращение от `cardinality`, точный
    аналог в русском языке для этого термина -- `мощность множества`.

* [`SISMEMBER key member`](https://redis.io/commands/sismember)<br>
    Возвращает `1`, если `member` присутствует в указанном множестве, иначе `0`.
    Похожая команда [`SMISMEMBER key member [member ...]`](https://redis.io/commands/smismember)
    возвращает массив из `0` и `1` для каждого аргумента `member` в зависимости от его наличия в наборе.

* [`SMEMBERS key`](https://redis.io/commands/smembers)<br>
    Возвращает массив со всеми элементами набора.

* [`SRANDMEMBER key [count]`](https://redis.io/commands/srandmember)<br>
    Возвращает случайный элемент набора. При наличии аргумента `count` вместо
    единственного значения вернётся массив; При положительном значении `count` вы получите указанное
    количество **без повторов**, и не больше, чем хранится в `set` по указанному ключу.
    Однако, если передать отрицательное значение `count`, это отключит логику избегания повторов:
    вам вернётся массив с количеством элементов, точно соответствующим абсолютному значению `count`
    (конечно, кроме случая, когда в наборе вообще нет элементов, то есть ключ не существует).
    Повторы будут случайны, но равномерны (правда, есть нюансы, связанные с распределением,
    начиная с версии 6 распределение стало более "честным" -- подробности, разумеется, есть в
    документации); из этого следует, что запросив меньше, чем есть, или столько же элементов,
    повторы _могут_ встретиться в ответе, а если больше -- то они однозначно там _будут_.<br>
    Родственная команда [`SPOP key [count]`](https://redis.io/commands/spop) работает схожим образом,
    но ещё и удаляет полученные элементы, плюс аргумент `count` не может быть отрицательным.

* [`SSCAN key cursor [MATCH pattern] [COUNT count]`](https://redis.io/commands/sscan)<br>
    `*SCAN ...` -- целое семейство функций для перебора элементов: вариации предназначены для
    разных типов данных, но работают схожим образом, поэтому они будут рассмотрены отдельно.

Помимо перечисленного, для `set` имеется набор функций для операций в математическом
понимании множеств: их объединение, пересечение и разница.

* [`SUNION key [key ...]`](https://redis.io/commands/sunion)<br>
    Вычислить **объединение** (union) всех указанных наборов.
    Возвращает результат в виде массива (из уникальных элементов среди всех перечисленных наборов).
    Родственная команда [`SUNIONSTORE destination key [key ...]`](https://redis.io/commands/sunionstore)
    выполняет ту же операцию, но сохраняет результат в `destination`, а отвечает просто количеством
    уникальных элементов.

* [`SINTER key [key ...]`](https://redis.io/commands/sinter)<br>
    Вычислить **пересечение** (intersection) всех указанных наборов.
    Возвращает результат в виде массива (из элементов, которые присутствует во всех перечисленных наборах).
    Родственная команда [`SINTERSTORE destination key [key ...]`](https://redis.io/commands/sinterstore),
    очевидно, делает то же самое, но сохраняет результат в `destination`, а отвечает количеством
    элементов в созданном наборе.<br>
    В версии 7 добавлена дополнительная команда
    [`SINTERCARD numkeys key [key ...] [LIMIT limit]`](https://redis.io/commands/sintercard) --
    гибрид с той же логикой операции, но вместо ответа получившимся набором или сохранения результата
    в отдельный ключ возвращает просто количество элементов результирующего набора (при наличии
    `limit > 0` операция может завершиться раньше, если набрано указанное количество элементов).
    Кстати, кодовое слово `LIMIT` перед значением `limit` необходимо для покрытия случаев, когда
    именем ключа, в котором хранится набор, может быть "LIMIT" или строка, содержащая десятичное
    число: тогда к этой команде стоит всегда явно добавлять два аргумента -- `LIMIT limit`.

* [`SDIFF key [key ...]`](https://redis.io/commands/sdiff)<br>
    Вычислить **разницу** (difference) между первым набором и остальными: то есть из набора,
    указанного первым, "вычесть" элементы, которые есть во всех остальных наборах.
    Возвращает результат в виде массива (из элементов, которые присутствует только в первом наборе).
    Несложно догадаться, что команда [`SDIFFSTORE destination key [key ...]`](https://redis.io/commands/sdiffstore)
    делает то же самое, только сохраняет результат в указанный ключ и возвращает не результирующий набор,
    а количество элементов в нём.

Примеры применения `set`:
* Отслеживание уникальных записей, например, для формирования списков ip-адресов, обращавшихся
    к некоторой странице по часам, достаточно при запросе этой страницы вызывать
    `SADD someprefix#${YmdH}#${url} ${ip}`.
* Используя `SUNION`, можно сформировать список уникальных адресов за больший отрезок времени или
    с помощью `SINTER` выяснить, кто в некотором интервале запрашивал раныые страницы, и так далее.
* Набор признаков: хранение свойств объектов в ключах вида `obj${obj_id}.prop_ids`, а объектов с
    определёнными свойствомами в `prop${prop_id}.obj_ids` позволяет запрашивать общие свойства
    указанных объектов или искать объекты по комбинации заданных свойств. Правда, реализацию такого
    инструмента лучше не делать "вручную" (с помощью отдельных команд из своего языка), скорее всего
    выйдет объёмно и неудобно: гораздо лучше унести всю логику прямо на сервер, задействовав Lua,
    о котором мы поговорим в разделе 11+3.


### **Hash**
Это именно то, что вы думаете: ассоциативный массив, он же набор пар ключ-значение. Внутренняя
реализация опирается на хеширование ключей для случайного доступа к записям, отсюда и название.
Ключи уникальны, то есть невозможно иметь две записи с разными значениями, но с совпадающими
ключами: запись в существующий ключ перезапишет старое значение.

Как имена ключей (полей), так и значения в этом типе могут быть только строками.

`Hash` -- несортированная структура, то есть не гарантирует зависимость порядка элементов от внешних
факторов вроде имён ключей или последовательности вставки: на то, каким будет порядок при переборе
влияет только внутренняя реализация. Теоретическое максимальное количество записей
в одном ключе, хранящем `hash` -- знакомое любому программисту значение 2<sup>32</sup> - 1,
а практически -- у вас скорее закончится доступная память, чем вы сможете достичь этого предела.

Все команды про `hash` имеют префикс "H", и их не очень много.

* [`HSET key field value [field value ...]`](https://redis.io/commands/hset)<br>
    Создать или обновить в указанном поле его значение.
    В версии 4.0.0 этой команде была добавлена возможность оперировать несколькими парами,
    а не единственной -- поэтому больше нет необходимости использовать отдельную команду
    [`HMSET key field value [field value ...]`](https://redis.io/commands/hmset) для этого случая:
    `HSET` и так позволяет это делать.<br>
    Отвечает количеством созданных записей.<br>
    [`HSETNX key field value`](https://redis.io/commands/hsetnx) -- вариация команды, выполняющая
    операцию только если записи с указанным именем поля не существует; отвечает аналогичным образом,
    но так как может принимать только одну пару "поле-значение", ответом может быть только `0` или `1`.

* [`HGET key field`](https://redis.io/commands/hget)<br>
    Получить значение указанного поля.<br>
    [`HMGET key field [field ...]`](https://redis.io/commands/hmget) позволяет прочитать не одно,
    а несколько значений из разных полей, количество и порядок значений в ответе будут соответствовать
    аргументам. Кстати, поля в аргументах могут повторяться: уникализации не происходит,
    иначе это могло бы внести неоднозначность между количеством запрошенных полей и количеством
    значений в ответе.

* [`HDEL key field [field ...]`](https://redis.io/commands/hdel)<br>
    Удаляет перечисленные поля. Возвращает количество удалённых элементов.

Вот что может показаться странным: существует `HSET`, но его спустя несколько релизов наделили
возможностями `HMSET`, рекомендуя больше не использовать второй вариант. При этом у нас всё ещё
"зачем-то" есть `HGET` и `HMGET`. Причина очень проста. Логика ответа `HSET` и `HMSET` одинакова,
в отличие от пары `HGET` и `HMGET`: первая отдаёт единственный элемент всегда в виде `bulk string`
(или `null bulk string`, если поле отсутствует), а вторая всегда отдаёт `array of bulk strings`,
даже если запрошено единственное поле. Вспомните, о чём говорилось в подразделе про RESP3:
разработчики считают проблемой механики, которые приводят к усложнению реализации клиентов, а
это именно тот случай; клиенту пришлось бы помнить дополнительные данные из контекста вызова,
реализовывать обработку большего количества вариантов ответа и так далее. Это плохо, да и не нужно;
кроме того могло бы усложнить не только код адаптера, но и ваш код, связанный с этой командой.
Для финализации картины давайте детально рассмотрим ответ `HMGET`, это важно и поможет в других
местах. Итак, `HMGET key faaa fbbb faaa fxxx`:
1. Если тип значения по ключу `key` -- не `hash`, вернётся ошибка.
2. Будет сформирован массив, количество элементов которого **всегда** совпадает с количеством полей
    в аргументах, повторяющиеся поля (`faaa`) никуда не пропадают, как я уже сказал в описании к `HMGET`.
3. Для всех найденных записей их значения кодируются как `bulk string` и окажутся в соответствующих местах этого массива.
4. Все отсутствующие записи в ответе кодируются как `null bulk string`.
5. Вы должны обратить внимание, что в п. 2 я не упомянул проверку наличия ключа. Собственно,
    отсутствие ключа при обращении к нему как к содержащему `hash` работает так, будто там
    действительно `hash`, но не хранящий никаких записей. Подобная логика работает и в других местах.

* [`HLEN key`](https://redis.io/commands/hlen)<br>
    Возвращает количество записей.

* [`HEXISTS key field`](https://redis.io/commands/hexists)<br>
    Возвращает `1`, если поле существует, иначе `0`.

* [`HSTRLEN key field`](https://redis.io/commands/hstrlen)<br>
    Возвращает длину строки, являющейся значением для указанного поля в `hash` по указанному ключу.
    Если ключ отсутствует или такого поля в нём не найдено, ответом будет `0`.

* [`HKEYS key`](https://redis.io/commands/hkeys)<br>
    Чтение всех имён полей из `hash` по указанному ключу.

* [`HVALS key`](https://redis.io/commands/hvals)<br>
    Аналогично `HKEYS`, но читает значения.

* [`HGETALL key`](https://redis.io/commands/hgetall)<br>
    Читает весь `hash`, возвращает одномерный массив, в котором нечётные элементы -- имена полей,
    а чётные -- значения. Размер массива в ответе всегда в два раза больше количества содержащихся
    в `hash` записей и очевидно, что всегда будет чётным.

* [`HRANDFIELD key [count [WITHVALUES]]`](https://redis.io/commands/hrandfield)<br>
    Берёт случайную запись из `hash`, возвращает имя поля. При наличии аргумента `count` вместо
    единственного имени поля вернётся массив из них; При положительном значении `count` вы
    получите указанное количество **без повторов**, но не больше, чем хранится в `hash` по указанному ключу.
    Однако, если передать отрицательное значение `count`, это отключит логику избегания повторов:
    вам вернётся массив с количеством элементов, точно соответствующим абсолютному значению `count`
    (конечно, кроме случая, когда в `hash` вообще нет элементов, то есть ключ не существует).
    Повторы будут случайны, но равномерны; из этого следует, что запросив меньше, чем есть, или
    столько же элементов, они _могут_ встретиться в ответе, а если больше -- то однозначно там _будут_.<br>
    Опция `WITHVALUES` позволяет получить не только имена полей, но и значения, ответом также будет
    одномерный массив, но с чередующимися именами полей и значениями: так же, как в `HGETALL`.

* [`HSCAN key cursor [MATCH pattern] [COUNT count]`](https://redis.io/commands/hscan)<br>
    `*SCAN ...` -- целое семейство функций для перебора элементов: вариации предназначены для
    разных типов данных, но работают схожим образом, поэтому они будут рассмотрены отдельно.

* [`HINCRBY key field increment`](https://redis.io/commands/hincrby) и
    [`HINCRBYFLOAT key field increment`](https://redis.io/commands/hincrbyfloat)<br>
    Работают абсолютно точно так же, как рассмотренные ранее [`INCRBY key increment`](https://redis.io/commands/incrby)
    и [`INCRBYFLOAT key increment`](https://redis.io/commands/incrbyfloat) за исключением того, что
    оперируют значениями полей в `hash`, а не всем ключом. Аргументом `increment` может выступать
    в том числе и отрицательное значение, поэтому в отдельных функциях вроде `HDECR*` нет необходимости.

Одно из наиболее очевидных применений для `hash` -- хранение структур, в которых набор полей не
обязательно должен быть известен заранее. В конце концов можно сказать, что это примерно как `object`
в `JSON`, разве что значения могут быть только простыми строками, а не вложенными объектами.


### **Sorted set**
`Sorted set` похож на рассмотренный ранее обычный `set`, по уровню абстракции отличаясь только
наличием для каждого элемента ассоциированного с ним числа с плавающей точкой: в некотором смысле
даже можно провести аналогию и с hash, за разницей в типе ассоциированного значения.

Не стоит обманываться кажущейся простотой: сортированные наборы -- очень мощный инструмент, на
основе которого можно строить неожиданно сложные и полезные вещи. С сортированным списком связано
очень много команд (наверное, больше всех относительно остальных типов), даже если ограничиваться
только _синхронными_.

Все _синхронные_ команды про `sorted set` имеют префикс "Z".
> Почему именно `Z`? Существовало несколько предположений; была даже
> [попытка](https://stackoverflow.com/a/64020752/2072889) связать это с пересечением фонетических
> и культурных особенностей одушевлённых имён, начинающихся на `Z` -- что уже, конечно, далековато
> от информационных технологий. Лично я, столкнувшись с этим, посчитал, что так как **`S`**`ET` уже
> есть, а `SS` (`sorted set`) вносит недостаточно однозначности (в том числе при произношении), `Z`
> образовалось из `ZED` -- "более заметный" `SET` (и совпадает с фонетикой буквы). Точку в этом
> вопросе мог поставить только автор, что он однажды и сделал, извиняясь за сложную ассоциацию:
> `Z` взято из названия координатных осей (`XYZ`), так как "порядок" в сортированных списках
> по сравнению с обычными -- это "дополнительное измерение". Источник:<br>
> https://github.com/redis/redis/issues/4024

Можно легко провести аналогию с ранее рассмотренными командами других типов. Например,
[`ZCARD`](https://redis.io/commands/zcard) и [`SCARD key`](https://redis.io/commands/scard),
[`ZRANDMEMBER key [count [WITHSCORES]]`](https://redis.io/commands/zrandmember) и [`HRANDFIELD key [count [WITHVALUES]]`](https://redis.io/commands/hrandfield),
[`ZUNION`](https://redis.io/commands/zunion) и [`SUNION key [key ...]`](https://redis.io/commands/sunion)
-- и так далее. [`ZSCAN key cursor [MATCH pattern] [COUNT count]`](https://redis.io/commands/zscan)
ожидаемо является местным аналогом `*SCAN`. Кроме этого, объём добавляется командами, отличными
от своих базовых вариантов только направлением обхода или выполнением удаления вместо получения
данных: например, [`ZRANGEBYLEX key min max [LIMIT offset count]`](https://redis.io/commands/zrangebylex),
[`ZREVRANGEBYLEX key max min [LIMIT offset count]`](https://redis.io/commands/zrevrangebylex) и
[`ZREMRANGEBYLEX key min max`](https://redis.io/commands/zremrangebylex) -- соответственно.
Очередное обзорное описание команд я считаю избыточным, так что здесь будет несколько иначе.

* [`ZADD key [NX|XX] [GT|LT] [CH] [INCR] score member [score member ...]`](https://redis.io/commands/zadd)<br>
    Добавить/обновить элемент(ы) и их соответствующие веса. по умолчанию (без дополнительных флагов)
    отсутствующие `member` будут внесены в сортированный список с указанным `score`, для существующих
    -- `score` обновится, а ответом будет количество _добавленных_ элементов.<br>
    Семантика флагов в основном уже должна выглядеть привычно:
    * `XX`/`NX`: добавляет условность: только если `member` существует / не существует
    * `GT`/`LT`: добавляет условность: только если новый `score` больше / меньше хранимого
    `GT`/`LT` сами по себе не мешают добавлению элементов, но это легко настраивается комбинацией с
    `XX`/`NX`.
    * `CH` не влияет на логику записи, но вместо количества _добавленных_ элементов ответом будет
    количество _затронутых_ элементов, то есть как добавленных, так и обновлённых. Это может быть
    полезно при использовании условных опций.
    * `INCR`: вместо обновления `score` новым значением происходит его суммирование с существующим,
    а ответом будет записанная в элемент сумма. При наличии этого флага в аргументах можно передать
    только один элемент (т.е. одну пару `score` и `member`). Фактически это превращает `ZADD` в аналог
    [`ZINCRBY`](https://redis.io/commands/zincrby) (см. документацию), но последняя не имеет флагов
    для управления условностью.

* [`ZRANGE key min max [BYSCORE|BYLEX] [REV] [LIMIT offset count] [WITHSCORES]`](https://redis.io/commands/zrange)<br>
    Получает элементы в указанном диапазоне, используя обход в указанном порядке.

Можно получить список элементов `sorted set`, как упорядоченный по весам, так и по значениям, причём
для формирования результата на сервере не происходит дополнительной сортировки: в привычных БД это
можно представить как таблицу из двух колонок, для каждой из которых добавлен свой индекс
(хотя вариантов полно, от сложных индексов до `PARTITIONING`). В Redis всё несколько хитрее,
используется гибрид хеш-таблицы и [списка с пропусками](https://ru.wikipedia.org/wiki/Список_с_пропусками).
При таком подходе операции вставки/обновления становятся алгоритмически сложнее, но взамен мы
получаем максимально быстрое и гибкое чтение в заданном порядке без лишних накладных расходов.

В целом, порядок устроен так:
* Если записи `A` и `B` имеют разный вес, то `A > B` при `A.score > B.score`.
* Если веса записей `A` и `B` совпадают, то используется лексикографическое сравнение значений
    `A.member` и `B.member` (`memcmp()`): результат будет однозначным, так как внутри одного
    `sorted set` все значения `member` уникальны.

При рассмотрении обычного `set` упоминался пример с ip-адресами, но там мы ограничились отслеживанием
самого факта обращения без подсчёта количества. Получить счётчик очень просто: вместо `set` используем
`sorted set`, меняя `SADD ...` на `ZADD someprefix#${YmdH}#${url} INCR 1 ${ip}`. Вся история с
пересечениями, объединениями и прочим никуда не пропадает, разве что команды превратятся из `S*` в `Z*`.

Другие примеры применения `sorted set`:
* Очевидные вариации на тему таблиц рейтинга разных форм и размеров.
* Частный случай свойств объекта, значения которых могут быть только числами.
* Поля с функцией автодополнения: в ключе `mydata` сохраняем все возможные варианты, при появлении
    чего-то на входе вызываем `ZRANGE mydata "[${input}" "[${input}\xff" BYLEX`, таким образом получая
    все значения, которые начинаются с $input.

Для большего погружения обязательно рекомендую всем ознакомиться с отличной статьёй из официального источника:
[Secondary indexing with Redis](https://redis.io/topics/indexes).

