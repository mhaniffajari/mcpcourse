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
    config = {
        "mcpServers": {
            "http": {
                "url": "http://localhost:9090/sse"
            }
        }
    }

    print("Initializing MCPAgent...")

    # Create MCP client from the configuration file
    client = MCPClient.from_dict(config)
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
                # Start the timing of tool execution
                start_time = time.time()

                # Use asyncio.wait_for to manage timeouts (e.g., 60 seconds)
                response = await asyncio.wait_for(agent.run(user_input), timeout=60)  # Timeout increased here

                # Measure time taken for the tool response
                duration = time.time() - start_time

                print(f"\n[DEBUG] Tool response time: {duration:.2f} seconds")

                # If the response took less than 3 seconds, allow a short delay
                if duration < 3:
                    await asyncio.sleep(1)  # add delay to allow MCP to complete processing

                print(response)

            except asyncio.TimeoutError:
                print("❌ Timeout error: The request took too long to process.")
                # Retry after 2 seconds if there's a timeout
                print("Retrying the request...")
                await asyncio.sleep(2)  # Wait before retrying
                continue
            except Exception as e:
                print(f"Error: {e}")
                # Retry after 2 seconds if there's an error
                print("Retrying the request...")
                await asyncio.sleep(2)  # Wait before retrying
                continue

    finally:
        if client and client.sessions:
            await client.close_all_sessions()
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(run_memory_chat())
