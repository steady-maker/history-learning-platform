import sys
from concurrent.futures import ThreadPoolExecutor

"""
确保全局唯一的线程池实例
"""

if 'global_thread_pool' in sys.modules:
    threadPool = sys.modules['global_thread_pool']
else:
    threadPool = ThreadPoolExecutor(
        max_workers=10,
        thread_name_prefix="hte_"
    )
    # 注册为全局可复用实例
    sys.modules['global_thread_pool'] = threadPool