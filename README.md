# Сервер MCP для поиска файлов

Это сервер Model Context Protocol (MCP), написанный на Python, который интегрируется с Cline в VSCode. Он ищет файлы в файловой системе по фрагменту пути и возвращает результаты в формате JSON.

## Требования

- Python 3.9 или выше
- Пакет Python `mcp` (установить с помощью `pip install mcp`)
- VSCode с установленным расширением Cline

## Установка

1. Клонируйте этот репозиторий:
   ```bash
   git clone https://github.com/kyan9400/file-finder-mcp.git
   cd file-finder-mcp
   ```

2. Установите необходимый пакет Python:
   ```bash
   pip install mcp
   ```

3. Обновите файл конфигурации Cline, чтобы включить сервер MCP:
   - Откройте или создайте файл конфигурации Cline (например, `C:\Users\<ВашеИмяПользователя>\AppData\Roaming\Code\User\cline_config.json` на Windows).
   - Добавьте следующую конфигурацию:
     ```json
     {
       "mcpServers": {
         "file-finder-mcp": {
           "args": ["file_finder_server.py"],
           "command": "python",
           "autoApprove": [],
           "disabled": false
         }
       }
     }
     ```

## Запуск сервера

Запустите сервер вручную для тестирования:
```bash
python file_finder_server.py
```
Также Cline автоматически запустит его при использовании инструмента.

## Тестирование с Cline

1. Откройте VSCode с активным расширением Cline.
2. Используйте следующий запрос в интерфейсе Cline для тестирования сервера:
   ```text
   Найдите файлы в файловой системе, содержащие фрагмент "test"
   ```
3. Cline вызовет инструмент `find_files`, и вы увидите ответ в формате JSON, например:
   ```json
   [
     {
       "file_name": "test_file.txt",
       "path": "D:\\files\\NEW JOB\\file-finder-mcp\\test_file.txt",
       "size": 1234,
       "created": "2025-03-02T13:00:00.000000"
     }
   ]
   ```

## Примечания

- Поиск начинается с текущей рабочей директории, где запущен сервер.
- Поиск нечувствителен к регистру.
- Размер указывается в байтах, а дата создания — в формате ISO.

## Лицензия

Этот проект лицензирован под лицензией MIT.
```

### Инструкции по использованию файла README.md

1. **Создайте файл README.md:**
   - В VSCode щелкните правой кнопкой мыши в боковой панели Explorer и выберите "Создать новый файл".
   - Назовите файл `README.md` и откройте его.

2. **Скопируйте содержимое:**
   - Скопируйте приведенное выше содержимое и вставьте его в файл `README.md`.

3. **Сохраните файл:**
   - Сохраните файл `README.md`, нажав `Ctrl+S` (или `Cmd+S` на Mac).

4. **Закоммитьте и отправьте изменения в GitHub:**
   - Если вы еще не закоммитили и не отправили изменения, сделайте это сейчас:
     ```bash
     git add README.md
     git commit -m "Добавлен файл README с инструкциями по установке и использованию"
     git push origin main
     ```

5. **Проверьте на GitHub:**
   - Перейдите в ваш репозиторий на GitHub (https://github.com/kyan9400/file-finder-mcp) и убедитесь, что файл `README.md` отображается и содержит правильное содержимое.

Этот файл README.md предоставляет четкие инструкции для тех, кто хочет настроить, запустить и протестировать ваш сервер MCP. Если у вас есть дополнительные вопросы или требуется дальнейшая настройка, не стесняйтесь обращаться!
