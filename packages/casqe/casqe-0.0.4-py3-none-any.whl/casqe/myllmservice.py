# here is myllmservice.py


import logging


logger = logging.getLogger(__name__)
import asyncio
from llmservice.base_service import BaseLLMService
from llmservice.generation_engine import GenerationRequest, GenerationResult
from typing import Optional, Union

from  casqe import prompts





class MyLLMService(BaseLLMService):
    def __init__(self, logger=None, max_concurrent_requests=200):
        super().__init__(
            logger=logging.getLogger(__name__),
            default_model_name="gpt-4o",
            # default_model_name="gpt-4.1-nano",
            max_rpm=500,
            max_concurrent_requests=max_concurrent_requests,
        )
        # No need for a semaphore here, it's handled in BaseLLMService
    
    def ask_llm_to_enrich(self, input_object, model=None) -> GenerationResult:
        

        if input_object.use_thinking:
            model="o3"


        user_prompt = prompts.ASK_LLM_TO_ENRICH_PROMPT.format(
            query=input_object.query,
            search_reason_context=input_object.search_reason_context,
            identifier_context=input_object.identifier_context,
            text_rules= input_object.text_rules,
            how_many_advanced =input_object.how_many_advanced
        )


        pipeline_config = [
        
            {
                'type': 'ConvertToDict',
                'params': {}
            },
           
        ]

        if model is None:
            model= "gpt-4o"
        
        generation_request = GenerationRequest(
            
            user_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="categorize_simple",
            pipeline_config= pipeline_config,
        
        )

      
        generation_result = self.execute_generation(generation_request)

        return generation_result
    


    def async_ask_llm_to_enrich(self, input_object, model=None) -> GenerationResult:
        

        if input_object.use_thinking:
            model="o3"

        
        user_prompt = prompts.ASK_LLM_TO_ENRICH_PROMPT.format(
            query=input_object.query,
            search_reason_context=input_object.search_reason_context,
            identifier_context=input_object.identifier_context,
            text_rules= input_object.text_rules,
            how_many_advanced =input_object.how_many_advanced
        )


        
        pipeline_config = [
        
            {
                'type': 'ConvertToDict',
                'params': {}
            },
           
        ]

        if model is None:
            model= "gpt-4o"
        
        generation_request = GenerationRequest(
            
            user_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="categorize_simple",
            pipeline_config= pipeline_config,
        
        )

      
        generation_result = self.execute_generation_async(generation_request)

        return generation_result
    
    


     
    def ask_llm_to_generate_platforms_and_entitiy_lists(self, input_object, model=None) -> GenerationResult:
        

      
        if input_object.use_thinking:
            model="o3"


        user_prompt = prompts.ASK_LLM_TO_GENERATE_PLATFORMS_PROMPT.format(
            query=input_object.query,
            search_reason_context=input_object.search_reason_context,
            identifier_context=input_object.identifier_context,
            text_rules= input_object.text_rules,
        
        )



        



        
        pipeline_config = [
           
            {
                'type': 'ConvertToDict',
                'params': {}
            },
          
        ]

        if model is None:
            model= "gpt-4o"
    
        
        generation_request = GenerationRequest(
            
            user_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="categorize_simple",
            pipeline_config= pipeline_config,
         
        )

      

        generation_result = self.execute_generation(generation_request)

        return generation_result
    


    def async_ask_llm_to_generate_platforms_and_entitiy_lists(self, input_object, model=None) -> GenerationResult:
        

      
        if input_object.use_thinking:
            model="o3"



        user_prompt = prompts.ASK_LLM_TO_GENERATE_PLATFORMS_PROMPT.format(
            query=input_object.query,
            search_reason_context=input_object.search_reason_context,
            identifier_context=input_object.identifier_context,
            text_rules= input_object.text_rules,
        
        )


        
        pipeline_config = [
           
            {
                'type': 'ConvertToDict',
                'params': {}
            },
          
        ]

        if model is None:
            model= "gpt-4o"
        

        
        generation_request = GenerationRequest(
            
            user_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="categorize_simple",
            pipeline_config= pipeline_config,
         
        )

      

        generation_result = self.execute_generation_async(generation_request)

        return generation_result




def main():
    """
    Main function to test the categorize_simple method of MyLLMService.
    """
    # Initialize the service
    my_llm_service = MyLLMService()

    # Sample data for testing
    sample_search_title_and_metadescription = "BAV99 Fast Switching Speed. • Surface-Mount Package Ideally Suited for Automated Insertion. • For General-Purpose Switching Applications."
   
   
    try:
        # Perform categorization
        result = my_llm_service.categorize_simple(
            semantic_filter_text=sample_search_title_and_metadescription,
    
        )

        # Print the result
        print("Generation Result:", result)
        if result.success:
            print("Filtered Content:", result.content)
        else:
            print("Error:", result.error_message)
    except Exception as e:
        print(f"An exception occurred: {e}")


if __name__ == "__main__":
    main()
