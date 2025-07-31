from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Callable, Awaitable, Any
from mindor.dsl.schema.workflow import WorkflowVariableConfig, WorkflowVariableGroupConfig, WorkflowVariableType, WorkflowVariableFormat
from mindor.core.workflow.schema import WorkflowSchema
from mindor.core.utils.streaming import StreamResource, Base64StreamResource
from mindor.core.utils.streaming import save_stream_to_temporary_file
from mindor.core.utils.http_request import create_upload_file
from mindor.core.utils.http_client import create_stream_with_url
from mindor.core.utils.image import load_image_from_stream
import gradio as gr
import json

class ComponentGroup:
    def __init__(self, group: gr.Component, components: List[gr.Component]):
        self.group: gr.Component = group
        self.components: List[gr.Component] = components

class GradioWebUIBuilder:
    def build(self, schema: Dict[str, WorkflowSchema], runner: Callable[[Optional[str], Any], Awaitable[Any]]) -> gr.Blocks:
        with gr.Blocks() as blocks:
            for workflow_id, workflow in schema.items():
                async def _run_workflow(input: Any, workflow_id=workflow_id) -> Any:
                    return await runner(workflow_id, input)

                if len(schema) > 1:
                    with gr.Tab(label=workflow.name or workflow_id):
                        self._build_workflow_section(workflow, _run_workflow)
                else:
                    self._build_workflow_section(workflow, _run_workflow)

        return blocks

    def _build_workflow_section(self, workflow: WorkflowSchema, runner: Callable[[Any], Awaitable[Any]]) -> gr.Column:
        with gr.Column() as section:
            gr.Markdown(f"## **{workflow.title or 'Untitled Workflow'}**")
 
            if workflow.description:
                gr.Markdown(f"📝 {workflow.description}")

            gr.Markdown("#### 📥 Input Parameters")
            input_components = [ self._build_input_component(variable) for variable in workflow.input ]
            run_button = gr.Button("🚀 Run Workflow", variant="primary")

            gr.Markdown("#### 📤 Output Values")
            output_components = [ self._build_output_component(variable) for variable in workflow.output ]

            if not output_components:
                output_components = [ gr.Textbox(label="", lines=8, interactive=False, show_copy_button=True) ]

            async def _run_workflow(*args):
                input = await self._build_input_value(args, workflow.input)
                output = await runner(input)
                if workflow.output:
                    output = await self._flatten_output_value(output, workflow.output)
                return output[0] if len(output) == 1 else output

            run_button.click(
                fn=_run_workflow,
                inputs=input_components,
                outputs=self._flatten_output_components(output_components)
            )

        return section

    def _build_input_component(self, variable: WorkflowVariableConfig) -> gr.Component:
        label = (variable.name or "") + (" *" if variable.required else "") + (f" (default: {variable.default})" if variable.default else "")
        info = variable.get_annotation_value("description") or ""
        default = variable.default

        if variable.type == WorkflowVariableType.STRING or variable.format in [ WorkflowVariableFormat.BASE64, WorkflowVariableFormat.URL ]:
            return gr.Textbox(label=label, value="", info=info)

        if variable.type in [ WorkflowVariableType.INTEGER, WorkflowVariableType.NUMBER ]:
            return gr.Number(label=label, value="", info=info)

        if variable.type == WorkflowVariableType.BOOLEAN:
            return gr.Checkbox(label=label, value=default or False, info=info)
        
        if variable.type == WorkflowVariableType.IMAGE:
            return gr.Image(label=label, type="filepath")

        if variable.type == WorkflowVariableType.AUDIO:
            return gr.Audio(label=label, type="filepath")

        if variable.type == WorkflowVariableType.VIDEO:
            return gr.Video(label=label, type="filepath")

        if variable.type == WorkflowVariableType.FILE:
            return gr.File(label=label)

        if variable.type == WorkflowVariableType.SELECT:
            return gr.Dropdown(choices=variable.options or [], label=label, value=default, info=info)

        return gr.Textbox(label=label, value=default, info=f"Unsupported type: {variable.type}")
    
    async def _build_input_value(self, arguments: List[Any], variables: List[WorkflowVariableConfig]) -> Any:
        if len(variables) == 1 and not variables[0].name:
            value, variable = arguments[0], variables[0]
            return await self._convert_input_value(value, variable.type, variable.subtype, variable.format, variable.internal)

        input: Dict[str, Any] = {}
        for value, variable in zip(arguments, variables):
            input[variable.name] = await self._convert_input_value(value, variable.type, variable.subtype, variable.format, variable.internal)
        return input

    async def _convert_input_value(self, value: Any, type: WorkflowVariableType, subtype: Optional[str], format: Optional[WorkflowVariableFormat], internal: bool) -> Any:
        if type in [ WorkflowVariableType.IMAGE, WorkflowVariableType.AUDIO, WorkflowVariableType.VIDEO, WorkflowVariableType.FILE ] and (not internal or not format):
            if internal and format and format != "path":
                value = await self._save_value_to_temporary_file(value, subtype, format)
            return create_upload_file(value, type.value, subtype) if value is not None else None

        return value if value != "" else None

    def _build_output_component(self, variable: Union[WorkflowVariableConfig, WorkflowVariableGroupConfig]) -> Union[gr.Component, List[ComponentGroup]]:
        if isinstance(variable, WorkflowVariableGroupConfig):
            groups: List[ComponentGroup] = []
            for index in range(variable.repeat_count if variable.repeat_count != 0 else 100):
                visible = True if variable.repeat_count != 0 or index == 0 else False
                with gr.Column(visible=visible) as group:
                    components = [ self._build_output_component(v) for v in variable.variables ]
                groups.append(ComponentGroup(group, components))
            return groups

        label = variable.name or ""
        info = variable.get_annotation_value("description") or ""

        if variable.type in [ WorkflowVariableType.STRING, WorkflowVariableType.BASE64 ]:
            return gr.Textbox(label=label, interactive=False, show_copy_button=True, info=info)

        if variable.type == WorkflowVariableType.MARKDOWN:
            return gr.Markdown(label=label)
        
        if variable.type in [ WorkflowVariableType.JSON, WorkflowVariableType.OBJECTS ]:
            return gr.JSON(label=label)

        if variable.type == WorkflowVariableType.IMAGE:
            return gr.Image(label=label, interactive=False)

        if variable.type == WorkflowVariableType.AUDIO:
            return gr.Audio(label=label)

        if variable.type == WorkflowVariableType.VIDEO:
            return gr.Video(label=label)

        return gr.Textbox(label=label, info=f"Unsupported type: {variable.type}")

    def _flatten_output_components(self, components: List[Union[gr.Component, List[ComponentGroup]]]) -> List[gr.Component]:
        flattened = []
        for item in components:
            if isinstance(item, list):
                for group in item:
                    flattened.extend(group.components)
            else:
                flattened.append(item)
        return flattened
    
    async def _flatten_output_value(self, output: Any, variables: List[Union[WorkflowVariableConfig, WorkflowVariableGroupConfig]]) -> Any:
        flattened = []
        for variable in variables:
            if isinstance(variable, WorkflowVariableGroupConfig):
                group = output[variable.name] if variable.name in output else None if variable.name else output
                for value in group or ():
                    flattened.extend(await self._flatten_output_value(value, variable.variables))
            else:
                value = output[variable.name] if variable.name in output else None if variable.name else output
                flattened.append(await self._convert_output_value(value, variable.type, variable.subtype, variable.format, variable.internal))
        return flattened

    async def _convert_output_value(self, value: Any, type: WorkflowVariableType, subtype: Optional[str], format: Optional[WorkflowVariableFormat], internal: bool) -> Any:
        if type == WorkflowVariableType.STRING:
            return json.dumps(value) if isinstance(value, (dict, list)) else str(value) if value is not None else None

        if type == WorkflowVariableType.IMAGE:
            return await self._load_image_from_value(value, subtype, format)

        if type in [ WorkflowVariableType.AUDIO, WorkflowVariableType.VIDEO ]:
            return await self._save_value_to_temporary_file(value, subtype, format)

        return value

    async def _load_image_from_value(self, value: Any, subtype: Optional[str], format: Optional[WorkflowVariableFormat]) -> Optional[str]:
        if format == WorkflowVariableFormat.BASE64 and isinstance(value, str):
            return await load_image_from_stream(Base64StreamResource(value), subtype)

        if format == WorkflowVariableFormat.URL and isinstance(value, str):
            return await load_image_from_stream(await create_stream_with_url(value), subtype)

        if isinstance(value, StreamResource):
            return await load_image_from_stream(value, subtype)

        return None

    async def _save_value_to_temporary_file(self, value: Any, subtype: Optional[str], format: Optional[WorkflowVariableFormat]) -> Optional[str]:
        if format == WorkflowVariableFormat.BASE64 and isinstance(value, str):
            return await save_stream_to_temporary_file(Base64StreamResource(value), subtype)

        if format == WorkflowVariableFormat.URL and isinstance(value, str):
            return await save_stream_to_temporary_file(await create_stream_with_url(value), subtype)

        if isinstance(value, StreamResource):
            return await save_stream_to_temporary_file(value, subtype)

        return None
