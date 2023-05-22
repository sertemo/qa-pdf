#Pipeline para los Modelos de Huggingface
#Notebook : https://colab.research.google.com/drive/1apdUEHhJrVapavJPNnQIVl5UyNfBnss0?usp=sharing#scrollTo=_38HzUkvIewb

from transformers import LlamaTokenizer, LlamaForCausalLM, pipeline
import torch

tokenizer = LlamaTokenizer.from_pretrained("TheBloke/wizardLM-7B-HF")

model = LlamaForCausalLM.from_pretrained("TheBloke/wizardLM-7B-HF",
                                              load_in_8bit=True,
                                              device_map='auto',
                                              torch_dtype=torch.float16,
                                              low_cpu_mem_usage=True
                                              )

pipe = pipeline(
    "text-generation",
    model=model, 
    tokenizer=tokenizer, 
    max_length=1024,
    temperature=0,
    top_p=0.95,
    repetition_penalty=1.15
)


