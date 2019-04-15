
from django.urls import path
from django.views.generic import TemplateView

from blog.views import views

urlpatterns = [
    path('', views.home, name="home"),
    path('tutoriel', views.tutoriel, name="tutoriel"),
    path('cpops', views.cpops, name="cpops"),
    path('toutes_les_capsules', views.toutes_les_capsules, name="toutes_les_capsules"),
    path('a_propos', views.a_propos, name="a_propos"),
    path('signUp', views.signUp, name="signUp"),
    path('logIn', views.logIn, name="logIn"),
    path('logOut', views.logOut, name="logOut"),
    path('profil/<int:id>', views.profil, name="profil"),
    path('profil_other/<int:id>', views.profil_other, name="profil_other"),
    path('view_media', views.view_media, name="media"),
    path('article/<int:id>', views.lire, name="lire"),
    path('parcours/<int:id>', views.view_collection,name="view_collection"),
    path('territoire/<int:id>', views.view_territoire,name="view_territoire"),
    path('territoires/',views.all_territoires,name="all_territoires"),
    path('categorie/<int:id>', views.view_categorie,name="view_categorie"),
    path('updateArticle/<int:id>', views.updateArticle,name="updateArticle"),
    path('upload', views.upload, name='upload'),
    path('reset_password_create',views.reset_password_create,name="reset_password_create"),
    path('updateprofil/',views.updateProfile,name='update_profil'),
    path('password/reset/confirm/<str:uid>/<str:token>', views.reset_password_confirm, name="reset_password_confirm"),
    path('contact',views.contact,name="contact"),
    path('parcours',views.view_collection,name="view_collection"),
    path('faq',views.FAQ,name="FAQ"),
    path('qsn',views.QSN,name="qui-sommes-nous"),
    path('a_propos',views.a_propos,name="a_propos"),
    path('app',views.app,name="app"),

]
