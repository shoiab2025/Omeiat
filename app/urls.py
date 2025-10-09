from django.urls import path
from django.views.generic import TemplateView
from app.views.job.jobs import (
    job_list_ins,
    job_list,
    job_detail,
    apply_job,
    my_applications,
    ins_applications,
    withdraw_application,
    my_jobs,
    update_job,
    delete_job,
    all_applications,
    create_or_update_job
)
from app.views.job.jobs import (
    add_to_shortlist,
    remove_from_shortlist,
    toggle_shortlist,
    bulk_add_to_shortlist,
    clear_shortlist,
    get_shortlist_status,
    get_shortlist_count
)
from app.views.dashboard.dashboard import dashboard_view, latest_jobs_views
from app.views.index.home_view import (home, about, institution_dashboard, institution_profile, profile_view)
from app.views.authentication.authentication import (
    register_account,
    login_account,
    logout_account,
    verify_otp
)

urlpatterns = [
    # ----------------------------
    # Home / Dashboard
    # ----------------------------
    path("", home, name="home"),
    path("about/", about, name="about"),
    path("dashboard/", institution_dashboard, name="dashboard"),
    path("latest-jobs/", latest_jobs_views, name="latest_jobs"),

    # ----------------------------
    # Job URLs (Public)
    # ----------------------------
    path("jobs/", job_list, name="jobs"),
    path("ins_jobs/", job_list_ins, name="ins_jobs"),
    path("jobs/<int:job_id>/", job_detail, name="job_detail"),

    # ----------------------------
    # Job Seeker URLs
    # ----------------------------
    path("jobs/<int:job_id>/apply/", apply_job, name="apply_job"),
    path("my-applications/", my_applications, name="my_applications"),
    path("my-applications/<int:application_id>/withdraw/", withdraw_application, name="withdraw_application"),

    # ----------------------------
    # Institution URLs
    # ----------------------------
    path("institution/jobs/", my_jobs, name="my_jobs"),
    path("ins_applications/", ins_applications, name="ins_applications"),
    path('jobs/save/', create_or_update_job, name='job_create_or_update'),
    path("institution/jobs/<int:job_id>/delete/", delete_job, name="delete_job"),

    # ----------------------------
    # Job Shortlist URLs (Institution)
    # ----------------------------
    path("job/<int:job_id>/shortlist/add/<int:user_id>/", add_to_shortlist, name="add_to_shortlist"),
    path("job/<int:job_id>/shortlist/remove/<int:user_id>/", remove_from_shortlist, name="remove_from_shortlist"),
    path("job/<int:job_id>/shortlist/toggle/<int:user_id>/", toggle_shortlist, name="toggle_shortlist"),
    path("job/<int:job_id>/shortlist/bulk-add/", bulk_add_to_shortlist, name="bulk_add_to_shortlist"),
    path("job/<int:job_id>/shortlist/clear/", clear_shortlist, name="clear_shortlist"),
    path("job/<int:job_id>/shortlist/status/<int:user_id>/", get_shortlist_status, name="get_shortlist_status"),
    path("job/<int:job_id>/shortlist/count/", get_shortlist_count, name="get_shortlist_count"),

    # ----------------------------
    # Admin URLs
    # ----------------------------
    path("admin/applications/", all_applications, name="all_applications"),

    # ----------------------------
    # Profile
    # ----------------------------
    path("profile/", profile_view, name="profile"),
    path("ins_profile/", institution_profile,  name="ins_profile"),
    path("profile/update/", TemplateView.as_view(template_name="update_profile.html"), name="update_profile"),

    # ----------------------------
    # User Authentication
    # ----------------------------
    path("register/", register_account, name="register"),
    path("login/", login_account, name="user_login"),
    path("verify-otp/", verify_otp, name="user_verify_otp"),
    path("logout/", lambda r: logout_account(r, "user"), name="user_logout"),

    # ----------------------------
    # Institution Authentication
    # ----------------------------
    path("institution/register/", lambda r: register_account(r, "institution"), name="institution_register"),
    path("institution/login/", lambda r: login_account(r, "institution"), name="institution_login"),
    path("institution/verify-otp/", lambda r: verify_otp(r, "institution"), name="institution_verify_otp"),
    path("institution/logout/", lambda r: logout_account(r, "institution"), name="institution_logout"),
]