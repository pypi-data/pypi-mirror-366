from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from mindor.dsl.schema.component import ModelComponentConfig
from mindor.dsl.schema.action import ModelActionConfig, SummarizationModelActionConfig
from mindor.core.logger import logging
from ..base import ModelTaskService, ModelTaskType, register_model_task_service
from ..base import ComponentActionContext
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer, GenerationMixin
import torch

class SummarizationTaskAction:
    def __init__(self, config: SummarizationModelActionConfig, model: Union[PreTrainedModel, GenerationMixin], tokenizer: PreTrainedTokenizer):
        self.config: SummarizationModelActionConfig = config
        self.model: Union[PreTrainedModel, GenerationMixin] = model
        self.tokenizer: PreTrainedTokenizer = tokenizer

    async def run(self, context: ComponentActionContext) -> Any:
        text: Union[str, List[str]] = await context.render_variable(self.config.text)

        max_input_length  = await context.render_variable(self.config.params.max_input_length)
        max_output_length = await context.render_variable(self.config.params.max_output_length)
        min_output_length = await context.render_variable(self.config.params.min_output_length)
        num_beams         = await context.render_variable(self.config.params.num_beams)
        length_penalty    = await context.render_variable(self.config.params.length_penalty)
        early_stopping    = await context.render_variable(self.config.params.early_stopping)
        do_sample         = await context.render_variable(self.config.params.do_sample)
        batch_size        = await context.render_variable(self.config.params.batch_size)

        texts: List[str] = [ text ] if isinstance(text, str) else text
        results = []

        for index in range(0, len(texts), batch_size):
            batch_texts = texts[index:index + batch_size]
            inputs = self.tokenizer(batch_texts, return_tensors="pt", max_length=max_input_length, padding=True, truncation=True).to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_output_length,
                    min_length=min_output_length,
                    num_beams=num_beams,
                    length_penalty=length_penalty,
                    early_stopping=early_stopping,
                    do_sample=do_sample,
                    pad_token_id=getattr(self.tokenizer, "pad_token_id", None),
                    eos_token_id=getattr(self.tokenizer, "eos_token_id", None)
                )

            outputs = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
            results.extend(outputs)
        
        result = results if len(results) > 1 else results[0]
        context.register_source("result", result)

        return (await context.render_variable(self.config.output, ignore_files=True)) if self.config.output else result

@register_model_task_service(ModelTaskType.SUMMARIZATION)
class SummarizationTaskService(ModelTaskService):
    def __init__(self, id: str, config: ModelComponentConfig, daemon: bool):
        super().__init__(id, config, daemon)

        self.model: Optional[Union[PreTrainedModel, GenerationMixin]] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None

    async def _serve(self) -> None:
        try:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.config.model).to(torch.device(self.config.device))
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model, use_fast=self.config.fast_tokenizer)
            logging.info(f"Model and tokenizer loaded successfully on device '{self.config.device}': {self.config.model}")
        except Exception as e:
            logging.error(f"Failed to load model '{self.config.model}': {e}")
            raise

    async def _shutdown(self) -> None:
        self.model = None
        self.tokenizer = None

    async def _run(self, action: ModelActionConfig, context: ComponentActionContext) -> Any:
        return await SummarizationTaskAction(action, self.model, self.tokenizer).run(context)
