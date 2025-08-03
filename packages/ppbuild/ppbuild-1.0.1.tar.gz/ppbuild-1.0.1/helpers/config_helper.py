from typing import Optional

from commands.base_command import CommandContext


class ContextHelper:
    context: CommandContext

    def __init__(self, context: CommandContext):
        self.context = context

    def get_app_config(self, key: str):
        return self.context.config.get("applications").get(key)

    def get_context_args(self, key: str):
        return self.context.args.get(key)

    def get_action_name(self) -> Optional[str]:
        return getattr(self.context.args, "action", None)

    def get_default_action_name(self) -> str:
        return self.context.config.get("default_action")
