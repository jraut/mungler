# -*- coding: utf-8 -*-
import re, os, sys

def etsi_ja_korvaa_muuttujat_merkkijonoista(teksti):
	a = re.compile(r"""
						(?P<merkkijono>((?P<merkkijononalkumerkki>["'])(?P<teksti>.*?)(?P=merkkijononalkumerkki)))		# Merkkijonot eivät normaalisti sisällä. Laitetaan sivuun ja käydään läpi muuttujien löytämiseksi.
					""", re.X|re.M|re.S)
	def merkkijonojen_korvaaminen(match):
		re_osumat = match.groupdict()
		teksti = re_osumat['teksti']
		erotin = re_osumat['merkkijononalkumerkki']
		if 	teksti in NIMIKEKARTTA:
			return erotin+NIMIKEKARTTA[teksti]+erotin
		else:
			return erotin+teksti+erotin
	return a.sub(merkkijonojen_korvaaminen, teksti)
							
def etsi_ja_korvaa_muuttujat(teksti):
	a = re.compile(r"""
					(?P<kommentti>(\/\* .*? \*\/) | (\/\/.*?$))	|											# Moniriviset ja yksiriviset kommentit. -> siirretty omakseen
					(?P<merkkijono>((?P<merkkijononalkumerkki>["']).*?(?P=merkkijononalkumerkki))) |		# Merkkijonot eivät normaalisti sisällä. Laitetaan sivuun ja käydään läpi muuttujien löytämiseksi.
#					(?P<eventmap>events:\s*\{.*?\})			|												# Merkkijonomuuttuja: backbone.js: osana funktiomäärittelyn events-mappia.	
					(?P<objekti>\{ [^}]*? \}) |																# Ei välttämättä tarpeellinen ...
					(?P<kutsu>\( [^)]*? \)) |																# Ei välttämättä tarpeellinen ...
# 					(?P<bbarvo>(?P<bbtoimenpide>.get|.set)\((?P<bbsisalto>[^)]+)\))		|					# Merkkijonomuuttuja: tietynmuotoiset Backbone-kutsut: get- ja set. get('muuttuja')
					(?P<kirjastokutsu>((\$\(.*?\))|(Backbone)|(Math)|(_)|(console))([.]\w*)*) |				# Kirjastokutsujen metodit ovat sellaisinaan - ei vaadi toimenpiteitä.
					(?P<muuttuja>\b[a-zA-Z]\w*\b) 															# Loput ilmaisut ovat muuttujia. Eivät ala kuin kirjaimella.
																
					""", re.X|re.M|re.S)
																							# var-määritteessä
#					\(?ms\{.*(?<muuttuja>\w)\s*:.+})  					# objektin ominaisuutena - Tätä ei ehkä tarvitse toteuttaa
#					\(?ms\{.*:[\b^"](?<muuttuja>\w)[\b^"].*}) 			# objektin ominaisuuden arvona
						# osana laskutoimitusta
						# osana parametrilistausta ( )
						# osana objektin arvomäärittelyä {tätäEiMuuteta: muuttuja}

#	a.match(rivi)
	return a.sub(kasittely_re_korvaukselle, teksti)

def poista_kommentit(teksti):
	return re.sub(r"(?xms)(?P<kommentti>(\/\* .*? \*\/) | (\/\/.*?$))", "", teksti)
	
def poista_valimerkit(teksti):
	a = re.compile(r"""
					(?P<edeltaja>\S*)\s+ 
					""", re.X|re.M|re.S)
	def valimerkinpoisto(match):
		if match.groups()[0] in VARATUT:
			return match.groups()[0]+" "
		else:
			return match.groups()[0]			
	return a.sub(valimerkinpoisto, teksti)

def merkkijonossa(teksti):#'events: {"a": "a1"."aa": "a2"}'
	a = re.compile(r"""

					(((?:(\.(on|off|trigger|once|listenTo|stopListening|listenToOnce)\()  \s* \{				# Merkkijonot voivat sisältää muuttujan: backbone.js: event-funktiokutsussa map-muodossa.
					 .*?):\s*['"](?P<muuttuja1>[a-zA-Z]\w*)['"].*?\))  |										# Jatkoa edelliseen...                   backbone.js: event-funktiokutsussa map-muodossa.
					(\.(on|off|trigger|once|listenTo|stopListening|listenToOnce)\(\.*						# Merkkijonot voivat sisältää muuttujan: backbone.js: -kutsussa merkkijonomuodossa.
					['"]\b(?P<muuttuja3>[a-zA-Z]\w*)\b['"][,.*?]*\)))										# Jatkoa edelliseen... 
					""", re.X|re.M|re.S)
	a.sub(boguskasittely, teksti)
def boguskasittely(match):
	osumat = match.groupdict()

	if osumat['muuttuja1']:
		print osumat['muuttuja1']
	if osumat['muuttuja2']:
		print osumat['muuttuja2']
	if osumat['muuttuja3']:
		print osumat['muuttuja3']
#merkkijonossa('events: {"a": "a1"."aa": "a2"}')

# Merkkijonokorvauksien toteuttaminen:
def kasittely_re_korvaukselle(match):
	re_osumat = match.groupdict();
#	if re_osumat['bbarvo']:
#		print re_osumat['bbarvo'];
#		return "."+re_osumat['bbtoimenpide']+"("+kasittely_jossa_stringkorvaus(re_osumat['bbsisalto'])+")"
	if re_osumat['merkkijono']:
		SEURANTAAN.append(re_osumat['merkkijono'])
		return re_osumat['merkkijono']#return kasittely_merkkijonoille(match)
#	if re_osumat['eventmap']:
#		return kasittely_jossa_stringkorvaus(re_osumat['eventmap'])
	if re_osumat['kirjastokutsu']:
		return re_osumat['kirjastokutsu']
		return kasittely_kirjastokutsuille(match)
	if re_osumat['muuttuja']:
		return kasittely_muuttujille(match.group('muuttuja'))	
	if re_osumat['objekti']:
#		print re_osumat
		return "{"+etsi_ja_korvaa_muuttujat(re_osumat['objekti'][1:-1])+"}"
	if re_osumat['kutsu']:
#		print re_osumat
		return "("+etsi_ja_korvaa_muuttujat(re_osumat['kutsu'][1:-1])+")"
	return "";
	
#	korvattavat_ryhmat = ['muuttuja', 'kommentti', 'merkkijono', 'kirjastokutsu']
#		for ryhma in korvattavat_ryhmat:
#			if ryhma in match.groups():
#				return match.group(ryhma)

def kasittely_muuttujille(muuttuja):
		
	
	if type(muuttuja) is not str: 
			muuttuja = muuttuja.group('muuttuja')
	
	osat = muuttuja.split(' ')
	if len(osat) > 1: # Eventmapin nimikeosassa käytetään viittauksia: "event domelement"
		return muuttuja #ei vielä käsitellä domelementtejä
		palautus = ""
		for osa in osat:
			palautus += kasittely_muuttujille(osa)+" ";
		return palautus
	else: 	
		if muuttuja in VARATUT:
			return muuttuja
		if muuttuja not in NIMIKEKARTTA:
			monesko = len(NIMIKEKARTTA)								# Monesko oma lisättävä nimikekarttaan tulee.
			nimike = lukujarjestelmasta_toiseen(monesko, MERKIT)	# Haetaan uusi nimike 
			NIMIKEKARTTA[muuttuja] = nimike						# Tallennetaan uusi nimike 
		return NIMIKEKARTTA[muuttuja]


def kasittely_jossa_stringkorvaus(eventmap_teksti): # Tavallaan turha toistaiseksi. Tarvitaan vasta dom-nimikkeiden sotkemiseen.
	a = re.compile(r"""
					\s*['"]\s*(?P<nimike_hipsuissa>[^"']+)\s*['"]\s*(?=:) |
					\s*(?P<nimike>\w+)\s*(?=:) |
					\s*:\s*['"]\s*(?P<ilmaisu_hipsuissa>\w+)\s*['"]\s*,? |
					\s*:\s*(?P<ilmaisu>\w+)\s*,? |
	#				\s*(?P<muuttuja>\b*\w+\b*)\s*
					""", re.X|re.M|re.S)

	def eventmapkorvaus(match):
		re_osumat = match.groupdict();
		if re_osumat['nimike_hipsuissa']:
#			print "hipsut "+re_osumat['nimike_hipsuissa']+" eli "+kasittely_muuttujille(re_osumat['nimike_hipsuissa'])
			return "'"+kasittely_muuttujille(re_osumat['nimike_hipsuissa'])+"':"
		if re_osumat['nimike']:
			return kasittely_muuttujille(re_osumat['nimike'])+":"
		if re_osumat['ilmaisu_hipsuissa']:
			#print "hipsut "+re_osumat['ilmaisu_hipsuissa']+" eli "+kasittely_muuttujille(re_osumat['ilmaisu_hipsuissa'])
			SEURANTAAN.append(re_osumat['ilmaisu_hipsuissa'])
			return "'"+kasittely_muuttujille(re_osumat['ilmaisu_hipsuissa'])+"',"
		if re_osumat['ilmaisu']:
			SEURANTAAN.append(re_osumat['ilmaisu'])
			return kasittely_muuttujille(re_osumat['ilmaisu'])+","
#		if re_osumat['muuttuja']:
#			return kasittely_muuttujille(re_osumat['muuttuja'])
		
		
	return a.sub(eventmapkorvaus, eventmap_teksti)
#	return match.group('eventmap') 
	
def kasittely_kommenteille(match):
	return ""

def kasittely_merkkijonoille(match):
	return match.group('merkkijono')

def kasittely_kirjastokutsuille(match):
	return match.group('kirjastokutsu')
		
	
# Aakkoset a-z.
MERKIT = [chr(i) for i in range(ord('a'), ord('z')+1)]	

# Ottaa vastaan listan jossa merkkijonoja ja palauttaa avain-arvo -pareina saman listan.
#	Listan avaimet luodaan järjestyksessä merkeistä a-z: a, b, c, d, ... , aa, ab, ac, ad, ... , ba, bb, bc, ...
#	Todo! Ottaa vastaan re.matcheja jotta tieto paikoista säilyisi. Ei välttämättä tarpeellinen ominaisuus.

def lukujarjestelmasta_toiseen(kymmenkantainen_luku, lukujarjestelman_merkit):
	palautus = ""
	merkkien_maara = 1
	lukujarjestelman_kantaisuus = len(lukujarjestelman_merkit)
	valisumma = lukujarjestelman_kantaisuus
	while valisumma < kymmenkantainen_luku:
		merkkien_maara += 1
		valisumma = (lukujarjestelman_kantaisuus ** merkkien_maara)
	valisumma = kymmenkantainen_luku
	eksponentit = range(0, merkkien_maara)
	eksponentit.reverse();
	for i in eksponentit:
		resoluutio = lukujarjestelman_kantaisuus ** i;
		numeraali = 0
		while (valisumma > resoluutio):
			valisumma -= resoluutio 
			numeraali += 1		
		palautus += lukujarjestelman_merkit[numeraali]
	return palautus


def muodosta_uusi_nimikekartta(muuttujanimikkeet, varatut):
	nimike = ""
	monesko = 0
	palautus = {}
	for mn in muuttujanimikkeet:
		monesko += 1
		nimike = lukujarjestelmasta_toiseen(monesko, MERKIT)
		palautus[mn] = nimike
	for i in varatut: 
		palautus[i] = i
	return palautus

JS_VARATUT = ["break", "case", "class", "catch", "const", "continue", "debugger", "default", "delete", "do", "else", "export", "extends", "finally", "for", "function", "if", "import", "in", "instanceof", "let", "new", "return", "super", "switch", "this", "throw", "try", "typeof", "var", "void", "while", "with", "yield"]
VARATUT = [	
	#common usage
	"arguments", "null", "NULL", "true", "false", "undefined", "NaN", "Infinity", "toString",
	#string functions
	"trim", "split", "join", 
	#array functions
	
	#ECMAScript 6
	"break", "case", "class", "catch", "const", "continue", "debugger", "default", "delete", "do", "else", "export", "extends", "finally", "for", "function", "if", "import", "in", "instanceof", "let", "new", "return", "super", "switch", "this", "throw", "try", "typeof", "var", "void", "while", "with", "yield",
	#Backbone
	"events", "Events", "render", "on", "off", "trigger", "once", "listenTo", "stopListening", "listenToOnce", "add", "remove", "update", "reset", "sort", "change", "destroy", "request", "sync", "error", "invalid", "route", "all",
	"Model", "extend", "constructor", "initialize", "get", "set", "escape", "has", "unset", "clear", "id", "idAttribute", "cid", "attributes", "changed", "defaults", "toJSON", "sync", "fetch", "save", "destroy", "Underscore Methods (9)", "validate", "validationError", "isValid", "url", "urlRoot", "parse", "clone", "isNew", "hasChanged", "changedAttributes", "previous", "previousAttributes",
	"Collection", "extend", "model", "modelId", "constructor / initialize", "models", "toJSON", "sync", "add", "remove", "reset", "set", "get", "at", "push", "pop", "unshift", "shift", "slice", "length", "comparator", "sort", "pluck", "where", "findWhere", "url", "parse", "clone", "fetch", "create",
	"Router", "extend", "routes", "constructor / initialize", "route", "navigate", "execute",
	"History", "start",
	"Sync", "Backbone.sync", "Backbone.ajax", "Backbone.emulateHTTP", "Backbone.emulateJSON",
	"View", "extend", "constructor / initialize", "el", "$el", "setElement", "attributes", "$ (jQuery)", "template", "render", "remove", "delegateEvents", "undelegateEvents", "tagName", "className", "id", "model", "collection", "el", "id", "$el",
	#Underscore
	"Collections", "each", "map", "reduce", "reduceRight", "find", "filter", "where", "findWhere", "reject", "every", "some", "contains", "invoke", "pluck", "max", "min", "sortBy", "groupBy", "indexBy", "countBy", "shuffle", "sample", "toArray", "size", "partition",
	"Arrays", "first", "initial", "last", "rest", "compact", "flatten", "without", "union", "intersection", "difference", "uniq", "zip", "unzip", "object", "indexOf", "lastIndexOf", "sortedIndex", "findIndex", "findLastIndex", "range",
	"Functions", "bind", "bindAll", "partial", "memoize", "delay", "defer", "throttle", "debounce", "once", "after", "before", "wrap", "negate", "compose",
	"Objects", "keys", "allKeys", "values", "mapObject", "pairs", "invert", "create", "functions", "findKey", "extend", "extendOwn", "pick", "omit", "defaults", "clone", "tap", "has", "matcher", "property", "propertyOf", "isEqual", "isMatch", "isEmpty", "isElement", "isArray", "isObject", "isArguments", "isFunction", "isString", "isNumber", "isFinite", "isBoolean", "isDate", "isRegExp", "isNaN", "isNull", "isUndefined",
	"Utility", "noConflict", "identity", "constant", "noop", "times", "random", "mixin", "iteratee", "uniqueId", "escape", "unescape", "result", "now", "template",
	"Chaining", "chain", "value",	
	#Animation events
"animationend", "animationiteration", "animationstart", "beginEvent", "endEvent", "repeatEvent",
#Battery events
"chargingchange chargingtimechange", "dischargingtimechange levelchange",
#Call events
"alerting", "busy", "callschanged cfstatechange", "connected", "connecting", "dialing", "disconnected", "disconnecting", "error", "held", "holding", "incoming", "resuming", "statechange", "voicechange",
#CSS events
"CssRuleViewRefreshed", "CssRuleViewChanged", "CssRuleViewCSSLinkClicked", "transitionend",
#Database events
"abort", "blocked", "complete", "error", "success", "upgradeneeded", "versionchange",
#Document events
"DOMLinkAdded", "DOMLinkRemoved", "DOMMetaAdded", "DOMMetaRemoved", "DOMWillOpenModalDialog", "DOMModalDialogClosed", "unload",
#DOM mutation events
"DOMAttributeNameChanged", "DOMAttrModified", "DOMCharacterDataModified", "DOMContentLoaded", "DOMElementNameChanged", "DOMNodeInserted", "DOMNodeInsertedIntoDocument", "DOMNodeRemoved", "DOMNodeRemovedFromDocument", "DOMSubtreeModified",
#Drag events
"drag", "dragdrop", "dragend", "dragenter", "dragexit", "draggesture", "dragleave", "dragover", "dragstart", "drop",
#Element events
"invalid", "overflow", "underflow", "DOMAutoComplete", "command", "commandupdate",
#Focus events
"blur", "change", "DOMFocusIn", "DOMFocusOut", "focus", "focusin", "focusout",
#Form events
"reset", "submit",
#Frame events
"mozbrowserclose", "mozbrowsercontextmenu", "mozbrowsererror", "mozbrowsericonchange", "mozbrowserlocationchange", "mozbrowserloadend", "mozbrowserloadstart", "mozbrowseropenwindow", "mozbrowsersecuritychange", "mozbrowsershowmodalprompt", "mozbrowsertitlechange", "DOMFrameContentLoaded",
#Input device events
"click", "contextmenu", "DOMMouseScroll", "dblclick", "gamepadconnected", "gamepaddisconnected", "keydown", "keypress", "keyup", "MozGamepadButtonDown", "MozGamepadButtonUp", "mousedown", "mouseenter", "mouseleave", "mousemove", "mouseout", "mouseover", "mouseup", "mousewheel", "MozMousePixelScroll", "pointerlockchange", "pointerlockerror,wheel",
#Media events
"audioprocess", "canplay", "canplaythrough", "durationchange", "emptied", "ended", "ended", "loadeddata", "loadedmetadata", "MozAudioAvailable", "pause", "play", "playing", "ratechange", "seeked", "seeking", "stalled", "suspend", "timeupdate", "volumechange", "waiting", "complete",
#Menu events
"DOMMenuItemActive", "DOMMenuItemInactive",
#Network events
"datachange", "dataerror", "disabled", "enabled", "offline", "online", "statuschange", "connectionInfoUpdate,",
#Notification events
"AlertActive", "AlertClose",
#Popup events
"popuphidden", "popuphiding", "popupshowing", "popupshown", "DOMPopupBlocked",
#Printing events
"afterprint", "beforeprint",
#Progress events
"abort", "error", "load", "loadend", "loadstart", "progress", "progress", "timeout", "uploadprogress",
#Resource events
"abort", "cached", "error", "load",
#Script events
"afterscriptexecute", "beforescriptexecute",
#Sensor events
"compassneedscalibration", "devicelight", "devicemotion", "deviceorientation", "deviceproximity", "MozOrientation", "orientationchange", "userproximity",
#Session history events
"pagehide", "pageshow", "popstate",
#Smartcard events
"icccardlockerror", "iccinfochange", "smartcard-insert", "smartcard-remove", "stkcommand", "stksessionend", "cardstatechange",
#SMS and USSD events
"delivered", "received", "sent", "ussdreceived",
#Storage events
"change (see Non-standard events)", "storage",
#SVG events
"SVGAbort", "SVGError", "SVGLoad", "SVGResize", "SVGScroll", "SVGUnload", "SVGZoom",
#Tab events
"tabviewsearchenabled", "tabviewsearchdisabled", "tabviewframeinitialized", "tabviewshown", "tabviewhidden", "TabOpen", "TabClose", "TabSelect", "TabShow", "TabHide", "TabPinned", "TabUnpinned", "SSTabClosing", "SSTabRestoring", "SSTabRestored", "visibilitychange",
#Text events
"compositionend", "compositionstart", "compositionupdate", "copy", "cut", "paste", "select", "text",
#Touch events
"MozEdgeUIGesture", "MozMagnifyGesture", "MozMagnifyGestureStart", "MozMagnifyGestureUpdate", "MozPressTapGesture", "MozRotateGesture", "MozRotateGestureStart", "MozRotateGestureUpdate", "MozSwipeGesture", "MozTapGesture", "MozTouchDown", "MozTouchMove", "MozTouchUp", "touchcancel", "touchend", "touchenter", "touchleave", "touchmove", "touchstart",
#Update events
"checking", "downloading", "error", "noupdate", "obsolete", "updateready",
#Value change events
"broadcast", "CheckboxStateChange", "hashchange", "input", "RadioStateChange", "readystatechange", "ValueChange",
#View events
"fullscreen", "fullscreenchange", "fullscreenerror", "MozEnteredDomFullscreen", "MozScrolledAreaChanged", "resize", "scroll", "sizemodechange",
#Websocket events
"close", "error", "message", "open",
#Window events
"DOMWindowCreated", "DOMWindowClose", "DOMTitleChanged", "MozBeforeResize", "SSWindowClosing", "SSWindowStateReady", "SSWindowStateBusy", "close",
#Uncategorized events
"beforeunload", "localized", "message", "message", "message", "MozAfterPaint", "moztimechange", "open", "show"	
		
	]
	
		
		
# SUORITUS:
#	-otetaan sotkettava tiedosto komentoriviltä argumenttina. 
#	-haetaan sen muuttujien määritellyt nimet. 
#	-luodaan niille hakemisto, joissa uudet nimet.
SEURANTAAN = []
NIMIKEKARTTA = {}
def suoritus(): 

	tiedostonimi = sys.argv[1] # komentoriviltä
	tiedostot = sys.argv[1:]
	muuttujat = []
	
#	for tiedostonimi in tiedostot:
#		if os.path.isfile(tiedostonimi):
#			tekstitiedosto = open(tiedostonimi, 'r')
#			etsi_muuttujat(tekstitiedosto.read())
#			#muuttujat += etsi_muuttujat_maarittelyssa(tekstitiedosto)

	NIMIKEKARTTA.update(muodosta_uusi_nimikekartta(muuttujat, VARATUT))

	for tiedostonimi in tiedostot:
		if os.path.isfile(tiedostonimi):
			vientitiedosto = open("munglattu-"+tiedostonimi, 'w+')
			tekstitiedosto = open(tiedostonimi, 'r')
			sisalto = tekstitiedosto.read()
			tekstitiedosto.close()
			sisalto = poista_kommentit(sisalto)
			sisalto = etsi_ja_korvaa_muuttujat(sisalto)
			sisalto = etsi_ja_korvaa_muuttujat_merkkijonoista(sisalto)
#			sisalto = poista_valimerkit(sisalto)
			vientitiedosto.write(sisalto)
			vientitiedosto.close()

#etsi_muuttujat(open(sys.argv[1], 'r'))
#print poista_kommentit("""	events: {		"click": "laajennaVarijyva",    // "click p.rinnakkaisvari": "vaihdaSavyRinnakkaiseen"},sss""")

suoritus()
print NIMIKEKARTTA['savyHEX']
#for nimike in SEURANTAAN:
#	if nimike in NIMIKEKARTTA:
#		print nimike + " JOLLE ON SALANIMI " + NIMIKEKARTTA[nimike]
#	else:
#		nimike

