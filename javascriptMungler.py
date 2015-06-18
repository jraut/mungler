# -*- coding: utf-8 -*-
import re, os, sys

def etsi_muuttujat_maarittelyssa(tiedosto):
	palautus = []
	with tiedosto as t:
		for rivi in t:
			mnimi = etsi_var_muuttujat(rivi)
			# järjestetään pituuden mukaan. Näin nimet eivät korvaa toisiaan "osittain".
			if mnimi: 
				paikka = 0
				for i in palautus:			
					if len(mnimi) > len(i): # Lisättävän paikka löytyi
						palautus.insert(paikka, mnimi)
						break
					paikka += 1
				else:  # saavutetaan vain jos edellinen rekursio menee loppuun asti
					paikka = 0
					palautus.append(mnimi)
	return palautus

#etsi_muuttujat(text = käsiteltävä tekstikatkelma, rivi koodia)
# listaa muuttujat jotka on määritelty "var muuttujanNimi = .." muodossa.
def etsi_var_muuttujat(rivi):
	muuttuja_exp = '^(?P<sisennys>\s*)var\s*(?P<muuttujanimi>\w*)\s*=' 
	palautus = ""
	m = re.match(muuttuja_exp, rivi, re.MULTILINE)
	if m:
		if m.group('muuttujanimi'):
			palautus = m.group('muuttujanimi')
	return palautus

def etsi_muuttujat(teksti):
	a = re.compile(r"""
					(?!
					(///*(?P<kommentti>.*)/*//) |								# ei monirivisissa kommenteissa
					(////(?P<kommentti_yksirivinen>.*)$) |		 				# ei kommenteissa
					("(?P<merkkijono>[^"]*)") |									# ei merkkijonoissa 
					('(?P<merkkijono2>[^']*)') |								# ei merkkijonoissa 
					([$(.*)]|[Math]|[_]|[console]([.](?P<kirjastokutsu>\w+))+) 	# ei tiettyjen kirjastojen muuttujina
					)
					\b(?P<muuttuja>[a-zA-Z]\w+)\b								# sulkeiden sisällä
					""", re.X)
																							# var-määritteessä
#					\(?ms\{.*(?<muuttuja>\w)\s*:.+})  					# objektin ominaisuutena - Tätä ei ehkä tarvitse toteuttaa
#					\(?ms\{.*:[\b^"](?<muuttuja>\w)[\b^"].*}) 			# objektin ominaisuuden arvona
						# osana laskutoimitusta
						# osana parametrilistausta ( )
						# osana objektin arvomäärittelyä {tätäEiMuuteta: muuttuja}

#	a.match(rivi)
	a.sub(kasittely_temp, teksti.read())

def kasittely_temp(match):
	print match.group('kommentti')
	

def muuttujanimi_nimikekartasta(re_match):
	etsittava = re_match.group('muuttuja')
	if etsittava in NIMIKEKARTTA:
		palautus = NIMIKEKARTTA[re_match.group('muuttuja')]

	else:
		palautus = etsittava

	return palautus
		
	
# Aakkoset a-z.
MERKIT = [chr(i) for i in range(ord('a'), ord('z')+1)]	

# Ottaa vastaan listan jossa merkkijonoja ja palauttaa avain-arvo -pareina saman listan.
#	Listan avaimet luodaan järjestyksessä merkeistä a-z: a, b, c, d, ... , aa, ab, ac, ad, ... , ba, bb, bc, ...
#	Todo! Ottaa vastaan re.matcheja jotta tieto paikoista säilyisi. Ei välttämättä tarpeellinen ominaisuus.
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

def korvaa_esiintymat(rivi):
	muuttuja_exp = r'\b(?P<muuttuja>[a-zA-Z]\w+)\b'
	rivi = re.sub(muuttuja_exp, muuttujanimi_nimikekartasta, rivi)
	return rivi
 
VARATUT = [	
	#common usage
	"arguments", "null", "NULL", "true", "false"
	#string functions
	"trim", 
	#array functions
	
	#ECMAScript 6
	"break", "case", "class", "catch", "const", "continue", "debugger", "default", "delete", "do", "else", "export", "extends", "finally", "for", "function", "if", "import", "in", "instanceof", "let", "new", "return", "super", "switch", "this", "throw", "try", "typeof", "var", "void", "while", "with", "yield",
	#Backbone
	"events", "Events", "render", "on", "off", "trigger", "once", "listenTo", "stopListening", "listenToOnce", 
	"Model", "extend", "constructor", "initialize", "get", "set", "escape", "has", "unset", "clear", "id", "idAttribute", "cid", "attributes", "changed", "defaults", "toJSON", "sync", "fetch", "save", "destroy", "Underscore Methods (9)", "validate", "validationError", "isValid", "url", "urlRoot", "parse", "clone", "isNew", "hasChanged", "changedAttributes", "previous", "previousAttributes",
	"Collection", "extend", "model", "modelId", "constructor / initialize", "models", "toJSON", "sync", "add", "remove", "reset", "set", "get", "at", "push", "pop", "unshift", "shift", "slice", "length", "comparator", "sort", "pluck", "where", "findWhere", "url", "parse", "clone", "fetch", "create",
	"Router", "extend", "routes", "constructor / initialize", "route", "navigate", "execute",
	"History", "start",
	"Sync", "Backbone.sync", "Backbone.ajax", "Backbone.emulateHTTP", "Backbone.emulateJSON",
	"View", "extend", "constructor / initialize", "el", "$el", "setElement", "attributes", "$ (jQuery)", "template", "render", "remove", "delegateEvents", "undelegateEvents",
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
	
	for tiedostonimi in tiedostot:
		if os.path.isfile(tiedostonimi):
			tekstitiedosto = open(tiedostonimi, 'r')
			muuttujat += etsi_muuttujat_maarittelyssa(tekstitiedosto)

	NIMIKEKARTTA.update(muodosta_uusi_nimikekartta(muuttujat, VARATUT))

	for tiedostonimi in tiedostot:
		if os.path.isfile(tiedostonimi):
			vientitiedosto = open("munglattu-"+tiedostonimi, 'w+')
			tekstitiedosto = open(tiedostonimi, 'r')
			sisalto = korvaa_esiintymat(tekstitiedosto.read())
			tekstitiedosto.close()
			vientitiedosto.write(sisalto)
			vientitiedosto.close()

#etsi_muuttujat(open(sys.argv[1], 'r'))

suoritus()
	
