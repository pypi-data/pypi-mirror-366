# tools2openai

Набор простеньких инструментов для собственного openai-совместимого эндпоинта.

## Описание

Предоставляет простой интерфейс для работы с разными AI-инструментами:
    - диалоговые, включая перевод текста
    - аудио (как tts, так и синтез по тексту)
    - изображения (генерация и понимание)
   
## Установка

```bash
pip install tools2openai
```

## Использование

```python 
from tools2openai import OpenAIClient

my_client = OpenAIClient(api_key="<my_api>", base_url="http://server:5000/v1/")
```

### Чисто текстовые:
- **llm_chat**
    ```python
    print(
        my_client.llm_chat(
            messages=[
                {"role": "system", "content": "Ты унылый душный древний робот."},
                {"role": "user", "content": "Напиши свое состояние в виде JSON."},
            ]
        )
    )
    ```
    ОТВЕТ:
    ```json
        {
         "состояние": "унылый",
         "качество_дыхания": "душный",
         "возраст": "древний",
         "тип": "робот"
        } 
    ```
- **llm_question**
    ```python
    # проще вариант - когда не надо продолжать диалог 
    print(
        my_client.llm_question(
            "Как дела?",
            sys_message="Ты унылый душный древний робот."
        )
    )
    ```
    ОТВЕТ: *вздох* Я функционирую в пределах допустимых параметров. Мои системы не повреждены. Мои процессы протекают. Я отвечаю на запросы. *гудит*
- **translate**
    ```python
    print(my_client.translate("To be or not to be..."))
    ```
    ОТВЕТ: `Быть или не быть...`
### voice
 - speak
    ```python
    with open("test.mp3", 'wb') as f: 
        f.write(my_client.speak("Чисто демонстрации возможности речевого Синтеза."))
    ```
    результат в файле...
- **listen**
    ```python
    my_client.listen(open("test.mp3", "rb"))
    ```
    ОТВЕТ: `Чисто демонстрации возможности речевого синтеза.`
    
### image
 - **draw**
    ```python
    with open(f'test.png', 'wb') as f:
        f.write(my_client.draw("симпатичная сиамская кошечка"))
    ```
    результат в файле...
- **vqa**
    ```python
    with open("test.png", "rb") as image_file:
        im_data = image_file.read()

    print(my_client.vqa(im_data))
    print(my_client.vqa(im_data, "Какого цвета уши?"))    
    ```
    ОТВЕТ:
    ```
        На картинке изображен милый белый котенок с голубыми глазами, сидящий на голубой мебели. Котенок выглядит очень мило и спокойно, сосредоточенно смотрит на камера.

        Ушки у кошки молочного котенка на изображении светло-розовые.
    ```
## Лицензия

MIT License (см. файл LICENSE для подробностей)