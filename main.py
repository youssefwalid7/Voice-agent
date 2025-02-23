import time
from openai import OpenAI
from rag import RAG
from langchain.memory import ConversationBufferMemory
import os 
# Ask user for their OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize memory for conversation history
memory = ConversationBufferMemory()

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Function to display chat history
def display_chat_history():
    for chat in memory.chat_memory.messages:
        role = "User" if chat.type == "human" else "Assistant"
        print(f"{role}: {chat.content}")

# Chat loop
while True:
    prompt = input("\nYou: ")
    if prompt.lower() in ["exit", "quit", "bye"]:
        print("Exiting chat. Goodbye!")
        break
    start_time = time.time()

    # Get context using RAG
    obj = RAG(prompt)
    context = obj.context
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Prepare prompt with context
    prompt_with_context = f"""Context: {context}\n
    Question: {prompt}\n
    Task: Answer the question based on the provided context.
    Instructions:
    - Include Article Number: If the context contains an article number (e.g., Article 12, Article 5), include it in your response.
    - Answer from Context: Your response must be directly derived from the provided context. Do not add information outside the context.
    - No Answer in Context: If the context does not contain sufficient information, respond with: "I don't have the answer please detect the company type "
    - Be Clear and Concise: Ensure your response is clear, concise, and directly addresses the question.
    """

    print("\nProcessing...")
    start_time2 = time.time()

    # Generate response
    try:
        stream = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *[
                    {"role": "user" if m.type == "human" else "assistant", "content": m.content}
                    for m in memory.chat_memory.messages
                ],
                {"role": "user", "content": prompt_with_context}
            ],
            stream=True,
        )

        # Collect response
        response = ""  # Initialize response before the loop
        for chunk in stream:
            content = chunk.choices[0].delta.content  # Directly access the attribute
            if content:  # Ensure content is not None
                print(content, end="", flush=True)
                response += content  # Append content to response


        end_time2 = time.time()
        elapsed_time2 = end_time2 - start_time2

        print(f"\n\nElapsed time: {elapsed_time:.6f} seconds")
        print(f"Elapsed time2: {elapsed_time2:.6f} seconds")
        # Save conversation in memory
        memory.chat_memory.add_user_message(prompt)
        memory.chat_memory.add_ai_message(response)

    except Exception as e:
        print(f"An error occurred: {e}")
