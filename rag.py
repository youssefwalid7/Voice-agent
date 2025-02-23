import os
from dotenv import load_dotenv
import re
import openai
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from langchain_openai.chat_models import ChatOpenAI
from utils import  query_classification_agent_qa , query_classification_agent_chapters , read_json , read_text_file  , rewrite_query
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from system_prompt import mci_prompt
memory = ConversationBufferMemory()
# how memory work 
#memory.chat_memory.add_user_message(question)
#memory.chat_memory.add_ai_message(response)


load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ["OPENAI_API_KEY"]
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY2")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY) 
class RAG:
    def __init__(self, question ):
        self.question = question
        #self.pc = PineconeManager(PINECONE_API_KEY, OPENAI_API_KEY)  # Initialize Pinecone
        self.context = "Here are the most relevant answers to the user's query:\n"
        # Run classification and similarity search in parallel
        results = self.run_parallel_tasks()
        self.classification_output = results["chapters_classification"]
        self.most_similar_questions = results["most_similar_questions"]
        self.question=results["rewrited_query"]
        # Add relevant questions to the context
        self.append_similar_questions_to_context()
        # Load additional data from JSON files
        self.load_text_data()
    def run_parallel_tasks(self):
        """Executes query classification and similarity search in parallel."""
        results = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            tasks = {
                executor.submit(query_classification_agent_chapters, self.question ): "chapters_classification",
                executor.submit(query_classification_agent_qa, self.question): "most_similar_questions",
                executor.submit(rewrite_query, self.question): "rewrited_query",
                
            }
            for future in as_completed(tasks):
                task_name = tasks[future]
                try:
                    results[task_name] = future.result()
                except Exception as e:
                    logging.error(f"Error in {task_name}: {e}")
                    results[task_name] = []  # Default to an empty list in case of error
        return results

    def append_similar_questions_to_context(self):
        """Appends the most similar questions and their answers to the context."""
        paths = [f"row data\Q-A_text\QA{i}.txt" for i in self.most_similar_questions]

        #with ThreadPoolExecutor() as executor:
            #results = executor.map(read_json, paths)
        for path in paths:
            self.context += "\n"+ read_text_file(path)
    def load_text_data(self):
        """Loads additional JSON data based on classification output."""
        if 0 in self.classification_output or "0" in self.classification_output:
            return  # Exit if classification output is 0
        paths = [f"row data\chapters_text\companies_rules{i}.txt" for i in self.classification_output]
        #with ThreadPoolExecutor() as executor:
            #results = executor.map(read_json, paths)
        for path in paths:
            self.context += "\n"+ read_text_file(path)
        #self.context += "\n".join(map(str, results))
    def get_answer(self):
        """Generates an answer based on the question and retrieved context."""
        return question_answer(question=self.question, context=self.context)

def question_answer(question , context ):
    prompt_with_context = f"""Context: {context} this is  Ministry of Commerce's rules and information 

Task: Answer the user's question based on the provided context, ensuring compliance with the rules and regulations of the Ministry of Commerce.  

Instructions:

1.Do not include article numbers in your response.
    -If the provided context references specific articles (e.g., Article 12, Article 5), omit these references in your response.
    Instead, focus on explaining the relevant legal provisions without explicitly mentioning article numbers to maintain clarity and accuracy.  


2.Answer from Context Only:
   - Your response must be directly derived from the provided context. Do not add, infer, or speculate on information outside the context.  

3.Output Format:

    The response should be in an unordered list format (e.g., using bullet points).
    Do not include numerical digits (1, 2, 3). Instead, write out numbers in words (one, two, three). if the english and واحد اثنين ثلاثه if arabic 
    

4. **Be Clear and Concise:**  
   - Ensure your response is clear, concise, and directly addresses the user's question. Avoid unnecessary details or ambiguity.  

5. Provide Step-by-Step Processes 
   - If the user asks about a process (e.g., establishing a company, renewing a license), provide a step-by-step guide based on the Ministry of Commerce's perspective. Include any required documents, fees, or procedures mentioned in the context.  

6. Ministry of Commerce Focus:**
   - Tailor your response to align with the Ministry of Commerce's rules, regulations, and processes. Ensure the user understands how to proceed from the Ministry's perspective.  

**Examples:**  

- If the user asks: *"كيف أسس شركة؟"* (How do I establish a company?)  
  - Your response should outline the step-by-step process for company establishment, including required documents, fees, and any relevant articles or regulations from the context.  

- If the user asks: *"ما هي شروط تجديد الرخصة؟"* (What are the conditions for renewing a license?)  
  - Your response should list the conditions and steps for license renewal as per the Ministry of Commerce's guidelines.  

**Important Notes:**  
- Always prioritize accuracy and relevance to the Ministry of Commerce's rules.  
- If the context is unclear or insufficient, do not guess or assume—explicitly state that the answer cannot be provided based on the available information. 
instrucations :
your main task answer only user question form the context user questions are {question}

"""

    

    # Ensure the total tokens do not exceed the model's limit
    max_response_tokens = 8000

    try:
        # Call OpenAI GPT-4 with streaming
        response_stream = client.chat.completions.create(
            model="gpt-4o",  # Use GPT-4 model
            messages=[
                {
                    "role": "system",
                    "content": mci_prompt
                },
                {"role": "user", "content": question}
            ],
            max_tokens=max_response_tokens,
            temperature=.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stream=True  # Enable streaming
        )

        # Iterate through the streamed response
        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except openai.BadRequestError as e:
        yield f"Invalid Request: {e}"
    except openai.AuthenticationError as e:
        yield f"Authentication Error: {e}"
    except Exception as e:
        yield f"An error occurred: {e}"

