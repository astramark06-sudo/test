"""Optional LangGraph StateGraph adapter; the core runner has no LangGraph dependency."""
from typing import Any, Callable

def build_langgraph(steps: list[tuple[str, Callable[[dict[str, Any]], dict[str, Any]]]], checkpointer: Any = None) -> Any:
    try: from langgraph.graph import END, START, StateGraph
    except ImportError as exc: raise RuntimeError("Install with pip install -e '.[agents]'") from exc
    graph = StateGraph(dict)
    for name, handler in steps:
        def node(state: dict[str, Any], _handler=handler, _name=name) -> dict[str, Any]:
            output = _handler(dict(state))
            if not isinstance(output,dict): raise TypeError(f"Node {_name} must return a dict")
            return output
        graph.add_node(name,node)
    if not steps:
        graph.add_node("noop",lambda state: {}); graph.add_edge(START,"noop"); graph.add_edge("noop",END)
    else:
        graph.add_edge(START,steps[0][0])
        for left,right in zip(steps,steps[1:]): graph.add_edge(left[0],right[0])
        graph.add_edge(steps[-1][0],END)
    return graph.compile(checkpointer=checkpointer)
