# -*- coding: utf-8 -*-
# ErosNow.com video addon
#

import requests, json, re, os, random
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import urllib
import urllib2
from addon.common.addon import Addon

addon_id = 'plugin.video.erosnow-rain'
addon = Addon(addon_id, sys.argv)
Addon = xbmcaddon.Addon(addon_id)

language = (Addon.getSetting('langType')).lower()

dialog = xbmcgui.Dialog()

if (language=='all'):
	language2 = ''
else:
	language2 = 'language='+language[0:3]+'&'

USERAGENT   = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
headers = {'User-Agent': USERAGENT, 'Accept':"*/*", 'Accept-Encoding':'gzip,deflate,br', 'Accept-Language':'en-US,en;q=0.8', 'X-Requested-With':'XMLHttpRequest'}
	
s=requests.Session()

def cleanHex(text):
    def fixup(m):
        text = m.group(0)
        if text[:3] == "&#x": return unichr(int(text[3:-1], 16)).encode('utf-8')
        else: return unichr(int(text[2:-1])).encode('utf-8')
    return re.sub("(?i)&#\w+;", fixup, text.decode('ISO-8859-1').encode('utf-8'))
	
def cleanName(name):
    name = name.replace("&#8217;", "'").replace("\u2019", "'").replace("&#8211;", "-").replace("\u2013", "-")\
                .replace("&amp;", "&").replace("&#038;", "&").replace("&#8220;", "\"").replace("&#8221;", "\"")\
                .replace("&#8230;", "...")
    name = name.strip()
    return name
	
def get_sec(s):
    l = s.split(':')
    return int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2])
	
def make_request(url):
    try:
		s.headers=headers
		response = s.get(url, headers=s.headers, cookies=s.cookies)
		data = response.content
		return data
    except urllib2.URLError, e:
        print e
	
def make_request_post(url):
	username = (Addon.getSetting('username'))
	password = (Addon.getSetting('password'))
	# ipaddressUK="31.7."
	# for x in xrange(1,2):
		# ipaddressUK += ".".join(map(str,(random.randint(0,255) for _ in range(2))))
	
	if (username != '' and password != ''):
		body = {'el':username, 'pw':password, 'mobile':'', 'callingcode':'', 'type':'json', 'fbid':''}
		body = urllib.urlencode(body)
		try:
			s.headers['Referer']='http://erosnow.com'
			# s.headers['X-Forwarded-For']=ipaddressUK
			s.headers['Content-Type']= 'application/x-www-form-urlencoded; charset=UTF-8'
			response = s.post(url, headers=headers, data=body, cookies=s.cookies, verify=False)
			data = response.text
			return data
		except urllib2.URLError, e:
			print
	else:
		reg_remind = 'Playing without username/password'
		dialog.notification("Registration reminder", reg_remind, xbmcgui.NOTIFICATION_INFO, 8000)
		
def get_menu():
	addDir(3, '[B][COLOR orange]Free Movies[/COLOR][/B]', 'http://erosnow.com/v2/catalog/movies?content_type_id=1&'+language2+'free=true&start_index=0&max_result=20&', '')
	addDir(1, '[B][COLOR orange]Latest Movies[/COLOR][/B]', '', '')
	addDir(3, '[B][COLOR orange]ALL Movies[/COLOR][/B]','http://erosnow.com/v2/catalog/movies?content_type_id=1&'+language2+'type=movie&start_index=0&max_result=20&','')
	addDir(4, '[B][COLOR orange]By Genre[/COLOR][/B]', '', '')
	addDir(2, '[B][COLOR orange]By Letters (A-Z)[/COLOR][/B]', '', '')
	addDir(22, '[B][COLOR orange]Star Studded Collection[/COLOR][/B]', 'http://erosnow.com/v2/catalog/playlist/1045190?&start=0&count=20', '')
	addDir(11, '[B][COLOR white]Search [COLOR orange]Movies[/COLOR][/COLOR][/B] [All Languages]', '', '')
	# addDir(31, 'TV shows', 'http://erosnow.com/v2/populartvshows?start=0&limit=20', '')
	addDir(91, '[COLOR grey]Add-on Settings[/COLOR]', '', '')

def get_search_movies():
	if url:
		search_url = base_url+url
	else:
		keyb = xbmc.Keyboard('', 'Search for Movies in all languages')
		keyb.doModal()
		if (keyb.isConfirmed()):
			search_term = urllib.quote_plus(keyb.getText())
			if not search_term:
				addon.show_ok_dialog(['empty search not allowed'.title()], addon.get_name())
				sys.exit()			
		else:
			sys.exit()
	
	search_url = 'http://erosnow.com/search/movies?q='+str(search_term)+'&start=0&rows=20&'
		
	get_movies(search_url)	

def get_movies(url):
	html2 = make_request(url)
	if 'search/movies' in url:
		html2 = html2.replace('\n','')
	html = json.loads(html2)
	total = html['total']
	
	for r in html['rows']:
		name = r['title']
		link = 'http://erosnow.com/catalog/movie/'+str(r['asset_id'])+'?'
		if r.get('images'):
			if r['images'].get('8'):
				img=r['images'].get('8')
			else:
				img=''
			if r['images'].get('9'):
				img2 = r['images']['9']
			elif r['images'].get('17'):
				img2 = r['images']['17']
			else:
				img2 = ''
		desc = r.get('short_description')
		rating = r.get('rating')
		if r.get('duration'):
			duration = get_sec(r.get('duration'))
		else:
			name = name+" - [COLOR red]Not released?[/COLOR]"
			duration=''
		addDir(21, name, link, img, img2, desc=desc, rating=rating,dur=duration, isplayable=True)
	
	if 'search/movies' in url:
		start=	int(url.partition('start=')[-1].rpartition('&rows')[0])
		if(start+20 < int(total)):
			new_start = start+20
			addDir(3, ' >>> Next Page >>>', url.replace('start='+str(start),'start='+str(new_start)),'' )
	else:
		start_url = re.compile('(start_index=(\d+))').findall(url)[0][0]
		index = re.compile('start_index=(\d+)').findall(url)[0]

		if (int(index)+20 < int(total)):
			new_index = int(index)+20
			new_url = url.replace(start_url, 'start_index='+str(new_index))
			addDir(3, '>>> Next Page >>>', new_url, '')
	
		
	setView('movies', 'movie-view')
	# xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL ) 
	
def get_free_movies():
	html2 = make_request(url)
	html = json.loads(html2)
	content_id=''
	for r in html['contents']:
		if '1' in r['content_type_id']:
			content_id = r['content_id']
			name = r['title']
	if content_id:
		userurl = 'https://erosnow.com/secured/dologin'
		req = make_request_post(userurl)
		movieurl2 = 'http://erosnow.com/profiles/'+str(content_id)+'?platform=2&q=auto'
		html3 = make_request(movieurl2)
		html4 = json.loads(html3)
		req2 = json.loads(req)
		item2 = xbmcgui.ListItem(name)
		if (str(req2['success']['plan']) == 'False'):
			movie_link = html4['profiles']['ADAPTIVE_SD'][0]
		else:
			movie_link = html4['profiles']['ADAPTIVE_ALL'][0]
			subYes = Addon.getSetting('subType')
			if (subYes=='true') and (html4.get('subtitles')):
				closedcaption=[]
				closedcaption.append(html4['subtitles']['eng']['url'])
				subpath = convert_subtitles(closedcaption)
				item2.setSubtitles([subpath])
		
		item2.setProperty('IsPlayable', 'true')
		item2.setPath(movie_link['url'])
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item2)
	else:
		dialog.notification('Error', 'Movie may not be released yet.', xbmcgui.NOTIFICATION_INFO, 6000)

def convert_subtitles(closedcaption):
	# from pycaption import detect_format, SRTWriter
	# idea taken from LearningIt(t1m)
	str_output =''
	if closedcaption[0] is not None:
		try:
			cc_content = smart_unicode(make_request(closedcaption[0]))
			# reader = detect_format(cc_content)
			if cc_content != "":
				profile = Addon.getAddonInfo('profile').decode("utf-8")
				prodir  = xbmc.translatePath(os.path.join(profile))
				if not os.path.isdir(prodir):
					os.makedirs(prodir)
				subfile = xbmc.translatePath(os.path.join(profile, 'subtitles.srt'))	
				file = open(subfile, 'w+')
				str_output = re.sub('\d+(\b,\b)\d+','.',cc_content)
				str_output = str_output.replace('WEBVTT','')
				file.write(str_output)
				str_output=''
				file.close()
			else:
				print "unknown sub type"
		except:
			print "Exception with Subs: "
			subfile = ''
	return subfile
	
# Unicode function
def smart_unicode(s):
    """credit : sfaxman"""
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s

def smart_utf8(s):
    return smart_unicode(s).encode('utf-8')
	
def get_genre():
	html = make_request('http://erosnow.com/genrelist?type=movie&')
	data = json.loads(html)
	for single in data:
		title = single['type']
		link = 'http://erosnow.com/v2/catalog/movies?content_type_id=1&'+language2+'genre='+str(single['id'])+'&type=movie&start_index=0&max_result=20&'
		# link = 'http://erosnow.com/catalog/movies?'+language2+'start_index=0&genre_type='+str(single['id'])+'&max_result='+perpage+'&'
		addDir(3, title, link, '')
		
	setView('movies', 'movie-view')
	
def get_latest():
	html = make_request('http://erosnow.com/playlist?page=&location=3&position=&&subset=0&p=&plid=1006864')
	data = json.loads(html)
	for result in data['playlist']:
		title = result['asset']['title']
		link = 'http://erosnow.com/catalog/movie/'+str(result['asset']['asset_id'])+'?'
		img = result['asset']['images']['8']
		if '9' in result['content']['images']:
			img2 = result['content']['images']['9']
		else:
			img2=""
		desc = result['asset']['short_description']
		rating = result['asset']['rating']
		duration = get_sec(result['content']['duration'])
		addDir(21, title, link, img, img2, desc, rating,dur=duration, isplayable=True)
		
	setView('movies', 'movie-view')	
		
def get_letters():
	azlist = map (chr, range(65,91))
	addDir(3, '#', 'http://erosnow.com/catalog/movies?'+language2+'term=-&type=movie&start_index=0&max_result=20&', '')
	for letter in azlist:
		term = 'term='+letter.lower()+'&'
		term = 'http://erosnow.com/v2/catalog/movies?content_type_id=1&'+language2+term+'start_index=0&max_result=20&'
		# print term.strip('\'')
		addDir(3, letter, term, '')
    # xbmcplugin.endOfDirectory(int(sys.argv[1]))

def star_studded():
	html = make_request(url)
	data2 = json.loads(html)
	for r in data2['data']:
		title = r['title'] +'      [COLOR orange]'+str(r['playlist_count'])+' movies[/COLOR]'
		link = 'http://erosnow.com/v2/catalog/playlist/'+str(r['asset_id'])+'?&start=0&count=20'
		if '48' in r['images']:
			img = r['images']['48']
		elif '17' in r['images']:
			img = r['images']['17']
		else:
			img=''
		img2 = img
		addDir(23, title, link, img, img2)
		
	start=	int(url.partition('start=')[-1].rpartition('&')[0])
	if(start+20 < int(data2['playlist_count'])):
		start = start+20
		addDir(22, ' >>> Next Page >>>', 'http://erosnow.com/v2/catalog/playlist/1045190?&start='+str(start)+'&count=20', '')
		
	setView('movies', 'movie-view')

def get_star_movies():
	html = make_request(url)
	data2 = json.loads(html)
	for r in data2['data']:
		title = r['title']
		link = 'http://erosnow.com/catalog/movie/'+str(r['asset_id'])+'?'
		img=r['images']['8']
		if '9' in r['images']:
			img2 = r['images']['9']
		else:
			img2=""
		desc = r['short_description']
		rating = r['rating']
		duration = get_sec(r['duration'])
		addDir(21, title, link, img, img2,desc,rating,dur=duration, isplayable=True)
		
	start=	int(url.partition('start=')[-1].rpartition('&')[0])
	if(start+20 < int(data2['playlist_count'])):
		new_start = start+20
		addDir(23, ' >>> Next Page >>>', url.replace('start='+str(start),'start='+str(new_start)), '')
		
	setView('movies', 'movie-view')
	
def playtrailer( url ):
    addon.log('Play Trailer %s' % url)
    notification( addon.get_name(), 'fetching trailer', addon.get_icon())
    xbmc.executebuiltin("PlayMedia(%s)"%url)

def setView(content, viewType):        
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)

    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_MPAA_RATING )

def addDir(mode,name,url,image,image2="",desc="",rating="",dur="",isplayable=False):
    name = name.encode('utf-8', 'ignore')
    url = url.encode('utf-8', 'ignore')
    desc = desc.encode('cp1252').decode('utf8', 'ignore')

    if 0==mode:
        link = url
    else:
        link = sys.argv[0]+"?mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)+"&image="+urllib.quote_plus(image)

    ok=True
    item=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
    item.addStreamInfo('video', {'codec': 'h264'})
    item.addStreamInfo('audio', {'codec': 'aac', 'language': 'en', 'channels': 2})
    item.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc, "Rating": rating, "Duration": dur } )
    item.setArt({'fanart': image2})
    if 'Settings' in name:
		isfolder=False
    else:
		isfolder=True
    if isplayable:
		# print 'item is', item
		item.setProperty('IsPlayable', 'true')
		isfolder=False
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=link,listitem=item,isFolder=isfolder)
    return ok
	
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

params=get_params()	
mode=None
name=None
url=None
image=None
image2=None

try:
    mode=int(params["mode"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    image=urllib.unquote_plus(params["image"])
except:
    pass
try:
    image2=urllib.unquote_plus(params["image2"])
except:
    pass
	
if mode==None:
	get_menu()

if mode==3:
    get_movies(url)
	
if mode==4:
	get_genre()

if mode==1:
	get_latest()
	
if mode==2:
	get_letters()
	
if mode==11:
	get_search_movies()
	
if mode==21:
	get_free_movies()
	
if mode==22:
	star_studded()

if mode==23:
	get_star_movies()
	
if mode==91:
    addon.show_settings()
	
s.close()
	
xbmcplugin.endOfDirectory(int(sys.argv[1]))