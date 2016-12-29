from django.conf.urls import url
from . import views

app_name = 'lovemarker'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/', views.register, name='register'),
    url(r'^login/', views.login, name='login'),
    url(r'^check_user_is_exist/', views.checkUserIsExist, name='checkUserIsExist'),
    url(r'^upload_avatar/', views.uploadAvatar, name='uploadAvatar'),
    url(r'^update_user_location/', views.updateUserPostLocation, name='updateUserPostLocation'),
    url(r'^get_post_tag/', views.getPostTag, name='getPostTag'),
    # url(r'^get_post_by_location/', views.getLocationByLocation, name='getLocationByLocation'),
    # url(r'^get_user_post/', views.getUserPost, name='getUserPost'),
    # url(r'^get_user_info_by_username/', views.getUserInfoByUsername, name='getUserInfoByUsername'),
    # url(r'^modify_user_info/', views.modifyUserInfo, name='modifyUserInfo'),
    # url(r'^get_post_by_username/', views.getPostByUsername, name='getPostByUsername'),
    # url(r'^get_current_post/', views.getCurrentPost, name='getCurrentPost'),
    # url(r'^delete_post_by_id/', views.deletePostById, name='deletePostById'),
    # url(r'^report_post/', views.reportPost, name='reportPost'),
    # url(r'^report_issue/', views.reportIssue, name='reportIssue'),
    # url(r'^get_user_info_by_useid/', views.getUserInfoByUseId, name='getUserInfoByUseId'),
    # url(r'^get_the_current_post/', views.getTheCurrentPost, name='getTheCurrentPost'),
    # url(r'^get_current_one_hour_post/', views.getCurrentOneHourPost, name='getCurrentOneHourPost'),
]