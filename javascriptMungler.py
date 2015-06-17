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

def etsi_muuttujat_kaytossa(rivi):
	a = re.compile(r"""	# sulkeiden sisällä
						# var-määritteessä
						# objektin ominaisuutena - Tätä ei ehkä tarvitse toteuttaa
						# osana laskutoimitusta
						# osana parametrilistausta ( )
						# osana objektin arvomäärittelyä {tätäEiMuuteta: muuttuja}
					""", re.X)
	a.match(rivi)
	
def korvaa_rivin_muuttujat(rivi):
	muuttuja_exp = r'\b(?P<muuttuja>\w+)\b'
	rivi = re.sub(muuttuja_exp, muuttujanimi_nimikekartasta, rivi)
	return rivi
 
def muuttujanimi_nimikekartasta(re_match):
	etsittava = re_match.group('muuttuja')
	if etsittava in nimikekartta:
		palautus = nimikekartta[re_match.group('muuttuja')]
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

def korvaa_esiintymat_legacy(teksti, korvaukset):
    for i, j in korvaukset.iteritems():
        teksti = teksti.replace(i, j)
    return teksti

def korvaa_esiintymat(teksti):
	print korvaa_rivin_muuttujat(teksti)
 

VARATUT = [	#Backbone
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
tiedostonimi = sys.argv[1] # komentoriviltä
if os.path.isfile(tiedostonimi):
	tekstitiedosto = open(tiedostonimi, 'r')
	muuttujat = etsi_muuttujat_maarittelyssa(tekstitiedosto)
	nimikekartta = muodosta_uusi_nimikekartta(muuttujat, VARATUT)
	tekstitiedosto = open(tiedostonimi, 'rw')
	print korvaa_esiintymat(tekstitiedosto.read())
#	print korvaa_esiintymat_legacy(tekstitiedosto.read(), nimikekartta)
	
