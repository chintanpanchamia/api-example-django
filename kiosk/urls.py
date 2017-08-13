from django.conf.urls import include, url


urlpatterns = [
    # url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),

    url(r'^/', ),

    url(r'^social/$', include('social.apps.django_app.urls', namespace='social')),

]
