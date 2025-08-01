import ast

from ..core import task_manager
from ..aient.src.aient.plugins import register_tool, registry

worker_fun = registry.tools["worker"]

@register_tool()
def create_task(goal, tools, work_dir):
    """
    启动一个子任务来自动完成指定的任务目标 (`goal`)。

    这个子任务接收一个清晰的任务描述、一组可供调用的工具 (`tools`)，以及一个工作目录 (`work_dir`)。
    它会结合可用的工具，自主规划并逐步执行必要的操作，直到最终完成指定的任务目标。
    核心功能是根据输入的目标，驱动整个任务执行流程。
    子任务下上文为空，因此需要细致的背景信息。

    Args:
        goal (str): 需要完成的具体任务目标描述。子任务将围绕此目标进行工作。必须清晰、具体。必须包含背景信息，完成指标等。写清楚什么时候算任务完成，同时交代清楚任务的背景信息，这个背景信息可以是需要读取的文件等一切有助于完成任务的信息。
        tools (list[str]): 一个包含可用工具函数对象的列表。子任务在执行任务时可能会调用这些工具来与环境交互（例如读写文件、执行命令等）。
        work_dir (str): 工作目录的绝对路径。子任务将在此目录上下文中执行操作。子任务的工作目录位置在主任务的工作目录的子目录。子任务工作目录**禁止**设置为主任务目录本身。

    Returns:
        str: 当任务成功完成时，返回字符串 "任务已完成"。
    """
    tasks_params = [
        {"goal": goal, "tools": ast.literal_eval(tools), "work_dir": work_dir, "cache_messages": True}
    ]
    task_ids = task_manager.create_tasks(worker_fun, tasks_params)
    return task_ids

@register_tool()
def resume_task(task_id, goal):
    """
    恢复一个子任务。
    """
    if task_id not in task_manager.tasks_cache:
        return f"任务 {task_id} 不存在"
    tasks_params = task_manager.tasks_cache[task_id]["args"]
    tasks_params["goal"] = goal
    tasks_params["cache_messages"] = True
    task_id = task_manager.resume_task(task_id, worker_fun, tasks_params)
    return f"任务 {task_id} 已恢复"

@register_tool()
def get_all_tasks_status():
    """
    获取所有任务的状态。
    子任务状态会持久化到磁盘，因此即使历史记录为空，之前的子任务仍然存在。

    Returns:
        str: 所有任务的状态。每个任务的id，状态，结果。
    """
    return task_manager.tasks_cache

@register_tool()
async def get_task_result():
    """
    等待并获取子任务的执行结果。如果需要等待子任务完成，请使用这个工具。一旦有任务完成，会自动获取结果。如果调用时没有任务完成，会等待直到有任务完成。

    Returns:
        str: 子任务的执行结果。
    """
    running_tasks_num = len([task_id for task_id, task in task_manager.tasks_cache.items() if task_id != "root_path" and task.get("status") == "RUNNING"])
    if running_tasks_num == 0:
        return "All tasks are finished."
    task_id, status, result = await task_manager.get_next_result()

    unfinished_tasks = [task_id for task_id, task in task_manager.tasks_cache.items() if task_id != "root_path" and task.get("status") != "DONE"]
    text = "".join([
        f"Task ID: {task_id}\n",
        f"Status: {status.value}\n",
        f"Result: {result}\n\n",
        f"There are {len(unfinished_tasks)} unfinished tasks, unfinished task ids: {unfinished_tasks}" if unfinished_tasks else "All tasks are finished.",
    ])

    return text