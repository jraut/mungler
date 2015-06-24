# -*- coding: utf-8 -*-
import re, os, sys
	
def etsi_ja_korvaa_muuttujat(teksti):
	a = re.compile(r"""
					(?P<kommentti>(\/\* .*? \*\/) | (\/\/.*?$))	|											# Moniriviset ja yksiriviset kommentit.
# 					.get|.set\(['"](?P<muuttuja>)["']\)														# tietynmuotoiset Backbone-kutsut: get- ja set. get('muuttuja')
					events:\s*\{(?P<eventmap>.*?)\}			|												# Merkkijonot voivat sisältää muuttujan: backbone.js: osana funktiomäärittelyn events-mappia.	
					(?P<merkkijono>((?P<merkkijononalkumerkki>["']).*?(?P=merkkijononalkumerkki))) |		# Merkkijonot eivät normaalisti sisällä. (greedy: ei erottele sisättäisiä merkkijonoja
					(?P<kirjastokutsu>((\$\(.*?\))|(Backbone)|(Math)|(_)|(console))([.]\w*)*) |				# Kirjastokutsujen metodit ovat sellaisinaan
					\b(?P<muuttuja>[a-zA-Z]\w*)\b 															# Loput ilmaisut ovat muuttujia. Eivät ala kuin kirjaimella.
																
					""", re.X|re.M|re.S)
																							# var-määritteessä
#					\(?ms\{.*(?<muuttuja>\w)\s*:.+})  					# objektin ominaisuutena - Tätä ei ehkä tarvitse toteuttaa
#					\(?ms\{.*:[\b^"](?<muuttuja>\w)[\b^"].*}) 			# objektin ominaisuuden arvona
						# osana laskutoimitusta
						# osana parametrilistausta ( )
						# osana objektin arvomäärittelyä {tätäEiMuuteta: muuttuja}

#	a.match(rivi)
	return a.sub(kasittely_re_korvaukselle, teksti)

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
	if re_osumat['kommentti']:
		return ""
	if re_osumat['merkkijono']:
		return re_osumat['merkkijono']#return kasittely_merkkijonoille(match)
	if re_osumat['kirjastokutsu']:
		return re_osumat['kirjastokutsu']
		return kasittely_kirjastokutsuille(match)
	if re_osumat['muuttuja']:
		return kasittely_muuttujille(match)	
	return "";
	
#	korvattavat_ryhmat = ['muuttuja', 'kommentti', 'merkkijono', 'kirjastokutsu']
#		for ryhma in korvattavat_ryhmat:
#			if ryhma in match.groups():
#				return match.group(ryhma)

def kasittely_muuttujille(match):
	etsittava = match.group('muuttuja')
	if etsittava in VARATUT:
		return etsittava
	if etsittava not in NIMIKEKARTTA:
		monesko = len(NIMIKEKARTTA)								# Monesko oma lisättävä nimikekarttaan tulee.
		nimike = lukujarjestelmasta_toiseen(monesko, MERKIT)	# Haetaan uusi nimike 
		NIMIKEKARTTA[etsittava] = nimike						# Tallennetaan uusi nimike 
	return NIMIKEKARTTA[match.group('muuttuja')]
	
	
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


VARATUT = [	
	#common usage
	"arguments", "null", "NULL", "true", "false"
	#string functions
	"trim", 
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
	]
	
		
		
# SUORITUS:
#	-otetaan sotkettava tiedosto komentoriviltä argumenttina. 
#	-haetaan sen muuttujien määritellyt nimet. 
#	-luodaan niille hakemisto, joissa uudet nimet.

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
			sisalto = etsi_ja_korvaa_muuttujat(tekstitiedosto.read())
			tekstitiedosto.close()
			vientitiedosto.write(sisalto)
			vientitiedosto.close()

#etsi_muuttujat(open(sys.argv[1], 'r'))
suoritus()



