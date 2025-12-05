# DO NOT SAVE API KEY!!!!
import requests

def ask_ai(prompt: str) -> str:
    """
    Ollama의 qwen3:4b 모델에 질문하고 답변을 받는 함수
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:4b",
                "prompt": prompt,
                "stream": False,  # 🔥 스트리밍 끄기 (중요)
            },
            timeout=120,
        )
        response.raise_for_status()  # HTTP 에러일 때 예외 발생

        data = response.json()
        # /api/generate의 응답 예시: {"model":"qwen3:4b","created_at":"...","response":"...","done":true}
        return data.get("response", "(응답 없음)")
    except Exception as e:
        return f"[오류 발생] {e}"

def main():
    print("=== Qwen3:4B 로컬 AI 도우미 ===")
    print("엔터를 누르면 종료됩니다.\n")

    while True:
        user_input = input("질문: ").strip()

        if not user_input:
            print("종료합니다.")
            break

        print("\n[AI 답변]")
        answer = ask_ai(user_input)
        print(answer)
        print()

if __name__ == "__main__":
    main()