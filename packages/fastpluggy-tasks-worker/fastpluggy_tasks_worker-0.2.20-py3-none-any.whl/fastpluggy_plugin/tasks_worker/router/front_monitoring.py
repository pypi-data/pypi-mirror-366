from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse

from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.widgets import CustomTemplateWidget

front_monitoring_task_router = APIRouter(
    tags=["task_router"],
)


@front_monitoring_task_router.get("/monitor/task_duration", response_class=HTMLResponse, name="task_duration_analytics")
async def task_duration_analytics(request: Request, view_builder=Depends(get_view_builder), ):
    items = [
        CustomTemplateWidget(
            template_name='tasks_worker/monitoring/task_time.html.j2',
            context={
                "request": request,
            }
        ),

    ]

    return view_builder.generate(
        request,
        title="Task Duration Analytics",
        widgets=items
    )
