from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from rest_framework.decorators import action

from tasks.filter import DjangoJobFilter
from tasks.scheduler import scheduler
from tasks.serializer import DjangoJobSerializer
from tasks.tasks import TasksFactory
from utils.exception import BizException
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet
from django_apscheduler.models import DjangoJob

class TasksViewSet(CustomModelViewSet):
    """
    定时任务接口:
    """
    queryset = DjangoJob.objects.all()
    serializer_class = DjangoJobSerializer
    filterset_class = DjangoJobFilter

    def list(self, request, *args, **kwargs):
        """
        定时任务列表
        """
        name = request.GET.get('name', None)
        func = request.GET.get('func', None)
        job_dict = {job.id: job for job in scheduler.get_jobs()}
        result = []
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)

        for job in serializer.data:
            job_info = job_dict.get(job["id"])
            if name and name not in job_info.name:
                continue
            if func and func not in job_info.func_ref:
                continue
            result.append({
                "id": job_info.id,
                "name": job_info.name,
                "type": job_info.trigger.__class__.__name__.lower().replace("trigger", ""),
                "next_run_time": job_info.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job_info.next_run_time else 'paused',
                "trigger": str(job_info.trigger),
                "func": job_info.func_ref.replace("tasks.tasks:TasksFactory.", "")
            })
        return self.get_paginated_response(result)

    def retrieve(self, request, *args, **kwargs):
        """
        获取定时任务详情
        """
        job_id = kwargs.get("pk")
        job_info = scheduler.get_job(job_id)
        result = {
            "id": job_info.id,
            "name": job_info.name,
            "type": job_info.trigger.__class__.__name__.lower().replace("trigger", ""),
            "func": job_info.func_ref.replace("tasks.tasks:TasksFactory.", "")
        }
        return SuccessResponse(result)

    def create(self, request, *args, **kwargs):
        """
        创建定时任务
        """
        req_data = request.data
        _id = req_data.get("id")
        name = req_data.get("name")
        _type = req_data.get("type")
        func = req_data.get("func")

        if not all([_id, name, _type, func]):
            raise BizException("基本参数不可为空")

        try:
            func = getattr(TasksFactory, func)
        except AttributeError:
            raise BizException(f"未找到任务函数: {func}")

        match _type:
            case "date":
                run_date = req_data.get("run_date")
                if not run_date:
                    raise BizException("date 类型任务必须指定 执行时间")
                trigger = DateTrigger(run_date=run_date, timezone='Asia/Shanghai')
                scheduler.add_job(id=_id, name=name, func=func, trigger=trigger, replace_existing=True)

            case "interval":
                weeks = req_data.get("weeks", 0)
                days = req_data.get("days", 0)
                hours = req_data.get("hours", 0)
                minutes = req_data.get("minutes", 0)
                seconds = req_data.get("seconds", 0)
                start_date = req_data.get("start_date")
                end_date = req_data.get("end_date")
                if not any([weeks, days, hours, minutes, seconds]):
                    raise BizException("interval 类型任务必须指定时间间隔，不可同时指定为 0")

                trigger = IntervalTrigger(
                    weeks=weeks,
                    days=days,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    start_date=start_date,
                    end_date=end_date,
                    timezone='Asia/Shanghai'
                )
                scheduler.add_job(id=_id, name=name, func=func, trigger=trigger, replace_existing=True)

            case "cron":
                cron_expr = req_data.get("cron_expr")
                if not cron_expr:
                    raise BizException("cron 类型任务必须指定 cron 表达式")
                trigger = CronTrigger.from_crontab(cron_expr, timezone='Asia/Shanghai')
                scheduler.add_job(id=_id, name=name, func=func, trigger=trigger, replace_existing=True)

            case _:
                raise BizException("未知任务类型")
        return SuccessResponse(msg="创建任务成功")

    def destroy(self, request, *args, **kwargs):
        """删除任务"""
        pk = kwargs.get("pk")
        pks = pk.split(",")
        for _id in pks:
            scheduler.remove_job(_id)
        return SuccessResponse()

    @action(detail=True)
    def pause(self, request, pk=None):
        """暂停任务"""
        pks = pk.split(",")
        for _id in pks:
            scheduler.pause_job(_id)
        return SuccessResponse(msg="暂停任务成功")

    @action(detail=True)
    def resume(self, request, pk=None):
        """恢复任务"""
        pks = pk.split(",")
        for _id in pks:
            scheduler.resume_job(_id)
        return SuccessResponse(msg="恢复任务成功")