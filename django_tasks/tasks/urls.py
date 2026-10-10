from django.urls import include, path
from .views import add_numbers, hello_world, get_all_tasks, get_tasks_by_id, create_task, TaskView, TaskViewSet
from rest_framework.routers import DefaultRouter

# in the config/urls.py file, we add path("api/", include("tasks.urls"))
# this will include the urls.py file in the tasks app
# then in the tasks/urls.py file, we add the urlpatterns
# then in the views.py file, we add the view
# then in the models.py file, we add the model
# then in the serializers.py file, we add the serializer
# then in the tests.py file, we add the tests
# then in the admin.py file, we add the admin

# urlpatterns = [
#     path('add-numbers/', add_numbers, name='add_numbers'),
#     # name is used to identify the view in the urls.py file
# ]

# the above is the same as the below
# urlpatterns = [path("hw/", hello_world),
# path("add-numbers/", add_numbers),
# path("get-tasks/", get_all_tasks),
# path("get-tasks/<int:id>/", get_tasks_by_id),
# path("create-task/", create_task),
# path("create-task-api/", TaskView.as_view()),
# path("get-task-api/<int:id>/", TaskView.as_view()),
# # path("get-task-api/", TaskView.as_view()),
# path("delete-task-api/<int:id>/", TaskView.as_view()),
# ]


# can skip all the above while using TaskViewSet by adding the following:
router = DefaultRouter()
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path("add-numbers/", add_numbers),
    path("", include(router.urls))
]
