from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.static import serve

from accounts.profile import ProfileView
from shares.views.search import search_view
from museum.views import migrate_view
from commons.utils import logout
from commons.utils import login_required_post_comment
import django_comments_xtd.api as comment_xtd_api

from accounts.views import my_login, RegisterView, FeedbackView
from shares.views.views import home_view, faq_view, TestView, forbidden_view, not_found_view, server_error_view, update_log_view, PasteView
from shares.views.museum import museum_view
from problems.views import make_payment_for_full_report, case_download_link
from submission.print import PrintCodeView, PrintCodeDownload, PrintAdminView, PrintPdfDownload
from commons.utils.site_settings import force_closed
from .settings import UPLOAD_DIR, DEBUG, STATIC_DIR, MEDIA_URL, MEDIA_ROOT


urlpatterns = [
    url(r'^login/$', my_login, name='login'),
    url(r'^contests/', include('contests.urls', namespace='contests')),
    url(r'^backstage/', include('backstage.urls', namespace='backstage')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^logout/$', logout, name='logout'),
    url(r'^search/$', search_view, name='search', kwargs=force_closed()),
    url(r'^mirror/', include('filemanager.urls', namespace='filemanager')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^$', home_view, name='home'),
    url(r'^faq/$', faq_view, name='faq'),
    url(r'^problems/', include('problems.urls', namespace='problems'), kwargs=force_closed()),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^shares/', include('shares.urls', namespace='shares'), kwargs=force_closed()),
    url(r'^feedback/', FeedbackView.as_view(), name='feedback'),
    url(r'^polygon/', include('polygon.urls', namespace='polygon')),
    url(r'^message/', include('message.urls', namespace='message')),
    url(r'^notification/', include('notification.urls', namespace='notification')),
    url(r'^museum/$', migrate_view, name='museum'),
    url(r'^pay/report/', make_payment_for_full_report, name='pay_report', kwargs=force_closed()),
    url(r'^case/download/$', case_download_link, name='download_case', kwargs=force_closed()),
    url(r'^museum/$', museum_view, name='museum'),
    url(r'^update/$', update_log_view, name='update_log'),
    url(r'^paste/$', PasteView.as_view(), name='pastebin'),
    url(r'^h/', include('paste.urls', namespace='paste'), kwargs=force_closed()),
    url(r'^profile/(?P<pk>\d+)/$', ProfileView.as_view(), name='profile'),
    url(r'^i18n/', include('django.conf.urls.i18n'))
]

urlpatterns += [
    url(r'^403/(?P<exception>\w+)/$', forbidden_view),
    url(r'^404/$', not_found_view),
    url(r'^500/$', server_error_view),
]


urlpatterns += [
    url(r'^comment/post/$', login_required_post_comment, name='comments-post-comment', kwargs=force_closed()),
    url(r'^comment/api/feedback/$', comment_xtd_api.ToggleFeedbackFlag.as_view(),
        name='comments-xtd-api-feedback', kwargs=force_closed()),
    url(r'^comment/api/flag/$', comment_xtd_api.CreateReportFlag.as_view(),
        name='comments-xtd-api-flag', kwargs=force_closed()),
]

urlpatterns += [
    url(r'^p/admin/$', PrintAdminView.as_view(), name='print_admin'),
    url(r'^p/code/(?P<pk>\d+)/$', PrintCodeDownload.as_view(), name='print_code_download'),
    url(r'^p/pdf/(?P<pk>\d+)/$', PrintPdfDownload.as_view(), name='print_pdf_download'),
    url(r'^p/$', PrintCodeView.as_view(), name='print'),
]


if DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve, name='static', kwargs={'document_root': STATIC_DIR}),
        url(r'^upload/(?P<path>.*)$', serve, name='upload', kwargs={'document_root': UPLOAD_DIR}),
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^t/', TestView.as_view())
    ] + static(MEDIA_URL, document_root=MEDIA_ROOT)


handler403 = 'home.views.forbidden_view'
handler404 = 'home.views.not_found_view'
handler500 = 'home.views.server_error_view'
