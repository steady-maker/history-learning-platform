"""
@Remark: 不要修改这里的代码，这里保证了全局唯一的 scheduler 实例，否则无法拿到当前内存中的任务列表
"""

import sys

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from utils.middleware import info_logger, error_logger

if 'global_scheduler_instance' in sys.modules:
    scheduler = sys.modules['global_scheduler_instance']
else:
    executors = {
        'default': ThreadPoolExecutor(10),
    }

    job_defaults = {
        'coalesce': True,
        'max_instances': 1,
        'misfire_grace_time': 60,
    }

    scheduler = BackgroundScheduler(
        jobstores={'default': DjangoJobStore()},
        executors=executors,
        job_defaults=job_defaults,
        timezone='Asia/Shanghai'
    )

    def job_listener(event):
        if event.exception:
            error_logger.error(
                f"任务执行出错: {event.job_id}\n"
                f"Traceback:{event.traceback}\n"
                f"{type(event.exception).__name__}: {event.exception}\n"
            )
        else:
            info_logger.info(f"任务完成: {event.job_id}")

    scheduler.add_listener(job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
    sys.modules['global_scheduler_instance'] = scheduler  # 注册全局唯一 scheduler

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        info_logger.info(f" APScheduler:({id(scheduler)}) 已启动，并加载数据库中的任务。")
