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
def get_answer_streaming(question):
        rag_instance = RAG(question)  # Initialize RAG pipeline
        response_generator = rag_instance.get_answer(memory)  # Get response generator
        for chunk in response_generator:
            yield chunk  # Yield each chunk as it arrives
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
   

    # Generate response
    try:
        for response_chunk in get_answer_streaming(prompt):
            print(response_chunk, end="", flush=True) 
        

        memory.chat_memory.add_user_message(prompt)
        memory.chat_memory.add_ai_message(prompt)

    except Exception as e:
        print(f"An error occurred: {e}")
