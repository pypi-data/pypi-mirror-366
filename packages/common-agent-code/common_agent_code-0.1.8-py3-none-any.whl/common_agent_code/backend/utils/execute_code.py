from common_agent_code.backend.utils.OutputCapture import OutputCapture
from common_agent_code.backend.utils.AgentState import AgentState
from common_agent_code.backend.utils.ExecutionResult import ExecutionResult
import traceback

def execute_code(code: str, state: AgentState) -> ExecutionResult:
    import os
    import uuid
    import json
    import matplotlib.pyplot as plt
    import textwrap

    plot_save_code = textwrap.dedent("""
    import os
    import matplotlib.pyplot as plt
    import uuid

    static_dir = os.path.join(os.getcwd(), "backend", "static")
    os.makedirs(static_dir, exist_ok=True)
    plot_path = os.path.join(static_dir, f"plot_{uuid.uuid4()}.png")
    web_path = f"/static/{os.path.basename(plot_path)}"
    plt.savefig(plot_path)
    returned_objects.setdefault("plot_paths", []).append(web_path)
    plt.close()
    """)

    code = code.replace("plt.show()", plot_save_code)

    if not code.strip():
        return ExecutionResult(output="No code to execute", returned_objects={})

    shared_env = state.data.copy()
    returned_objects = {}
    shared_env["returned_objects"] = returned_objects

    with OutputCapture() as output:
        try:
            if "\n" not in code and not code.strip().endswith(":"):
                result = eval(code, shared_env, shared_env)
                if result is not None:
                    returned_objects["result"] = str(result)
            else:
                exec(code, shared_env, shared_env)
                for k, v in shared_env.items():
                    if k not in state.data and k not in ["returned_objects"]:
                        returned_objects[k] = v

            # Catch plots that didn’t use plt.show()
            if plt.get_fignums():
                fallback_path = f"static/plot_{uuid.uuid4()}.png"
                os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
                plt.savefig(fallback_path)
                plt.close()
                returned_objects.setdefault("plot_paths", []).append("/" + fallback_path)

            # Update shared state with serializable values
            for key, value in shared_env.items():
                if key not in state.data or state.data[key] is not value:
                    try:
                        json.dumps(value, default=str)
                        state.data[key] = value
                    except (TypeError, ValueError):
                        continue

            return ExecutionResult(
                output=output.stdout.getvalue(),
                error=None,
                traceback=None,
                returned_objects=returned_objects
            )

        except Exception as e:
            return ExecutionResult(
                output=output.stdout.getvalue(),
                error=str(e),
                traceback=traceback.format_exc(),
                returned_objects=returned_objects
            )

