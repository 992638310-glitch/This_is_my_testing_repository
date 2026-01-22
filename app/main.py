import time

from agent import Agent

if __name__ == "__main__":
    agent = Agent()
    session_id = f"user_{int(time.time())}"

    print("\n" + "="*50)
    print("🤖 Enterprise AI Agent CLI (v1.0)")
    print(f"🔑 Session ID: {session_id}")
    print("Commands:")
    print("  /upload <path> : 上传文件到知识库")
    print("  /quit          : 退出程序")
    print("="*50 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input: continue

            if user_input.lower() == "/quit":
                break

            if user_input.startswith("/upload "):
                path = user_input.split(" ", 1)[1].strip()
                print(agent.handle_upload(path))
                continue

            # 对话模式
            start_t = time.time()
            response = agent.handle_chat(session_id, user_input)
            duration = time.time() - start_t

            print(f"Bot ({duration:.2f}s): {response}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")