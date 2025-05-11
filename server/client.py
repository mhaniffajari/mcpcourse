import asyncio
import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

async def run_memory_chat():
    """ Run a chat using MCPAgent's built-in conversation memory. """
    load_dotenv()
    os.environ["GOOGLE_GENAI_API_KEY"] = os.getenv("GOOGLE_GENAI_API_KEY")
    config_file = "server/weather.json"

    print("Initializing MCPAgent...")
    client = MCPClient.from_config_file(config_file)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=os.getenv("GOOGLE_GENAI_API_KEY"))

    agent = MCPAgent(llm=llm, client=client, max_steps=15, memory_enabled=True)

    print("Starting chat...")
    print("Type 'clear' to clear the conversation history.")
    print("===========================\n")

    try:
        while True:
            user_input = input("\nYou: ")

            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation...")
                break
            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue

            print("\nAssistant: ", end="", flush=True)

            try:
                start_time = time.time()
                response = await agent.run(user_input)
                duration = time.time() - start_time

                print(f"\n[DEBUG] Tool response time: {duration:.2f} seconds")

                # Optional wait for slow tools (can remove later)
                if duration < 3:
                    await asyncio.sleep(1)  # add delay to prevent LLM from racing ahead

                print(response)

            except Exception as e:
                print(f"Error: {e}")

    finally:
        if client and client.sessions:
            await client.close_all_sessions()

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(run_memory_chat())
