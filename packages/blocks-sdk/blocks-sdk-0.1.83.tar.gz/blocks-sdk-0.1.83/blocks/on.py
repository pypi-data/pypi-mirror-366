import contextlib
import inspect

from .state import BlocksState
from .base import BaseTaskDecorator

class OnClass(BaseTaskDecorator):

    def __init__(self, func, state: BlocksState):
        super().__init__(func, state)

    @staticmethod
    def get_decorator(state: BlocksState):
        def set_trigger(func, trigger_alias=None, trigger_kwargs=None):
            new_trigger = OnClass(func, state)
            trigger_kwargs = trigger_kwargs or {}

            is_function_already_wrapped_in_decorator = False

            # Check if the function is already wrapped in a decorator
            with contextlib.suppress(AttributeError):
                if func.task_metadata:
                    function_name = func.task_metadata.get("function_name")
                    parent_type = func.task_metadata.get("type")
                    function_source_code = func.task_metadata.get("function_source_code")
                    function_arg_count = func.task_metadata.get("function_arg_count")
                    task_kwargs = func.task_metadata.get("task_kwargs")
                    config_schema = func.task_metadata.get("config_schema")
                    config_class = func.task_metadata.get("config_class")

                    
                    state.automations.append({
                        "trigger_alias": trigger_alias,
                        "function_name": function_name,
                        "function_source_code": function_source_code,
                        "function_arg_count": function_arg_count,
                        "config_schema": config_schema,
                        "config_class": config_class,
                        "parent_type": parent_type,
                        "trigger_kwargs": trigger_kwargs,
                        "task_kwargs": task_kwargs,
                    })

                    is_function_already_wrapped_in_decorator = True
            
            if not is_function_already_wrapped_in_decorator:
                config_class = new_trigger.get_config_class()
                config_schema = new_trigger.get_config_schema() 
                function_arg_count = new_trigger.get_function_arg_count()
                func.trigger_metadata = {
                    "type": "trigger",
                    "trigger_alias": trigger_alias,
                    "function_name": new_trigger.name,
                    "function_source_code": new_trigger.source_code,
                    "function_arg_count": function_arg_count,
                    "trigger_kwargs": trigger_kwargs,
                    "config_schema": config_schema,
                    "config_class": config_class
                }
            
            return func

        def decorator(*decorator_args, **decorator_kwargs):
            # If decorator is used without parentheses
            if len(decorator_args) == 1 and callable(decorator_args[0]) and not decorator_kwargs:
                return set_trigger(decorator_args[0])
            
            # If decorator is used with parentheses
            def wrapper(func):
                return set_trigger(func, decorator_args[0] if decorator_args else None, decorator_kwargs)
            return wrapper
            
        decorator.blocks_state = state
        return decorator
