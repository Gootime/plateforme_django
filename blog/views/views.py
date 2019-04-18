import os

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from blog.forms import UserLogIn, UserFormSignUp, ArticleForm, CommentForm, UserForm, ProfileForm, \
    form_reset_password_create, form_reset_password_confirm, upate_profile_form, UserFormUpdate,Contact
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import urllib
import json
import requests
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from blog.models import Capsule, Place
from cpop.settings import BASE_URL, get_header
from django.utils import formats
from django.core.mail import send_mail


def home(request):
    articles = requests.get(BASE_URL + '/api/capsule/last/')
    articles = articles.json()

    data = requests.get(BASE_URL + '/api/cpops_last/').json()




    get_territoire = requests.get(BASE_URL + '/api/place/', headers=get_header(request))
    get_territoire = [Place(place) for place in get_territoire.json()]

    get_category = [1, 2, 3, 4]  # Category.objects.all()
    allArticle = requests.get(BASE_URL + '/api/capsule/')
    allArticle = [Capsule(article) for article in allArticle.json()]
    listMarker = []
    for article in allArticle:
        listMarker.append((getLatLng(article.pk['address']), article.pk['title'], article.pk['id']))

    return render(request, 'blog/home.html',
                  {'articles': articles, 'listMarker': listMarker, 'territoires': get_territoire,
                   'categories': get_category, 'count': len(allArticle),'cpops':data})


def lire(request, id):
    oneArticle = requests.get(BASE_URL + '/api/capsule/'+str(id)+'/')
    oneArticle = Capsule(oneArticle.json())
    #print(oneArticle.pk['username'])
    capsuleAuthor = requests.get(BASE_URL + '/api/capsule_author/',json={'username':oneArticle.pk['username']}).json()
    profile = capsuleAuthor['profile']
    other_post = capsuleAuthor['capsule']

    media = oneArticle.file.instance.pk['file']
    filename, file_extension = os.path.splitext(media)
    url_formated = media
    html = ""
    # Check File_extension
    # Image
    if file_extension == '.png' or file_extension == '.PNG':
        html = "<img src='" + url_formated + "'>"
    if file_extension == '.jpg' or file_extension == '.JPG':
        html = "<img src='" + url_formated + "'>"
    if file_extension == '.gif' or file_extension == '.GIF':
        html = "<img src='" + url_formated + "'>"
    if file_extension == '.jpeg' or file_extension == '.JPEG':
        html = "<img src='" + url_formated + "'>"

    # video
    if file_extension == '.mov' or file_extension == '.MOV':
        html = "<video controls width='250'><source src='" + url_formated + "' type='video/mp4'></video>"
    if file_extension == '.mp4' or file_extension == '.MP4':
        html = "<video controls width='250'><source src='" + url_formated + "' type='video/mp4'></video>"
    if file_extension == '.mpeg4' or file_extension == '.MPEG4':
        html = "<video controls width='250'><source src='" + url_formated + "' type='video/mp4'></video>"
    if file_extension == '.avi' or file_extension == '.AVI':
        html = "<video controls width='250'><source src='" + url_formated + "' type='video/mp4'></video>"

    # Son
    if file_extension == '.mp3' or file_extension == '.MP3':
        html = "<audio controls><source src='" + url_formated + "' type='audio/mp3'></audio>"

    center = getLatLng(oneArticle.id['address'])
    # getCat = Category.objects.get(id=oneArticle.category_id)
    allArticle = []
    listMarker = []
    listMarker.append((getLatLng(oneArticle.id['address']), oneArticle.id['title']))

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.visible = True
        contenu = form.cleaned_data['contenu']
        comment.article = oneArticle
        comment.save()
    try:
        user = requests.get(BASE_URL + '/api/users/'+str(oneArticle.pk['user'])+'/', headers=get_header(request)).json()['username']
        header = get_header(request)['Authorization']
    except:
        user = None

    url = BASE_URL
    # Comment = Commentaire.objects.filter(article_id=oneArticle.id)

    return render(request, 'blog/oneArticle.html', locals())


def login_api(username, password):
    return requests.post(BASE_URL + '/api/token/create/', data={'username': username, 'password': password})


def logIn(request):
    error = False
    form = UserLogIn(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['pseudo']
        password = form.cleaned_data['password']
        r = login_api(username, password)
        try:
            request.session['token'] = r.json()['auth_token']
            request.session['me'] = requests.get(BASE_URL + '/api/users/me/', headers=get_header(request)).json()
            return redirect('toutes_les_capsules')
        except Exception as e:
            error = True
    return render(request, 'blog/logIn.html', locals())


def logOut(request):
    r = requests.post(BASE_URL + '/api/token/logout/', headers=get_header(request))
    logout(request)
    return redirect('home')


def updateProfile(request):
    error = False
    if request.method == 'POST':
        form = UserFormUpdate(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if all((form.is_valid(), profile_form.is_valid())):
            data_user = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name']
            }
            try:
                # user = requests.put(BASE_URL + '/api/users/create/', data=data_user)
                # if user.status_code != 201:
                #     raise Exception('User already exist')
                # user = user.json()
                data_profile = {
                    'user': request.session['me']['id']
                }

                if 'picture' in profile_form.cleaned_data:
                    file_profile = {
                        'picture': profile_form.cleaned_data['picture']
                    }
                else:
                    file_profile = {}

                data_put = {
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name']

                }

                # r = login_api(user['username'], form.cleaned_data['password'])
                full_profile = requests.get(BASE_URL + '/api/profile/full/', headers=get_header(request)).json()
                profile_id = full_profile['profile']['id']
                profile = requests.put(BASE_URL + '/api/profile/'+str(profile_id)+'/', data=data_profile, files=file_profile,
                                        headers=get_header(request)).json()
                user = requests.put(BASE_URL + '/api/user/'+str(request.session['me']['id'])+'/', data=data_user,
                                        headers=get_header(request)).json()
                request.session['me'] = requests.get(BASE_URL + '/api/users/me/', headers=get_header(request)).json()
                return redirect('home')
            except Exception as e:
                error = True

    form = UserFormUpdate()
    profile_form = ProfileForm()
    # if request.user.is_authenticated():
    #     redirect('home')
    return render(request, 'blog/updateprofil.html', locals())

def signUp(request):
    error = False
    if request.method == 'POST':
        form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if all((form.is_valid(), profile_form.is_valid())):
            data_user = {
                'username': form.cleaned_data['username'],
                'password': form.cleaned_data['password'],
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name']
            }
            try:
                user = requests.post(BASE_URL + '/api/users/create/', data=data_user)
                if user.status_code != 201:
                    raise Exception('User already exist')
                user = user.json()
                data_profile = {
                    'user': user['id']
                }

                if 'picture' in profile_form.cleaned_data:
                    file_profile = {
                        'picture': profile_form.cleaned_data['picture']
                    }
                else:
                    file_profile = {}

                data_put = {
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name']

                }

                r = login_api(user['username'], form.cleaned_data['password'])

                request.session['token'] = r.json()['auth_token']
                request.session['me'] = requests.get(BASE_URL + '/api/users/me/', headers=get_header(request)).json()

                profile = requests.post(BASE_URL + '/api/profile/', data=data_profile, files=file_profile,
                                        headers=get_header(request)).json()
                user = requests.put(BASE_URL + '/api/user/'+str(user['id'])+'/', data=data_put,
                                        headers=get_header(request)).json()
                return redirect('home')
            except Exception as e:
                error = True

    form = UserForm()
    profile_form = ProfileForm()
    # if request.user.is_authenticated():
    #     redirect('home')
    return render(request, 'blog/signUp.html', locals())


def profil_other(request, id):
    full_profile = requests.get(BASE_URL + '/api/profile/full/'+str(id)+'/', headers=get_header(request)).json()
    # full_profile = [Capsule(article) for article in articles.json()]

    Myarticle = full_profile['capsules']
    avatar = full_profile['profile']['picture']
    city = full_profile['profile']['city']
    user = full_profile['user']
    get_parcours = full_profile['parcours']
    paginator = Paginator(Myarticle, 6)
    page = request.GET.get('page', 1)
    try:
        article_page = paginator.page(page)
    except PageNotAnInteger:
        article_page = paginator.page(1)
    except EmptyPage:
        article_page = paginator.page(paginator.num_pages)
    return render(request, 'blog/profil_other.html', {
        'Article_by_author': article_page,
        'user': user,
        'avatar': avatar,
        'city' : city,
        'Parcours_by_author': get_parcours,
        'url': BASE_URL,
        'count_post':len(Myarticle)

    })


def profil(request, id):
    full_profile = requests.get(BASE_URL + '/api/profile/full/', headers=get_header(request)).json()
    # full_profile = [Capsule(article) for article in articles.json()]

    Myarticle = full_profile['capsules']
    avatar = full_profile['profile']['picture']
    city = full_profile['profile']['city']
    user = full_profile['user']
    get_parcours = full_profile['parcours']

    return render(request, 'blog/profil.html', {
        'Article_by_author': Myarticle,
        'user': user,
        'avatar': avatar,
        'Parcours_by_author': get_parcours,
        'url': BASE_URL,
        'header': get_header(request)['Authorization'],
    })


def view_media(request):
    items = FileItem.objects.all()
    itemsVideo = [i for i in items if i.name.split('.')[-1] == 'mp4']

    itemsImage = [i for i in items if i.name.split('.')[-1] != 'mp4']
    return render(request, 'blog/view_media.html', locals())


def upload(request):
    places = [Place(place) for place in requests.get(BASE_URL + '/api/place/').json()]
    url = BASE_URL
    return render(request, 'blog/upload/upload.html', locals())


def getLatLng(adresse):
    try:
        googleGeocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?'
        query = adresse.encode('utf-8')
        params = {
            'address': query,
            'sensor': "true"
        }

        url = googleGeocodeUrl + urllib.parse.urlencode(params) + "&key=AIzaSyDSyghpSVaeCKCEa80aGrXCl4rUwZVfea8"

        json_response = urllib.request.urlopen(url)
        response = json.loads(json_response.read())
        if response['results']:
            location = response['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
        else:
            latitude, longitude = 0, 0

        return latitude, longitude
    except:
        return 0, 0


def view_collection(request, id):
    p = requests.get(BASE_URL + '/api/playlist/'+str(id)+'/', headers=get_header(request)).json()
    get_the_post = p['playlist']['capsules']
    listMarker = []
    for article in get_the_post:
        listMarker.append((getLatLng(article['address']), article['title'], article['id']))
    return render(request, 'blog/view_collection.html', {'item': get_the_post, 'marker': listMarker})


def view_territoire(request, id):
    articles = requests.get(BASE_URL + '/api/place/' + str(id) + '/capsules/', headers=get_header(request)).json()

    territoires = requests.get(BASE_URL + '/api/place/', headers=get_header(request))
    territoires = [Place(place) for place in territoires.json()]
    get_category = [1, 2, 3, 4]
    paginator = Paginator(articles, 6)
    page = request.GET.get('page', 1)
    try:
        article_page = paginator.page(page)
    except PageNotAnInteger:
        article_page = paginator.page(1)
    except EmptyPage:
        article_page = paginator.page(paginator.num_pages)

    territoire = requests.get(BASE_URL + '/api/place/' + str(id) + '/', headers=get_header(request))
    territoire = territoire.json()
    return render(request, 'blog/view_territoire.html',
                  {'articles': article_page, 'territoires': territoires, 'categories': get_category,
                   'request_territoire': territoire['name'],'territoire_id':id})


def all_territoires(request):
    territoires = requests.get(BASE_URL + '/api/place/', headers=get_header(request))
    territoires = [Place(place) for place in territoires.json()]
    get_category = [1, 2, 3, 4]
    allArticle = requests.get(BASE_URL + '/api/capsule/')
    allArticle = [Capsule(article) for article in allArticle.json()]
    listMarker = []
    for article in allArticle:
        listMarker.append((getLatLng(article.pk['address']), article.pk['title'], article.pk['id']))
    return render(request, 'blog/all_territoires.html',
    {'territoires': territoires,
     'categories': get_category,
     'listMarker': listMarker,})


def view_categorie(request, id):
    get_article_from_categorie = requests.get(BASE_URL + '/api/capsule/category/'+str(id)+'/').json()
    paginator = Paginator(get_article_from_categorie, 6)
    page = request.GET.get('page', 1)
    try:
        article_page = paginator.page(page)
    except PageNotAnInteger:
        article_page = paginator.page(1)
    except EmptyPage:
        article_page = paginator.page(paginator.num_pages)
    territoire = requests.get(BASE_URL + '/api/place/').json()
    return render(request, 'blog/view_category.html',
                  {'articles': article_page,
                  'territoire': territoire,
                  'cat_id':id})


def tutoriel(request):
    return render(request, 'blog/tutoriel.html', locals())


def a_propos(request):
    return render(request, 'blog/a_propos.html', locals())


def toutes_les_capsules(request):
    articles = requests.get(BASE_URL + '/api/capsule/')
    get_article_from_image = requests.get(BASE_URL + '/api/capsule/category/1/').json()
    get_article_from_video = requests.get(BASE_URL + '/api/capsule/category/2/').json()
    get_article_from_son = requests.get(BASE_URL + '/api/capsule/category/3/').json()
    get_article_from_text = requests.get(BASE_URL + '/api/capsule/category/4/').json()

    #ull_profile = requests.get(BASE_URL + '/api/profile/full/'+str(id)+'/', headers=get_header(request)).json()
    #avatar = full_profile['profile']['picture']
    #city = full_profile['profile']['city']
    #user = full_profile['user']
    #get_parcours = full_profile['parcours']
    #Myarticle = full_profile['capsules']



    articles = [Capsule(article) for article in articles.json()]
    paginator = Paginator(articles, 6)
    page = request.GET.get('page', 1)
    try:
       article_page = paginator.page(page)
    except PageNotAnInteger:
       article_page = paginator.page(1)
    except EmptyPage:
       article_page = paginator.page(paginator.num_pages)
    territoires = requests.get(BASE_URL + '/api/place/', headers=get_header(request))
    territoires = [Place(place) for place in territoires.json()]
    categories = [1, 2, 3, 4]
    return render(request, 'blog/toutes_les_capsules.html', {
    'articles' : article_page ,
    'count_post' : len(articles),
    'territoires':territoires,
    'categories':categories,
    'count_image':len(get_article_from_image),
    'count_video':len(get_article_from_video),
    'count_son':len(get_article_from_son),
    'count_text':len(get_article_from_text)})



def cpops(request):
    data = requests.get(BASE_URL + '/api/cpops/').json()
    paginator = Paginator(data,18)
    page = request.GET.get('page', 1)
    try:
        cpops_page = paginator.page(page)
    except PageNotAnInteger:
        cpops_page_page = paginator.page(1)
    except EmptyPage:
        cpops_page = paginator.page(paginator.num_pages)
    return render(request, 'blog/cpops.html', { 'data' : cpops_page })


def updateArticle(request, id):
    places = [Place(place) for place in requests.get(BASE_URL + '/api/place/').json()]
    url = BASE_URL
    instance = Capsule(requests.get(BASE_URL + '/api/capsule/'+str(id)+'/').json())
    return render(request, 'blog/updateArticle.html', locals())

def password_reset_create_api(email):
    data = {'email': email}
    lol =  requests.post(BASE_URL + '/api/password/reset/', data=data)
    return lol

def reset_password_create(request):
    form_reset_create = form_reset_password_create(request.POST)
    if form_reset_create.is_valid():
        email = form_reset_create.cleaned_data['email']
        try:
            lol = password_reset_create_api(email)
            redirect('logIn')
        except:
            return ('Erreur')
            redirect('logIn')
    return render(request,'blog/reset_password_create.html', locals())

def password_reset_confirm_api(new_password, re_new_password, uid, token):
    data = {
        'new_password': new_password,
        're_new_password': re_new_password,
        'uid': uid,
        'token': token
    }
    return requests.post(BASE_URL + '/api/password/reset/confirm/', data=data)

def reset_password_confirm(request, uid, token):
    form_reset_confirm = form_reset_password_confirm(request.POST)
    if form_reset_confirm.is_valid():
        new_password = form_reset_confirm.cleaned_data['new_password']
        re_new_password = form_reset_confirm.cleaned_data['re_new_password']
        try:
            password_reset_confirm_api(new_password, re_new_password, uid, token)
            redirect('home')
        except Exception as e:
            pass

    return render(request,'blog/reset_password_confirm.html', locals())


def contact(request):
    form = Contact(request.POST)
    if form.is_valid():
        sujet = form_reset_create.cleaned_data['sujet']
        email = form_reset_create.cleaned_data['email']
        message = form_reset_create.cleaned_data['message']
        print(sujet + ' ' + email + ' ' + message)
        try:
            send_mail(
                sujet,
                message,
                email,
                ['gotimeingame@gmail.com'],
                fail_silently=False,
            )
        except:
            return('Erreur')
    return render(request,'blog/contact.html',locals())

def view_collection(request):
    all_playlist = requests.get(BASE_URL + '/api/all_playlist').json()
    print(json.dumps(all_playlist))
    #playlist_by_author = all_playlist['playlist']
    return render(request,'blog/view_collection.html',locals())

def FAQ(request):
    print('Hello world')
    return render(request,'blog/faq.html',locals())

def QSN(request):
    print('Hello World')
    return render(request,'blog/qsn.html',locals())

def a_propos(request):
    print('Hello World')
    return render(request,'blog/a_propos.html',locals())

def app(request):
    print('Hello World')
    return render(request,'blog/app.html',locals())
