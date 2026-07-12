"""Execute ActionArc Arcs."""

from actionarc.components.registry import ComponentRegistry
from actionarc.engine.context import RunContext
from actionarc.engine.results import ActionResult, ArcRunResult, ArcRunStatus, TriggerResult
from actionarc.models import Arc


class ArcRunner:
    """Coordinates the execution of a single Arc."""

    def __init__(self, registry: ComponentRegistry):
        self.registry = registry

    def run(self, arc: Arc) -> ArcRunResult:
        context = RunContext(arc_id=arc.id)

        try:
            trigger = self.registry.create_trigger(arc.trigger.type, arc.trigger.config)
            trigger_result = trigger.evaluate(context)
        except Exception as error:
            trigger_result = TriggerResult(matched=False, message=f"Trigger failed: {error}")
            return ArcRunResult(arc_id=arc.id, status=ArcRunStatus.FAILED, trigger=trigger_result)

        if not trigger_result.matched:
            return ArcRunResult(arc_id=arc.id, status=ArcRunStatus.NOT_TRIGGERED, trigger=trigger_result)

        context.data.update(trigger_result.data)
        action_results: list[ActionResult] = []

        for action_definition in arc.actions:
            try:
                action = self.registry.create_action(action_definition.type, action_definition.config)
                result = action.execute(context)
            except Exception as error:
                result = ActionResult(succeeded=False, message=f"Action failed: {error}")

            action_results.append(result)

            if not result.succeeded:
                return ArcRunResult(
                    arc_id=arc.id,
                    status=ArcRunStatus.FAILED,
                    trigger=trigger_result,
                    actions=action_results,
                )

            context.data.update(result.data)

        return ArcRunResult(
            arc_id=arc.id,
            status=ArcRunStatus.SUCCEEDED,
            trigger=trigger_result,
            actions=action_results,
        )