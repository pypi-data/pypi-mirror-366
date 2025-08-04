from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, pipeline
import os
from dotenv import load_dotenv
from huggingface_hub import login
from openai import OpenAI
import pynvml
import re

from .logger import logger, log_progress
from .agent import _Agent

class _ModelWrapper:
    """
    This is a class used to contain and abstract the usage of a given llm for inference_tree.
    With this class, a user can pass agent prompts to either a local huggingface model OR the
    OpenAI API, without any additional tweaks outside of initialization.

    Methods:
        _get_gpu_with_most_free_memory(): If there is more than one gpu, finds the one with the most free
                                         memory and returns its id as a string.
        generate(input, agent): takes the arguement "input", and passes it to the model for processing before
                                returning the model output.  Make sure to use the agent class's form_prompt()
                                function on an input to get it in the right format before passing.
    
    Args:
        model_name: The reference name for the model.  Example: "meta-llama/Llama-3.2-3B-Instruct" for
                    huggingface, or "gpt-4o" for an OpenAI API call.
        model_origin: Defines whether the model in question comes from huggingface(pass in "hf") or 
                      OpenAI(pass in "openai").
        model_params: Takes a dictionary of hyperparameters and directly applies them to the model.
                      Design this dictionary the same way as if you were calling the given llm directly.
    """

    def __init__(self, model_name: str, model_origin: str, model_params: dict = None):
        self.model_origin = model_origin     

        load_dotenv()
        best_gpu = self._get_gpu_with_most_free_memory()
        if best_gpu is not None: os.environ["CUDA_VISIBLE_DEVICES"] = best_gpu
        os.environ["TORCH_USE_CUDA_DSA"] = "1"
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True" 
        
        #sets the llm that will be used by the other functions, and exposes it as an accessible variable
        if model_origin == "hf":
            #This code runs if the llm is from huggingface.co or a local huggingface model
            try:
                key = os.getenv('token')
                # user = os.getenv('username')
                login(key)
            except:
                raise KeyError("Login with token failed!  Make sure to set your huggingface login key under 'token' in your .env!")

            #save the user-defined model hyperparameters to an AutoConfig object, then initialize the model into a global variable
            config = AutoConfig.from_pretrained(model_name, **model_params)
            automodel = AutoModelForCausalLM.from_pretrained(model_name, config=config)
            autotokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = pipeline("text-generation", model=automodel, tokenizer=autotokenizer, pad_token_id = autotokenizer.eos_token_id)
        elif model_origin == "openai":
            #This code runs if the llm is accessed throught the openai api
            self.model = {
                "model": model_name,
                "config": model_params
            }
        else: 
            logger.error("model origin selected incorrectly, failed to load model")
            #raise TypeError(f"model_origin of '{model_origin}' incorrect, must be 'hf', 'openai'")

    def _get_gpu_with_most_free_memory(self):
        """returns the id of the gpu with the most unused memory"""
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            free_memories = []

            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                free_memories.append((i, mem_info.free))

            pynvml.nvmlShutdown()

            # Sort by most free memory (descending)
            best_gpu = sorted(free_memories, key=lambda x: x[1], reverse=True)[0][0]
            return str(best_gpu)
        except:
            logger.info("No CUDA device found, skipping device finding function.")
            return None

    def generate(self, input: str, agent: _Agent):
        """
        This function handles passing prompts to a given model, and abstracts away the complexities of tokenization
        and the like.  It is very important that any customization of the output formatting is done within this function.

        Args:
        input -- contains the input text to be formatted by the agent
        agent -- passes in the agent so it can apply a question to the input text to make a full prompt.

        Returns:
        response -- Ultimately a single string, execution will vary by model_origin parameter.
        """
        if input == '':
            raise ValueError("Text input was found to be empty when constructing prompt!")
        formatted_input = agent.form_prompt(input)

        if self.model_origin == "hf":
            response = self.model(formatted_input, return_full_text=False)[0]["generated_text"]
            log_progress.info(f"Prompt: {formatted_input} GAVE OUTPUT {response}")
            
            if re.match(r".*\btext\b(?:\s+\b\w+\b){0,5}\s+\bsummarize\b.*", response):
                logger.error(f"An empty input was detected by the LLM in the following entry: '{input}.'  The response the model gave was: '{response}.'")

            return response
        elif self.model_origin == "openai":
                client = OpenAI(
                    api_key = os.getenv('OPENAI_API_KEY')
                )

                response = client.responses.create(
                    model=self.model["model"],
                    input=formatted_input,
                    store=False,
                    **self.model["config"]
                )

                logger.info(f"Prompt: {formatted_input} GAVE OUTPUT {response.output_text}")
                return response.output_text
        else:
            logger.error("model failed generation step")
            raise RuntimeError("Model generation failed due to unrecognized model_origin.")