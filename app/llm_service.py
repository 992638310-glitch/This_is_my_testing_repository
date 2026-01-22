from config import Config

class LLMService:
    def __init__(self):
        self.client = None
        if Config.OPENAI_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def chat(self, system_prompt, history, user_input):
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        if self.client:
            # 真实调用
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content
        else:
            # Mock 模式 (没 Key 时用)
            return f"【Mock LLM】我收到了你的问题：'{user_input}'。\n根据知识库上下文，我发现了相关信息..."