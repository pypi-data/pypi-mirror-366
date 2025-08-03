import time
import requests
import json
import os
from collections import deque
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from swarmflow.core.task import Task

class SwarmFlow:
    def __init__(self):
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        span_processor = SimpleSpanProcessor(ConsoleSpanExporter())
        trace.get_tracer_provider().add_span_processor(span_processor)
        self.tracer = tracer
        self.tasks = {}
    
    def add(self, fn):
        task = fn._task
        self.tasks[task.name] = task
        return self
    
    def depends_on(self, task_name, *dependency_names):
        for dep_name in dependency_names:
            self.tasks[task_name].add_dependency(self.tasks[dep_name])
        return self

    def _topological_sort(self):
        visited = set()
        temp_stack = set()
        ordering = []

        def dfs(task):
            if task.name in temp_stack:
                # Build cycle path for better error reporting
                cycle_path = list(temp_stack) + [task.name]
                raise ValueError(f"Cycle detected in workflow: {' → '.join(cycle_path)}")
            if task.name in visited:
                return

            temp_stack.add(task.name)
            for dep in task.dependencies:
                dfs(dep)
            temp_stack.remove(task.name)
            visited.add(task.name)
            ordering.append(task)

        for task in self.tasks.values():
            if task.name not in visited:
                dfs(task)

        return ordering
    
    def run(self):
        ordered_tasks = self._topological_sort()

        for task in ordered_tasks:
            with self.tracer.start_as_current_span(task.name) as span:
                start = time.time()

                # Skip if any dependency failed
                if any(dep.status != "success" for dep in task.dependencies):
                    task.status = "skipped"
                    task.failed_due_to_dependency = True
                    task.execution_time_ms = 0
                    span.set_attribute("task.status", task.status)
                    span.set_attribute("task.output", str(task.output))
                    span.set_attribute("task.duration_ms", task.execution_time_ms)
                    self._log(task)
                    continue

                success = False
                for attempt in range(task.retries + 1):
                    try:
                        inputs = [dep.output for dep in task.dependencies]
                        # Only pass dependency inputs if the task function expects arguments
                        if task.fn.__code__.co_argcount > 0:
                            task.output = task.fn(*inputs, *task.args, **task.kwargs)
                        else:
                            task.output = task.fn(*task.args, **task.kwargs)
                        task.status = "success"
                        success = True
                        break
                    except Exception as e:
                        task.output = str(e)
                        task.status = "retrying" if attempt < task.retries else "failure"

                task.execution_time_ms = int((time.time() - start) * 1000)
                self._extract_metadata(task)
                span.set_attribute("task.status", task.status)
                span.set_attribute("task.output", str(task.output))
                span.set_attribute("task.duration_ms", task.execution_time_ms)
                self._log(task)

    def _log(self, task: Task):
        print(f"\n[SwarmFlow] Task: {task.name}")
        print(f"  ↳ Status: {task.status}")
        print(f"  ↳ Duration: {task.execution_time_ms} ms")
        print(f"  ↳ Output: {task.output}")
        if task.metadata:
            print(f"  ↳ Metadata: {task.metadata}")
            for key, value in task.metadata.items():
                print(f"    • {key}: {value}")

        # Send trace to frontend API
        trace_payload = {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "duration_ms": task.execution_time_ms,
            "output": task.output,
            "metadata": task.metadata,
            "dependencies": [dep.name for dep in task.dependencies],
        }

        try:
            # Send traces to SwarmFlow backend service
            api_url = "http://localhost:8000/api/trace"
            res = requests.post(
                api_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(trace_payload)
            )
            res.raise_for_status()
        except Exception as e:
            print(f"[SwarmFlow] ⚠️ Failed to send trace: {e}")

    def _extract_metadata(self, task: Task):
        output = task.output

        if not output:
            return

        # Handle OpenAI-style dict
        if isinstance(output, dict) and "model" in output:
            usage = output.get("usage", {})
            task.metadata.update({
                "agent": "LLMProcessor",
                "provider": "OpenAI",
                "model": output.get("model"),
                "tokens_used": usage.get("total_tokens", 0),
                "cost_usd": self._estimate_cost_openai(output.get("model"), usage)
            })

        # Handle Anthropic-style response
        elif hasattr(output, "model") and hasattr(output, "usage"):
            usage = getattr(output, "usage", {})
            task.metadata.update({
                "agent": "LLMProcessor",
                "provider": "Anthropic",
                "model": getattr(output, "model", None),
                "tokens_used": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                "cost_usd": self._estimate_cost_anthropic(getattr(output, "model", ""), usage)
            })

        # Add more LLM provider detections here (Groq, Mistral, etc.)

    def _estimate_cost_openai(self, model, usage):
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = input_tokens + output_tokens

        if "gpt-4" in model:
            return round((input_tokens * 0.03 + output_tokens * 0.06) / 1000, 4)
        elif "gpt-3.5" in model:
            return round(total_tokens * 0.0015 / 1000, 4)
        return 0.0

    def _estimate_cost_anthropic(self, model, usage):
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        # Replace with real pricing later
        return round((input_tokens + output_tokens) * 0.00002, 4)