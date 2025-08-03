import base64
from openai import OpenAI
from typing import Optional, List, Dict

class Config:
    """
    Конфигурация клиента OpenAI.

    Attributes:
    - default_llm (str, optional): Модель для использования в чатe. По умолчанию "llama4:maverick".
    - translate_llm (str, optional): Модель для перевода текста. По умолчанию "qwen2.5vl:latest".
    - vqa_llm (str, optional): Модель для ответа на вопросы по изображениям. По умолчанию "qwen2.5vl:latest".
    - trl_prompt_template (str, optional): Шаблон для запроса перевода. По умолчанию "Переведи этот текст на {} язык: ".
    - vqa_prompt (str, optional): Prompt для запроса ответа на вопрос по изображению. По умолчанию "Что нарисовано на картинке?".
    - draw_prompt (str, optional): Prompt для генерации картинки. По умолчанию: "на основе сообщения пользователя сформулирую prompt для stable diffusion на английском."
    - model_options (dict): Опции для различных моделей.
    """

    def __init__(
        self,
        default_llm: str = "llama4:maverick",
        translate_llm: str = "qwen2.5vl:latest",
        vqa_llm: str = "qwen2.5vl:latest",
        trl_prompt_template: str = "Переведи этот текст на {} язык: ",
        vqa_prompt: str = "Что нарисовано на картинке?",
        draw_prompt: str = "на основе сообщения пользователя сформулирую prompt для stable diffusion на английском.",
    ):
        self.default_llm = default_llm
        self.translate_llm = translate_llm
        self.vqa_llm = vqa_llm
        self.trl_prompt_template = trl_prompt_template
        self.vqa_prompt = vqa_prompt
        self.draw_prompt = draw_prompt
        self.model_options = {
            "llama4:maverick": {
                "maxTokens": 16384,
                "numThreads": 48,
                "keepAlive": -1,
                "numGpu": 0,
            },
        }

# единая точка входа на все сервисы
class OpenAIClient:

    def __init__(
        self, base_url: str, api_key: str = "-", config: Optional[Config] = None
    ):
        """
        Инициализирует клиент OpenAI с указанным базовым URL, ключом API и конфигурацией.

        Args:
        - base_url (str): Базовый URL для клиента OpenAI.
        - api_key (str, optional): Ключ API для клиента OpenAI. По умолчанию "-".
        - config (Config, optional): Конфигурация клиента.

        Примечание:
        Если конфигурация не предоставлена, будет использована конфигурация по умолчанию, определенная в классе Config.
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.config = config if config else Config()

    def llm_chat(
        self, messages: List[Dict[str, str]], model: Optional[str] = None
    ) -> str:
        """
        Создаёт завершение чата с использованием указанных сообщений и модели.

        Args:
        - messages (list): Список сообщений для завершения чата.
        - model (str, optional): Модель для использования в завершении чата. По умолчанию - та, что задана в объекте.

        Returns:
        - Ответ.
        """
        response = self.client.chat.completions.create(
            model=model if model else self.config.default_llm,
            messages=messages,
        )
        return response.choices[0].message.content

    def llm_question(
        self,
        user_message: str,
        sys_message: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Дает ответ на вопрос с ис пользованием режима чата, указанного вопроса пользователя и системного сообщения и модели (опционально).

        Args:
        - user_message (str): Сообщение пользователя.
        - sys_message (str, optional): Системное сообщение. По умолчанию None.
        - model (str, optional): Модель для использования в завершении чата. По умолчанию - та, что задана в объекте.

        Returns:
        - Ответ.
        """
        messages = []

        if sys_message:
            messages.append({"role": "system", "content": sys_message})
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=model if model else self.config.default_llm,
            messages=messages,
        )

        return response.choices[0].message.content

    def translate(self, text: str, lang: str = "ru") -> str:
        """
        Переводит текст на указанный язык с использованием модели перевода.

        Args:
        - text (str): Текст для перевода.
        - lang (str, optional): Язык перевода. По умолчанию "ru" (русский).

        Returns:
        - str: Переведённый текст.
        """
        response = self.client.chat.completions.create(
            model=self.config.translate_llm,
            messages=[
                {
                    "role": "user",
                    "content": self.config.trl_prompt_template.format(lang) + text,
                }
            ],
        )
        return response.choices[0].message.content

    def vqa(self, image: bytes, question: Optional[str] = None) -> str:
        """
        Выполняет визуальный вопрос-ответ (VQA) для изображения.

        Args:
        - image (bytes): Изображение в бинарном формате.
        - question (str, optional): Вопрос об изображении. Если не указан, используется шаблон вопроса по умолчанию.

        Returns:
        - str: Ответ на вопрос об изображении.
        """
        encoded_string = base64.b64encode(image).decode("utf-8")
        response = self.client.chat.completions.create(
            model=self.config.vqa_llm,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question if question else self.config.vqa_prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/png;base64,{encoded_string}",
                        },
                    ],
                },
            ],
        )
        return response.choices[0].message.content

    def draw(
        self,
        describe: str,
        no_translate: bool = False,
        size: str = "512x512",
        style: str = "natural",
        n: int = 1,
    ) -> bytes:
        """
        Генерирует изображение на основе текстового описания.

        Args:
        - describe (str): Текстовое описание изображения.
        - size (str, optional): Размер генерируемого изображения. По умолчанию "512x512".
        - style (str, optional): Стиль генерируемого изображения. По умолчанию 'natural'. Возможные значения: 'natural', 'vivid'.
        - n (int, optional): Количество генерируемых изображений. По умолчанию 1.

        Returns:
        - bytes: Содержимое изображения в бинарном формате.

        Примечание:
        Использует модель dall-e-1 для генерации изображения на основе текстового описания.
        """
        prompt = (
            describe
            if no_translate
            else self.llm_question(describe, sys_message=self.config.draw_prompt)
        )
        response = self.client.images.generate(
            model="dall-e-1",
            prompt=prompt,
            response_format="b64_json",
            size=size,
            quality="hd",
            style=style,  # natural, vivid
            n=n,
        )
        return base64.b64decode(response.data[0].b64_json)

    def speak(self, text: str, voice: str = "girl") -> bytes:
        """
        Создаёт аудио текст-в-речь с использованием указанного текста и голоса.

        Args:
        - text (str): Текст для преобразования в речь.
        - voice (str, optional): Голос для использования в тексте-в-речь. По умолчанию "girl".

        Returns:
        - Содержимое аудио текст-в-речь.
        """
        with self.client.audio.speech.with_streaming_response.create(
            model="tts-1-hd", voice=voice, input=text
        ) as response:
            content = b"".join(response.iter_bytes())
            return content

    def listen(self, audio: bytes, lang: str = None, translate: bool = False) -> str:
        """
        Выполняет распознавание речи (Speech-to-Text, STT) для предоставленного аудиоданных.

        Args:
        - audio (bytes): Аудиоданные в бинарном формате.
        - lang (str, optional): Язык аудиоданных в формате ISO 639-1. Если не указан, язык будет определен автоматически. Defaults to None.
        - translate (bool, optional): Если True, результат будет переведен на английский язык. Defaults to False.

        Returns:
        - str: Результат распознавания речи в виде текста.

        Примечания:
        - Для распознавания используется модель "whisper-1".
        - Если указан параметр `translate`, язык результата будет английским, независимо от языка исходного аудио.
        """
        if translate:
            return self.client.audio.translations.create(model="whisper-1", file=audio).text
        elif lang:
            return self.client.audio.transcriptions.create(
                model="whisper-1", language=lang, file=audio
            ).text
        else:
            return self.client.audio.transcriptions.create(
                model="whisper-1", file=audio
            ).text


# Пример использования:
if __name__ == "__main__":
    base_url = "http://my_server:5000/v1/"
    client = OpenAIClient(base_url)

    # Используйте методы клиента по мере необходимости
    response = client.translate("Hello, gigahumster!")
    print(response)
