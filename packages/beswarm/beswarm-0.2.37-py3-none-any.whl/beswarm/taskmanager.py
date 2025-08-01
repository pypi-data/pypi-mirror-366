import json
import uuid
import asyncio
from enum import Enum
from pathlib import Path

from .aient.src.aient.plugins import registry

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"
    NOT_FOUND = "NOT_FOUND"


class TaskManager:
    """一个简单的异步任务管理器"""
    def __init__(self):
        self.tasks = {}  # 使用字典来存储任务，key是task_id, value是task对象
        self.results_queue = asyncio.Queue()
        self.root_path = None
        self.tasks_cache = {}

    def set_root_path(self, root_path):
        if self.root_path:
            return
        self.root_path = Path(root_path)
        self.cache_dir = self.root_path / ".beswarm"
        self.task_cache_file = self.cache_dir / "tasks.json"
        self.task_cache_file.touch(exist_ok=True)
        self.read_tasks_cache()
        self.set_task_cache("root_path", str(self.root_path))
        self.resume_all_running_task()

    def set_task_cache(self, *keys_and_value):
        """
        设置可嵌套的任务缓存。
        接受无限个键和一个值，例如 set_task_cache('a', 'b', 'c', value)
        会转换为 tasks_cache['a']['b']['c'] = value
        """
        if len(keys_and_value) < 2:
            return  # 至少需要一个键和一个值

        keys = keys_and_value[:-1]
        value = keys_and_value[-1]

        d = self.tasks_cache
        # 遍历到倒数第二个键，确保路径存在
        for key in keys[:-1]:
            d = d.setdefault(key, {})

        # 在最后一个键上设置值
        d[keys[-1]] = value
        self.save_tasks_cache()

    def save_tasks_cache(self):
        self.task_cache_file.write_text(json.dumps(self.tasks_cache, ensure_ascii=False, indent=4), encoding="utf-8")

    def read_tasks_cache(self):
        content = self.task_cache_file.read_text(encoding="utf-8")
        try:
            self.tasks_cache = json.loads(content) if content else {}
        except json.JSONDecodeError:
            raise ValueError("任务缓存文件格式错误")

    def create_tasks(self, task_coro, tasks_params):
        """
        批量创建并注册任务。

        Args:
            task_coro: 用于创建任务的协程函数。
            tasks_params (list): 包含任务参数的列表。

        Returns:
            list: 创建的任务ID列表。
        """
        task_ids = []
        for args in tasks_params:
            coro = task_coro(**args)
            task_id = self.create_task(coro)
            task_ids.append(task_id)
            self.set_task_cache(task_id, "args", args)
            self.set_task_cache(task_id, "status", TaskStatus.RUNNING.value)
        return task_ids

    def resume_all_running_task(self):
        running_task_id_list = [task_id for task_id, task in self.tasks_cache.items() if task_id != "root_path" and task.get("status") == "RUNNING"]
        for task_id in running_task_id_list:
            tasks_params = self.tasks_cache[task_id]["args"]
            task_id = self.resume_task(task_id, registry.tools["worker"], tasks_params)

    def resume_task(self, task_id, task_coro, args):
        """
        恢复一个任务。
        """
        task = self.tasks_cache.get(task_id)
        if not task:
            return TaskStatus.NOT_FOUND

        coro = task_coro(**args)
        task_id = self.create_task(coro, task_id)
        self.set_task_cache(task_id, "args", args)
        self.set_task_cache(task_id, "status", TaskStatus.RUNNING.value)
        print(f"任务已恢复: ID={task_id}, Name={task_id}")
        print(f"args: {args}")
        print(f"self.tasks_cache: {json.dumps(self.tasks_cache, ensure_ascii=False, indent=4)}")
        return task_id

    def create_task(self, coro, task_id=None):
        """
        创建并注册一个新任务。

        Args:
            coro: 要执行的协程。
            name (str, optional): 任务的可读名称。 Defaults to None.

        Returns:
            str: 任务的唯一ID。
        """
        if task_id == None:
            task_id = str(uuid.uuid4())
        task_name = f"Task-{task_id[:8]}"

        # 使用 asyncio.create_task() 创建任务
        task = asyncio.create_task(coro, name=task_name)

        # 将任务存储在管理器中
        # 当任务完成时，通过回调函数将结果放入队列
        task.add_done_callback(
            lambda t: self._on_task_done(task_id, t)
        )
        self.tasks[task_id] = task
        print(f"任务已创建: ID={task_id}, Name={task_name}")
        return task_id

    def get_task_status(self, task_id):
        """
        查询特定任务的状态。

        Args:
            task_id (str): 要查询的任务ID。

        Returns:
            TaskStatus: 任务的当前状态。
        """
        task = self.tasks.get(task_id)
        if not task:
            return TaskStatus.NOT_FOUND

        if task.done():
            if task.cancelled():
                return TaskStatus.CANCELLED
            elif task.exception() is not None:
                return TaskStatus.ERROR
            else:
                return TaskStatus.DONE

        # asyncio.Task 没有直接的 'RUNNING' 状态。
        # 如果任务还没有完成，它要么是等待执行（PENDING），要么是正在执行（RUNNING）。
        # 这里我们简化处理，认为未完成的就是运行中。
        return TaskStatus.RUNNING

    def get_task_result(self, task_id):
        """获取已完成任务的结果，如果任务未完成或出错则返回相应信息。"""
        task = self.tasks.get(task_id)
        if self.get_task_status(task_id) == TaskStatus.DONE:
            return task.result()
        elif self.get_task_status(task_id) == TaskStatus.ERROR:
            return task.exception()
        return None

    def _on_task_done(self, task_id, task):
        """私有回调函数，在任务完成时将结果放入队列。"""
        try:
            # 将元组 (task_id, status, result) 放入队列
            self.results_queue.put_nowait(
                (task_id, TaskStatus.DONE, task.result())
            )
            self.set_task_cache(task_id, "status", TaskStatus.DONE.value)
            self.set_task_cache(task_id, "result", task.result())
        except asyncio.CancelledError:
            self.results_queue.put_nowait(
                (task_id, TaskStatus.CANCELLED, None)
            )
            self.set_task_cache(task_id, "status", TaskStatus.CANCELLED.value)
        except Exception as e:
            self.results_queue.put_nowait(
                (task_id, TaskStatus.ERROR, e)
            )
            self.set_task_cache(task_id, "status", TaskStatus.ERROR.value)
            self.set_task_cache(task_id, "result", str(e))

    async def get_next_result(self):
        """
        等待并返回下一个完成的任务结果。

        如果所有任务都已提交，但没有任务完成，此方法将异步等待。

        Returns:
            tuple: 一个包含 (task_id, status, result) 的元组。
        """
        return await self.results_queue.get()

    def get_task_index(self, task_id):
        """
        获取任务在任务字典中的插入顺序索引。

        Args:
            task_id (str): 要查询的任务ID。

        Returns:
            int: 任务的索引（从0开始），如果未找到则返回-1。
        """
        try:
            # 将字典的键转换为列表并查找索引
            task_ids_list = list(self.tasks.keys())
            return task_ids_list.index(task_id)
        except ValueError:
            # 如果任务ID不存在，则返回-1
            return -1

async def main():
    manager = TaskManager()

    # --- 任务提交阶段 ---
    print("--- 任务提交 ---")

    tasks_to_run = [
        {"goal": ""},
        {"goal": 1},
        {"goal": 5},
        {"goal": 2},
        {"goal": 4},
    ]
    task_ids = manager.create_tasks(registry.tools["worker"], tasks_to_run)
    print(f"\n主程序: {len(task_ids)} 个任务已提交，现在开始等待结果...\n")

    # --- 结果处理阶段 ---
    # 使用 get_next_result() 逐个获取已完成任务的结果
    print("--- 结果处理 ---")
    for i in range(len(task_ids)):
        print(f"等待第 {i + 1} 个任务完成...")
        # 此处会异步等待，直到队列中有可用的结果
        task_id, status, result = await manager.get_next_result()

        # 从管理器中获取任务名称（如果需要）
        task_name = manager.tasks[task_id].get_name()

        print(f"-> 收到结果: 任务 {task_name}, index: {manager.get_task_index(task_id)}")
        print(f"  - 状态: {status.value}")

        if status == TaskStatus.DONE:
            print(f"  - 结果: '{result}'")
        elif status == TaskStatus.ERROR:
            print(f"  - 错误: {result}")
        elif status == TaskStatus.CANCELLED:
            print("  - 结果: 任务被取消")
        print("-" * 20)

    print("\n--- 所有任务的结果都已处理完毕 ---")


# 运行主协程
if __name__ == "__main__":
    asyncio.run(main())
    print("\n主程序: 所有任务都已完成并处理。")