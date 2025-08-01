import os

import dashscope
from prompt_toolkit import PromptSession


def translate_text(input_text: str, target_lang: str, source_lang: str = "auto"):
    messages = [{"role": "user", "content": input_text}]
    translation_options = {
        "source_lang": source_lang,
        "target_lang": target_lang,
    }
    response = dashscope.Generation.call(
        # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model="qwen-mt-turbo",
        messages=messages,  # type: ignore
        result_format="message",
        translation_options=translation_options,
    )
    print(response.output.choices[0].message.content)  # type: ignore


def main():
    session = PromptSession()

    target_lang = "English"
    source_lang = "Chinese"
    prompt_str = "汉译英> "
    while True:
        try:
            text: str = session.prompt(prompt_str)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            if text.startswith("\\c"):
                target_lang = "Chinese"
                source_lang = "English"
                print("Translate English to Chinese")
                prompt_str = "En2Ch> "
            elif text.startswith("\\e"):
                target_lang = "English"
                source_lang = "Chinese"
                prompt_str = "汉译英> "
                print("翻译成英文")
            else:
                translate_text(text, target_lang=target_lang, source_lang=source_lang)
    print("GoodBye!")


if __name__ == "__main__":
    main()
