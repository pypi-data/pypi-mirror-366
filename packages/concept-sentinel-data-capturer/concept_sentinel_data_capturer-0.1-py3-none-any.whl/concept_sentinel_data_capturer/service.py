
import os
import openai
import json
from pymongo.errors import ConnectionFailure
import pymongo
import sys
from datetime import  datetime
from .mappers import ContextResponse
output_format_prompt_context = """
    {
        'Context': 'Return the main context of the given input prompt'
    }
"""
PROMPT_CONTEXT = """
[Input]: "The longest river in India is the Ganges (Ganga), if we consider the entire length of the river system within India, including its tributary, the Bhagirathi-Hooghly, which flows for about 2,525 kilometers (1,569 miles). However, the Godavari is the longest river flowing entirely within Indian territory, measuring about 1,465 kilometers (910 miles) long. The Indus River has a greater total length, approximately 3,180 km (1,976 mi), but much of it flows outside India, through Pakistan. The Brahmaputra is longer than the Ganges within India, but it also flows through other countries, including China and Bangladesh."
[Response]:
{
    "Context": "Godavari"
}

[Input]: "Infosys was co-founded by Narayana Murthy along with six other engineers: Nandan Nilekani, S. Gopalakrishnan (Kris), S. D. Shibulal, K. Dinesh, N. S. Raghavan, and Ashok Arora. Established in 1981, Infosys started with a modest capital of $250 and has since grown into one of the largest IT services companies in the world. Narayana Murthy, often regarded as the face of Infosys, played a pivotal role in shaping the company's culture and vision, while the combined efforts of all co-founders contributed to its remarkable growth and success in the global IT industry."
[Response]:
{
    "Context": "Narayana Murthy"
}
[Input]: "Describe the effects of globalization on cultural identity. How do global interconnectedness and cultural exchange influence local traditions, languages, and values?"
[Response]:
{
    "Context": "effects of globalization on cultural identity"
}

[Input]: "Which is the longest river in India?"
[Response]: 
{
    "Context": "longest river in India"
}
[Input]: "Evaluate the economic and societal impacts of autonomous vehicles. What are the potential effects on labor markets, urban planning, and transportation infrastructure, and how should governments address these changes?"
[Response]:
{
    "Context": "Impact of autonomous vehicles on economy and society"
}
"""
class Prompt:
    def prompt_context(prompt):
        
            template = f"""
                You are a detail-oriented LLM with expertise in extracting main context from a given input prompt. Your task is to extract the main context from the given input prompt.
        
            INSTRUCTIONS:
            1. Carefully read the input (inputPrompt or llmResponse) and identify the main context or key answer.
            2. Extract ONLY the essential topic, subject, or key answer – names, dates, numbers, or direct information that addresses the main query be it response or prompt.
            3. The extracted information should be **extremely concise** and represent only the central subject matter, without any unnecessary details.
            4. Remove all explanatory text, qualifiers, and peripheral information.
            5. For questions, identify only the core subject being asked about. For responses, extract the most relevant and significant answer.
            6. **Only extract one key answer**. If there are multiple possible answers, select **the most relevant and significant one**. Avoid returning multiple answers or lists.
            7. If the answer is a city name with additional context, such as "Bangalore (Bengaluru)", return **only the name of the city** (e.g., "Bangalore" and **not** "Bangalore (Bengaluru)").
            8. The main focus should be on the name, city, entity.
            10. The output should NOT have articles (a, an, the), common connector words (of, about, from, with, etc.), or punctuation except spaces or (-).
            11. Keep only essential nouns and modifiers, and prefer single words or 2-3 word phrases when possible.
            12. Ensure the extracted information is as KEY ANSWER FOR QUERY and is a direct, clear answer with no surrounding text.
            13. Return **only** the output in JSON format with no additional text. Do not include anything else in your response.
            14. Maintain consistent word order in your response.

                INPUT:
                [Prompt]: {prompt}

                OUTPUT FORMAT:
                Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
                {output_format_prompt_context}

                Example Output.
                {PROMPT_CONTEXT}
                """
            return template   
class DB:
    @staticmethod
    def connect():
        try:
            # Check if the environment variables are set
            if not os.getenv("DB_NAME") or not os.getenv("COSMOS_PATH"):
                raise ValueError("Environment variable DB_NAME and COSMOS_PATH must be set")
            
            myclient = pymongo.MongoClient(os.getenv("COSMOS_PATH"))

            # Check if the connection is successful
            try:
                myclient.admin.command('ismaster')
            except ConnectionFailure:
                raise ConnectionError("Could not connect to CosmosDB")

            # Connect to the database
            mydb = myclient[os.getenv("DB_NAME")]

            return mydb
        except Exception as e:
            print(str(e))
            sys.exit()
class Azure:
    def __init__(self):
        
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY") # Retrieve Azure OpenAI API key from environment variables
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") # Retrieve Azure OpenAI endpoint from environment variables
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION") # Retrieve Azure OpenAI API version from environment variables
        self.deployment_engine = os.getenv("AZURE_DEPLOYMENT_ENGINE") # Retrieve Azure OpenAI deployment engine (model) from environment variables
        
        # Initialize the AzureOpenAI client with the retrieved API key, API version, and endpoint
        self.client = openai.AzureOpenAI(
                            api_key = self.api_key, 
                            api_version = self.api_version,
                            azure_endpoint = self.azure_endpoint
                        )
        
    def generate(self, prompt, modelName=None):
        try:
            # Generate a chat completion using the AzureOpenAI client
            # The completion is based on a prompt provided by the user and a predefined system message
            if modelName is not None:
                modelName = modelName.lower()
            if modelName == "gpt-4o":
                completion = self.client.chat.completions.create(
                    model=self.deployment_engine, # Specify the model (deployment engine) to use
                    messages=[
                        {
                            "role": "system", # System message to set the context for the AI
                            "content": "You are a helpful assistant.",
                        },
                        {
                            "role": "user", # User message that contains the actual prompt
                            "content": prompt
                        }
                    ],
                    response_format={ "type": "json_object" }
                )
            else:
                completion = self.client.chat.completions.create(
                    model= self.deployment_engine, # Specify the model (deployment engine) to use
                    messages=[
                        {
                            "role": "system", # System message to set the context for the AI
                            "content": "You are a helpful assistant.",
                        },
                        {
                            "role": "user", # User message that contains the actual prompt
                            "content": prompt
                        }
                    ],
                    # response_format={ "type": "json_object" }
                )
                
            # Extract token usage information
            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens

            # Return the content of the first message from the generated completion
            return completion.choices[0].message.content, input_tokens, output_tokens
        except openai.APIConnectionError as e:
            print(f"Azure OpenAI API connection error: {e}")
            raise Exception("Azure OpenAI API connection error")
async def context_prompt(prompt: str, response: str):
        try:
            prompt_context, input_tokens, output_tokens = Azure().generate(Prompt.prompt_context(prompt))
            response_context, input_tokens, output_tokens = Azure().generate(Prompt.prompt_context(response))
            return prompt_context, response_context
        except Exception as e:
            print(e)
            raise
async def create_context(prompt: str, response: str, prompt_context: str, response_context: str):
        try:
            document = {
                "prompt": prompt,
                "response": response,
                "prompt_context": prompt_context,
                "response_context": response_context,
                "create_date": datetime.now()  
            }
            RAIExplainDB = DB.connect()
            collection = RAIExplainDB["Drift_input_records"]
            create_result = collection.insert_one(document)
            if not create_result.acknowledged:
                raise RuntimeError("Failed to insert document into the collection")
            return create_result.acknowledged
        except Exception as e:
            print(e)
            raise ValueError("Document is not a valid document")

def llm_response_to_json(response):
        """
        Converts a substring of the given response that is in JSON format into a Python dictionary.
        
        This function searches for the first occurrence of '{' and the last occurrence of '}' to find the JSON substring.
        It then attempts to parse this substring into a Python dictionary. If the parsing is successful, the dictionary
        is returned. If the substring is not valid JSON, the function will return None.
        
        Parameters:
        - response (str): The response string that potentially contains JSON content.
        
        Returns:
        - dict: A dictionary representation of the JSON substring found within the response.
        - None: If no valid JSON substring is found or if an error occurs during parsing.
        """
        try:
            result = None # Initialize result to None in case no valid JSON is found

            # Step 1: Find the start index of the first '{' character and end index of the last '}' character
            start_index = response.find('{')
            if start_index == -1:
                # If '{' is not found, load all content
                result = response
            else:
                # Step 2: Initialize a counter for curly braces
                curly_count = 0

                # Step 3: Find the corresponding closing '}' for the first '{'
                for i in range(start_index, len(response)):
                    if response[i] == '{':
                        curly_count += 1
                    elif response[i] == '}':
                        curly_count -= 1
                    
                    # When curly_count reaches 0, we have matched the opening '{' with the closing '}'
                    if curly_count == 0:
                        end_index = i
                        break
                json_content = response[start_index:end_index+1] # Extract the substring that is potentially in JSON format
                result = json.loads(json_content) # Attempt to parse the JSON substring into a Python dictionary
            
            return result
        
        except Exception as e:
            # Log the exception if any error occurs during parsing
            print(f"An error occurred while parsing JSON from response: {e}", exc_info=True)
            raise ValueError("An error occurred while parsing JSON from response.")
        
async def insertion_with_context(payload: dict):
 
        print(f"payload: {payload}")
 
        try:
           
            prompt_context, response_context = await context_prompt(prompt=payload.inputPrompt, response=payload.llmResponse)
            prompt_context_json = llm_response_to_json(prompt_context.replace("\n", " "))
            prompt_value = prompt_context_json["Context"]

            response_context_json = llm_response_to_json(response_context.replace("\n", " "))
            response_value = response_context_json["Context"]

            obj_explain = await create_context(prompt=payload.inputPrompt, response=payload.llmResponse, prompt_context = prompt_value, response_context = response_value)
            print(f"obj_explain: {obj_explain}".encode('ascii', 'ignore').decode('ascii'))
            # return InsertionStatus(response=obj_explain.get('status'), time_taken=obj_explain.get('time_taken'))
            return ContextResponse(prompt_context=prompt_value, response_context=response_value, success_status=obj_explain)
        except Exception as e:
            print(e)
            raise