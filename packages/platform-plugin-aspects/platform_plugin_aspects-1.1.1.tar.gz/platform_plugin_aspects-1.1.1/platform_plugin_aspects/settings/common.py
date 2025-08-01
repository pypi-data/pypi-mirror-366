"""
Common Django settings for eox_hooks project.
For more information on this file, see
https://docs.djangoproject.com/en/2.22/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.22/ref/settings/
"""

from platform_plugin_aspects import ROOT_DIRECTORY


# Make '_' a no-op so we can scrape strings for translation, because
# `django.utils.translation.ugettext_noop` cannot be imported in this file
def _(text):
    return text


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.MAKO_TEMPLATE_DIRS_BASE.append(ROOT_DIRECTORY / "templates")
    settings.SUPERSET_CONFIG = {
        "internal_service_url": "http://superset:8088",
        "username": "superset",
        "password": "superset",
    }
    settings.ASPECTS_INSTRUCTOR_DASHBOARDS = [
        {
            "name": _("Course Dashboard"),
            "slug": "course-dashboard",
            "uuid": "c0e64194-33d1-4d5a-8c10-4f51530c5ee9",
            "allow_translations": True,
        },
        {
            "name": _("Individual Learner Dashboard"),
            "slug": "individual-learner",
            "uuid": "abae8a25-1ba4-4653-81bd-d3937a162a11",
            "allow_translations": True,
        },
        {
            "name": _("At-Risk Learners Dashboard"),
            "slug": "learner-groups",
            "uuid": "8661d20c-cee6-4245-9fcc-610daea5fd24",
            "allow_translations": True,
        },
    ]
    settings.SUPERSET_SHOW_INSTRUCTOR_DASHBOARD_LINK = True
    settings.SUPERSET_EXTRA_FILTERS_FORMAT = []
    settings.SUPERSET_DASHBOARD_LOCALES = ["en"]
    settings.EVENT_SINK_CLICKHOUSE_BACKEND_CONFIG = {
        # URL to a running ClickHouse server's HTTP interface. ex: https://foo.openedx.org:8443/ or
        # http://foo.openedx.org:8123/ . Note that we only support the ClickHouse HTTP interface
        # to avoid pulling in more dependencies to the platform than necessary.
        "url": "http://clickhouse:8123",
        "username": "ch_cms",
        "password": "password",
        "database": "event_sink",
        "timeout_secs": 5,
    }

    settings.EVENT_SINK_CLICKHOUSE_PII_MODELS = [
        "user_profile",
        "external_id",
    ]

    settings.EVENT_SINK_CLICKHOUSE_MODEL_CONFIG = {
        "auth_user": {
            "module": "django.contrib.auth.models",
            "model": "User",
        },
        "user_profile": {
            "module": "common.djangoapps.student.models",
            "model": "UserProfile",
        },
        "course_overviews": {
            "module": "openedx.core.djangoapps.content.course_overviews.models",
            "model": "CourseOverview",
        },
        "external_id": {
            "module": "openedx.core.djangoapps.external_user_ids.models",
            "model": "ExternalId",
        },
        "course_enrollment": {
            "module": "common.djangoapps.student.models",
            "model": "CourseEnrollment",
        },
        "custom_course_edx": {
            "module": "lms.djangoapps.ccx.models",
            "model": "CustomCourseForEdX",
        },
        "user_preference": {
            "module": "openedx.core.djangoapps.user_api.models",
            "model": "UserPreference",
        },
        "tag": {"module": "openedx_tagging.core.tagging.models", "model": "Tag"},
        "taxonomy": {
            "module": "openedx_tagging.core.tagging.models",
            "model": "Taxonomy",
        },
        "object_tag": {
            "module": "openedx_tagging.core.tagging.models",
            "model": "ObjectTag",
        },
    }

    # This is on by default here, off by default in tutor-contrib-aspects until we only
    # support versions Sumac and beyond
    settings.ASPECTS_ENABLE_STUDIO_IN_CONTEXT_METRICS = True

    settings.ASPECTS_IN_CONTEXT_DASHBOARDS = {
        "course": {
            "name": _("Course"),
            "slug": "in-context-course",
            "uuid": "f2880cc1-63e9-48d7-ac3c-d2ff6f6698e2",
            "allow_translations": True,
            "course_filter_ids": ["NATIVE_FILTER-QLQbulmHH"],
            "block_filter_ids": [],
        },
        "sequential": {
            "name": _("Graded Subsection"),
            "slug": "in-context-graded-subsection",
            "uuid": "f0321087-6428-4b97-b32e-2dae7d9cc447",
            "allow_translations": True,
            "course_filter_ids": ["NATIVE_FILTER-oPAuR7ahy"],
            "block_filter_ids": ["NATIVE_FILTER-CBWbI7uLq"],
        },
        "problem": {
            "name": _("Problem"),
            "slug": "in-context-problem",
            "uuid": "98ff33ff-18dd-48f9-8c58-629ae4f4194b",
            "allow_translations": True,
            "course_filter_ids": ["NATIVE_FILTER-29CPcbirK"],
            "block_filter_ids": ["NATIVE_FILTER-TJwItQhUI"],
        },
        "video": {
            "name": _("Video"),
            "slug": "in-context-video",
            "uuid": "bc6510fb-027f-4026-a333-d0c42d3cc35c",
            "allow_translations": True,
            "course_filter_ids": ["NATIVE_FILTER-uaxvZkSAg"],
            "block_filter_ids": ["NATIVE_FILTER-Fse4rzDW0"],
        },
    }
    settings.IN_CONTEXT_DASHBOARD_COURSE_KEY_COLUMN = "course_key"
    settings.IN_CONTEXT_DASHBOARD_BLOCK_ID_COLUMN = "block_id"
