# -*- coding: utf-8 -*-
import re, os, sys

#etsi_muuttujat(text = käsiteltävä tekstikatkelma, rivi koodia)
# listaa muuttujat jotka on määritelty "var muuttujanNimi = .." muodossa.
def etsi_muuttujat(text):
	# etsitään muuttujien nimiä. Kerran per rivi. 
	muuttujaExp = '^(?P<sisennys>\s*)var\s*(?P<muuttujanimi>\w*)\s*=' 
	palautus = ""
	# vain yksi haku per rivi: aloitetaan rivin alusta ja siksi re.match
	m = re.match(muuttujaExp, text, re.MULTILINE)
	if m:
#		if m.group('sisennys'):
#			print m.start('sisennys')
		if m.group('muuttujanimi'):
			palautus = m.group('muuttujanimi')
#			print m.start('muuttujanimi')
#			print m.end('muuttujanimi')
#			print m.group('muuttujanimi');
#			print match
#		print [m.start(0):m.end(0)]
	return palautus

    
# Aakkoset a-z.
MERKIT = [chr(i) for i in range(ord('a'), ord('z')+1)]	

# Ottaa vastaan listan jossa merkkijonoja ja palauttaa avain-arvo -pareina saman listan.
#	Listan avaimet luodaan järjestyksessä merkeistä a-z: a, b, c, d, ... , aa, ab, ac, ad, ... , ba, bb, bc, ...
#	Todo! Ottaa vastaan re.matcheja jotta tieto paikoista säilyisi. Ei välttämättä tarpeellinen ominaisuus.
def muodosta_uusi_nimikekartta(muuttujanimikkeet):
	nimike = ""
	monesko = 0
	palautus = {}
	for mn in muuttujanimikkeet:
		monesko += 1
		nimike = lukujarjestelmasta_toiseen(monesko, MERKIT)
		palautus[mn] = nimike
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
		
# SUORITUS:
#	-otetaan sotkettava tiedosto komentoriviltä argumenttina. 
#	-haetaan sen muuttujien määritellyt nimet. 
#	-luodaan niille hakemisto, joissa uudet nimet.
tiedostonimi = sys.argv[1] # komentoriviltä
if os.path.isfile(tiedostonimi):
	palautus = []
	with open(tiedostonimi) as t:
		for rivi in t:
			mnimi = etsi_muuttujat(rivi)
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

#	print palautus;		
	muodosta_uusi_nimikekartta(palautus);
	
#	t = open(tiedostonimi, 'r')
#	tiedosto = t.read()
#	print tiedosto
#	etsi_muuttujat(tiedosto)
			
#find_variables(parametri)
