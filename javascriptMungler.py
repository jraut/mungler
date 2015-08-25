#kis-*- coding: utf-8 -*-
import re, os, sys

def onTyyppia(tiedostonimi, paate):
	return tiedostonimi.endswith(paate)
	#return tiedostonimi.split(".")[-1].find(paate) > -1	

def poista_konsolirivit(teksti):
	return re.sub(r"(?xms)(?P<konsolirivi>^.*?console\..*?$)", "", teksti)

def poista_kommentit(teksti):
	return re.sub(r"(?xms)(?P<kommentti>(\/\*.*?\*\/)|(\/\/.*?$))", "",teksti)

def poista_valimerkit(teksti):
	a = re.compile(r"""
					(?P<edeltaja>\S*)\s+(?P<vikaKirjain>.)\s+$
					""", re.X|re.S)
	def valimerkinpoisto(match):
		osumat = match.groupdict()
		palautus = osumat['edeltaja']
		if osumat['edeltaja'] in VARATUT:
			palautus += " "
		if osumat['vikaKirjain']:
			palautus += " "
		return palautus			
	return a.sub(valimerkinpoisto, teksti)

def etsi_ja_korvaa_muuttujat_htmlsta(teksti):
	a = re.compile(r"""
			(?<=id=")\b(?P<id>(\w|-)+?)(?=") |			
			(?<=class=")(?P<luokka>[^"]*?)(?=") |
			(?<=%-\s)\b(?P<muuttuja>\w+?)\b(?=\s%>) // ASP-tagi.
			
		""", re.X|re.M|re.S)
	def kas(match):
		osumat = match.groupdict()
		if osumat['muuttuja']:
			return kasittely_loydetyille_muuttujille(osumat['muuttuja'])			
		if osumat['id']:
			return kasittely_loydetyille_muuttujille(osumat['id'])
		if osumat['luokka']:
			palautus = ""
			eka = 1
			for osa in osumat['luokka'].split(' '):
				if eka == 0:
					palautus += " "
				palautus += kasittely_loydetyille_muuttujille(osa)
				if eka == 1:
					eka = 0
			return palautus

	return a.sub(kas, teksti)
#	return a.sub(kasittely_loydetyille_muuttujille, teksti)

def etsi_ja_korvaa_muuttujat_phpsta(teksti):
	global NIMIKEKARTTA 
	a = re.compile(r"""
			(?P<merkkijononalkumerkki>["'])
			(?P<merkkijono>([^(?P=merkkijononalkumerkki)]+?))
			(?P=merkkijononalkumerkki)
		""", re.X|re.M|re.S)
	def kas(match):
		if match.group('merkkijono') in NIMIKEKARTTA:
			return NIMIKEKARTTA[match.group('merkkijono')]
	return a.sub(kas, teksti)	

def etsi_ja_korvaa_muuttujat_csssta(teksti):
	a = re.compile(r"""
			(?P<lauseke>\{[^}]*?\}) |
			(?<=\#)(?P<id>\w+)\b |			
			(?<=\.)(?P<luokka>\w+)\b
			
		""", re.X|re.M|re.S)
	def kas(match):
		if match.group('lauseke'):
			return match.group('lauseke')
		elif match.group('id'):
			return kasittely_loydetyille_muuttujille(match.group('id'))
		elif match.group('luokka'):
			return kasittely_loydetyille_muuttujille(
					match.group('luokka'))
	return a.sub(kas, teksti)

def etsi_ja_korvaa_muuttujat_pehmoisesti(teksti):
	global NIMIKEKARTTA 
	a = re.compile(r"""
			(?P<merkkijononalkumerkki>["'])
			(?P<merkkijono>.*?)
			(?P=merkkijononalkumerkki)
		""", re.X|re.M|re.S)
	def kas(match):
		if match.group('merkkijono') in NIMIKEKARTTA:
			return (match.group('merkkijononalkumerkki') + 
			NIMIKEKARTTA[match.group('merkkijono')] + 
			match.group('merkkijononalkumerkki'))
		else:
			return (match.group('merkkijononalkumerkki') + 
			match.group('merkkijono') + 
			match.group('merkkijononalkumerkki'))
	return a.sub(kas, teksti)	

def etsi_muuttujat_merkkijonosta(teksti):
	a = re.compile(r"""
#			\b(\.\w+)\b | 					// className
#			\b(\#\w+)\b | 					// idName or hex
#			\brgb[a]?([^)]*? ([(][^)]*?[)])*? [^)]*?)\b | 	// rgb-string
#			\b.|.#|rgb[a]?([^)]*? ([(][^)]*?[)])*? [^)]*?){0,0}
			(?<!\/)\b(?P<muuttuja>[a-zA-Z]\w*)\b 				
		""", re.X|re.M|re.S)

	return a.sub(kasittely_loydetyille_muuttujille, teksti)

def etsi_muuttujat(teksti, softly = False):
	toimenpide = ei_tallenneta if softly else tallenna_muuttujat 
	a = re.compile(r"""
					(?P<merkkijononalkumerkki>["'])
					(?P<merkkijono>([^(?P=merkkijononalkumerkki)]+?))
					(?P=merkkijononalkumerkki) |	
					\{(?P<objekti>[^}]*? (\{[^}]*?\})*? [^}]+? )\} |		
					\((?P<kutsu> ([(][^)]*?[)])*? [^)]+? )\) |				
					(?<!\/)\b(?P<muuttuja>[a-zA-Z](\w|-)*)\b 				
																
					""", re.X|re.M|re.S)

	return a.sub(toimenpide, teksti)

def tallenna_muuttujat(match):
	re_osumat = match.groupdict();
	if re_osumat['merkkijono']:
		return (re_osumat['merkkijononalkumerkki']+
		etsi_muuttujat_merkkijonosta(re_osumat['merkkijono'])+
		re_osumat['merkkijononalkumerkki'])
	if re_osumat['muuttuja']:
		return kasittely_loydetyille_muuttujille(match.group('muuttuja'))
	if re_osumat['objekti']:
		return '{'+etsi_muuttujat(re_osumat['objekti'])+'}'
	if re_osumat['kutsu']:
		return '('+etsi_muuttujat(re_osumat['kutsu'])+')'
	return "";

def ei_tallenneta(match):
	
	re_osumat = match.groupdict();
	if re_osumat['merkkijono']:
		muuttuja = re_osumat['merkkijono']
		return (re_osumat['merkkijononalkumerkki']+
		(NIMIKEKARTTA[muuttuja] if 
			(muuttuja in NIMIKEKARTTA) else 
			muuttuja)+re_osumat['merkkijononalkumerkki'])
	if re_osumat['muuttuja']:
		muuttuja = re_osumat['muuttuja']
		return NIMIKEKARTTA[muuttuja] if (
			(muuttuja in NIMIKEKARTTA)) else muuttuja
	if re_osumat['objekti']:
		return '{'+etsi_muuttujat(re_osumat['objekti'], True)+'}'
	if re_osumat['kutsu']:
		return '('+etsi_muuttujat(re_osumat['kutsu'], True)+')'
	return "";
	
def kasittely_loydetyille_muuttujille(muuttuja):
	global NIMIKEKARTTA, VARATUT;
	if type(muuttuja) is not str: 
		muuttuja = muuttuja.group('muuttuja')
	if muuttuja in VARATUT:
		return muuttuja
	if muuttuja not in NIMIKEKARTTA:
		nimike = "" 
		while (nimike == "") or (nimike in VARATUT):
			nimike = seuraava_nimike()

		NIMIKEKARTTA[muuttuja] = nimike	
		return nimike
	return NIMIKEKARTTA[muuttuja]


# Aakkoset a-z.
MERKIT = [chr(i) for i in range(ord('a'), ord('z')+1)]	

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

NIMIKKEITA = 0
def seuraava_nimike():
	global NIMIKKEITA
	NIMIKKEITA += 1
	return lukujarjestelmasta_toiseen(NIMIKKEITA, MERKIT)

def lue_muunnoskartta(tiedostonimi):
	global NIMIKEKARTTA, NIMIKKEITA
	if os.path.isfile(tiedostonimi):
			teksti = open(tiedostonimi, 'r').read()
	if (teksti):
		a = re.compile(r"""
			^(?P<alkuperainen>\w+):\s*(?P<munglattu>\w+)$""", re.M)
		for match in a.finditer(teksti):
			NIMIKEKARTTA[match.group(1)] = match.group(2)
	NIMIKKEITA = len(NIMIKEKARTTA)
	return NIMIKEKARTTA 
	
VARATUT = (	
	#More missing dom stuff:
	"DOMActivate", 
	#jQuery effect
	"effect", "direction", "blind",  
	""""paletti", "savyHEX", 'koostumus', 'taysi', # 'oma', 'savyja', 
	'alisavyja', 'taysi', 'hex', 'savyHEX', 'rinnakkaisvarit', 'alivarit', 
	'rinnakkaisuus', 'varijyva', 'varikartta', 'suljeNappiKehys', 'linkki', 
	'taysiTaytto', 'varinOtsikko', 'settiValitsin', 'settivalitsimet', 
	'variasetukset', "savyvalitsin", "kyllaisyysvalitsin", "kirkkausvalitsin", 
	"varihex", "varinsaatimet", "varisaatimenPykala", "piilotettu", "vaihda", 
	"eiKaytossa", "linkki",
	"""
	#Randoms: css-property values
	'cover', 'hover', 'auto', 'inline-block', "scroll", "hidden", "overflow", 
	'block', 'clientX', 'clientY', "hsl", "rgb", "hsla", "rgba", "ffffff", 
	"000000", "c0c0c0", "af4f4f", 'light', 'source-over', "transparent",
	#HTML-elements
	'body', 'html', 'head', 'li', 'ul', 'div', 'p', 'canvas', 'h1', 'h2', 
	'button', 
	#common js-usage
	"arguments", "null", "NULL", "true", "false", "undefined", "NaN", 
	"Infinity", "toString", "console", "log", "apply", "setTimeout", 
	"clearTimeout", "window", "toPrecision", "setInterval", "setTimeout",
	#Firebug console
	"console", "log", "debug", "info", "warn", "exception", "assert", "dir", 
	"dirxml", "trace", "group", "groupCollapsed", "groupEnd", "profile", 
	"profileEnd", "count", "clear", "time", "timeEnd", "timeStamp", "table", 
	"error",
	#Math
	"Math", "toSource", "abs", "acos", "asin", "atan", "atan2", "ceil", 
	"clz32", "cos", "exp", "floor", "imul", "fround", "log", "max", "min", 
	"pow", "random", "round", "sin", "sqrt", "tan", "log10", "log2", "log1p", 
	"expm1", "cosh", "sinh", "tanh", "acosh", "asinh", "atanh", "hypot", 
	"trunc", "sign", "cbrt", "E", "LOG2E", "LOG10E", "LN2", "LN10", "PI", 
	"SQRT2", "SQRT1_2",
	#Number
	"Number", "prototype", "NaN", "POSITIVE_INFINITY", "NEGATIVE_INFINITY", 
	"MAX_VALUE", "MIN_VALUE", "MAX_SAFE_INTEGER", "MIN_SAFE_INTEGER", 
	"EPSILON", "isFinite", "isInteger", "isNaN", "isSafeInteger", 
	"parseFloat", "parseInt", "length", "name",	
	#Object
	"Object", "getPrototypeOf", "setPrototypeOf", "getOwnPropertyDescriptor", 
	"keys", "is", "defineProperty", "defineProperties", "create", 
	"getOwnPropertyNames", "getOwnPropertySymbols", "isExtensible", 
	"preventExtensions", "freeze", "isFrozen", "seal", "isSealed", 
	"prototype", "assign", "name", "length",
	#String
	"String", "prototype", "toLowerCase", "toUpperCase", "charAt", 
	"charCodeAt", "contains", "indexOf", "lastIndexOf", "startsWith", 
	"endsWith", "trim", "trimLeft", "trimRight", "toLocaleLowerCase", 
	"toLocaleUpperCase", "normalize", "match", "search", "replace", "split",
	"concat", "fromCharCode", "fromCodePoint", "raw", "substring", "substr", 
	"slice", "localeCompare", "length", "name", 
	#Array
	"Array", "join", "reverse", "sort", "push", "pop", "shift", "unshift", 
	"splice", "concat", "slice", "filter", "isArray", "lastIndexOf", 
	"indexOf", "forEach", "map", "every", "some", "reduce", "reduceRight", 
	"from", "of", "prototype", "length", "name",
	#Event
	"stopPropagation", "stopImmediatePropagation", "preventDefault", 
	"initEvent", "getPreventDefault", "type", "target", "currentTarget", 
	"eventPhase", "bubbles", "cancelable", "defaultPrevented", "timeStamp", 
	"originalTarget", "explicitOriginalTarget", "NONE", "CAPTURING_PHASE", 
	"AT_TARGET", "BUBBLING_PHASE", "ALT_MASK", "CONTROL_MASK", "SHIFT_MASK", 
	"META_MASK", "constructor",
	# Canvas:
	"addColorStop", "arc", "arcTo", "beginPath", "bezierCurveTo", 
	"clearRect", "clip", "closePath", "createImageData", 
	"createLinearGradient", "createPattern", "createRadialGradient", 
	"drawImage", "fill", "fillRect", "fillText", "getContext", 
	"getImageData", "isPointInPath", "lineTo", "measureText", "moveTo", 
	"putImageData", "quadraticCurveTo", "rect", "restore", "rotate", "save", 
	"scale", "setTransform", "stroke", "stokeRect", "strokeText", 
	"toDataURL", "transform", "translate", "fillStyle", "globalAlpha", 
	"globalCompositeOperation", "lineCap", "lineJoin", "lineWidth", 
	"miterLimit", "shadowBlur", "shadowColor", "shadowOffsetX", 
	"shadowOffsetY", "width", "height", "strokeStyle", "textAlign", 
	"textBaseline", 
	#ECMAScript 6
	"break", "case", "class", "catch", "const", "continue", "debugger", 
	"default", "delete", "do", "else", "export", "extends", "finally", 
	"for", "function", "if", "import", "in", "instanceof", "let", "new", 
	"return", "super", "switch", "this", "throw", "try", "typeof", "var", 
	"void", "while", "with", "yield",
	#canvas context
	"save", "restore", "scale", "rotate", "translate", "transform", 
	"setTransform", "resetTransform", "createLinearGradient", 
	"createRadialGradient", "createPattern", "clearRect", "fillRect", 
	"strokeRect", "beginPath", "fill", "stroke", "drawFocusIfNeeded", 
	"clip", "isPointInPath", "isPointInStroke", "fillText", "strokeText", 
	"measureText", "drawImage", "createImageData", "getImageData", 
	"putImageData", "setLineDash", "getLineDash", "closePath", "moveTo", 
	"lineTo", "quadraticCurveTo", "bezierCurveTo", "arcTo", "rect", "arc", 
	"canvas", "globalAlpha", "globalCompositeOperation", "strokeStyle", 
	"fillStyle", "shadowOffsetX", "shadowOffsetY", "shadowBlur", 
	"shadowColor", "mozCurrentTransform", "mozCurrentTransformInverse", 
	"mozFillRule", "mozDash", "mozDashOffset", "mozTextStyle", 
	"mozImageSmoothingEnabled", "lineWidth", "lineCap", "lineJoin", 
	"miterLimit", "lineDashOffset", "font", "textAlign", "textBaseline", 
	#canvas + generic DOM 
	"getContext", "toDataURL", "toBlob", "mozGetAsFile", "width", "height", 
	"mozOpaque", "mozPrintCallback", "click", "focus", "blur", "title", 
	"lang", "dir", "dataset", "itemScope", "itemType", "itemId", "itemRef", 
	"itemProp", "properties", "itemValue", "hidden", "tabIndex", "accessKey", 
	"accessKeyLabel", "draggable", "contentEditable", "isContentEditable", 
	"contextMenu", "spellcheck", "style", "oncopy", "oncut", "onpaste", 
	"offsetParent", "offsetTop", "offsetLeft", "offsetWidth", "offsetHeight", 
	"onabort", "onblur", "onfocus", "oncanplay", "oncanplaythrough", 
	"onchange", "onclick", "oncontextmenu", "ondblclick", "ondrag", 
	"ondragend", "ondragenter", "ondragleave", "ondragover", "ondragstart", 
	"ondrop", "ondurationchange", "onemptied", "onended", "oninput", 
	"oninvalid", "onkeydown", "onkeypress", "onkeyup", "onload", 
	"onloadeddata", "onloadedmetadata", "onloadstart", "onmousedown", 
	"onmouseenter", "onmouseleave", "onmousemove", "onmouseout", 
	"onmouseover", "onmouseup", "onpause", "onplay", "onplaying", 
	"onprogress", "onratechange", "onreset", "onresize", "onscroll", 
	"onseeked", "onseeking", "onselect", "onshow", "onstalled", "onsubmit", 
	"onsuspend", "ontimeupdate", "onvolumechange", "onwaiting", 
	"onmozfullscreenchange", "onmozfullscreenerror", 
	"onmozpointerlockchange", "onmozpointerlockerror", "onerror", 
	"getAttribute", "getAttributeNS", "setAttribute", "setAttributeNS", 
	"removeAttribute", "removeAttributeNS", "hasAttribute", "hasAttributeNS", 
	"hasAttributes", "closest", "matches", "getElementsByTagName", 
	"getElementsByTagNameNS", "getElementsByClassName", "mozMatchesSelector", 
	"setCapture", "releaseCapture", "mozRequestFullScreen", 
	"mozRequestPointerLock", "getAttributeNode", "setAttributeNode", 
	"removeAttributeNode", "getAttributeNodeNS", "setAttributeNodeNS", 
	"getClientRects", "getBoundingClientRect", "scrollIntoView", "scroll", 
	"scrollTo", "scrollBy", "insertAdjacentHTML", "querySelector", 
	"querySelectorAll", "remove", "tagName", "id", "className", "classList", 
	"attributes", "onwheel", "scrollTop", "scrollLeft", "scrollWidth", 
	"scrollHeight", "clientTop", "clientLeft", "clientWidth", "clientHeight", 
	"scrollTopMax", "scrollLeftMax", "innerHTML", "outerHTML", 
	"previousElementSibling", "nextElementSibling", "children", 
	"firstElementChild", "lastElementChild", "childElementCount", 
	"hasChildNodes", "insertBefore", "appendChild", "replaceChild", 
	"removeChild", "normalize", "cloneNode", "isEqualNode", 
	"compareDocumentPosition", "contains", "lookupPrefix", 
	"lookupNamespaceURI", "isDefaultNamespace", "nodeType", "nodeName", 
	"baseURI", "ownerDocument", "parentNode", "parentElement", "childNodes", 
	"firstChild", "lastChild", "previousSibling", "nextSibling", "nodeValue", 
	"textContent", "namespaceURI", "prefix", "localName", "ELEMENT_NODE", 
	"ATTRIBUTE_NODE", "TEXT_NODE", "CDATA_SECTION_NODE", 
	"ENTITY_REFERENCE_NODE", "ENTITY_NODE", "PROCESSING_INSTRUCTION_NODE", 
	"COMMENT_NODE", "DOCUMENT_NODE", "DOCUMENT_TYPE_NODE", 
	"DOCUMENT_FRAGMENT_NODE", "NOTATION_NODE", 
	"DOCUMENT_POSITION_DISCONNECTED", "DOCUMENT_POSITION_PRECEDING", 
	"DOCUMENT_POSITION_FOLLOWING", "DOCUMENT_POSITION_CONTAINS", 
	"DOCUMENT_POSITION_CONTAINED_BY", 
	"DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC", "addEventListener", 
	"removeEventListener", "dispatchEvent",
	#jQuery Event 1.11 
	"$", "isDefaultPrevented", "isPropagationStopped", 
	"isImmediatePropagationStopped", "preventDefault", "stopPropagation", 
	"stopImmediatePropagation",	
	#jQuery 1.11 
	"prototype", "fn", "extend", "expando", "isReady", "error", "noop", 
	"isFunction", "isArray", "isWindow", "isNumeric", "isEmptyObject", 
	"isPlainObject", "type", "globalEval", "camelCase", "nodeName", "each", 
	"trim", "makeArray", "inArray", "merge", "grep", "map", "guid", "proxy", 
	"now", "support", "find", "expr", "unique", "text", "isXMLDoc", 
	"contains", "filter", "dir", "sibling", "Callbacks", "Deferred", "when", 
	"readyWait", "holdReady", "ready", "acceptData", "cache", "noData", 
	"hasData", "data", "removeData", "_data", "_removeData", "queue", 
	"dequeue", "_queueHooks", "access", "event", "removeEvent", "Event", 
	"clone", "buildFragment", "cleanData", "swap", "cssHooks", "cssNumber", 
	"cssProps", "style", "css", "Tween", "easing", "fx", "Animation", 
	"speed", "timers", "valHooks", "attr", "removeAttr", "attrHooks", 
	"propFix", "prop", "propHooks", "parseJSON", "parseXML", "active", 
	"lastModified", "etag", "ajaxSettings", "ajaxSetup", "ajaxPrefilter", 
	"ajaxTransport", "ajax", "getJSON", "getScript", "get", "post", 
	"_evalUrl", "param", "parseHTML", "offset", "noConflict", "effects", 
	"Color", "length", "name",
	#jQuery("body") 1.11
	"length", "prevObject", "context", "selector", "constructor", "init", 
	"jquery", "size", "toArray", "get", "pushStack", "each", "ready", "eq", 
	"first", "last", "slice", "map", "end", "push", "sort", "splice", 
	"extend", "data", "removeData", "queue", "dequeue", "delay", 
	"clearQueue", "promise", "attr", "removeAttr", "prop", "removeProp", 
	"addClass", "removeClass", "toggleClass", "hasClass", "val", "on", "one", 
	"off", "bind", "unbind", "live", "die", "delegate", "undelegate", 
	"trigger", "triggerHandler", "toggle", "hover", "blur", "focus", 
	"focusin", "focusout", "load", "resize", "scroll", "unload", "click", 
	"dblclick", "mousedown", "mouseup", "mousemove", "mouseover", "mouseout", 
	"mouseenter", "mouseleave", "change", "select", "submit", "keydown", 
	"keypress", "keyup", "error", "contextmenu", "find", "has", "not", 
	"filter", "is", "closest", "index", "add", "addBack", "andSelf", 
	"parent", "parents", "parentsUntil", "next", "prev", "nextAll", 
	"prevAll", "nextUntil", "prevUntil", "siblings", "children", "contents", 
	"text", "wrapAll", "wrapInner", "wrap", "unwrap", "append", "prepend", 
	"before", "after", "remove", "empty", "clone", "html", "replaceWith", 
	"detach", "domManip", "appendTo", "prependTo", "insertBefore", 
	"insertAfter", "replaceAll", "css", "show", "hide", "serialize", 
	"serializeArray", "ajaxStart", "ajaxStop", "ajaxComplete", "ajaxError", 
	"ajaxSuccess", "ajaxSend", "fadeTo", "animate", "stop", "slideDown", 
	"slideUp", "slideToggle", "fadeIn", "fadeOut", "fadeToggle", "offset", 
	"position", "offsetParent", "scrollLeft", "scrollTop", "innerHeight", 
	"height", "outerHeight", "innerWidth", "width", "outerWidth", 
	"highlightText",
	#body.style dom-pproperties
	"MozAppearance", "MozOutlineRadius", "MozOutlineRadiusTopleft", 
	"MozOutlineRadiusTopright", "MozOutlineRadiusBottomright", 
	"MozOutlineRadiusBottomleft", "MozTabSize", "all", "animation", 
	"animationDelay", "animation-delay", "animationDirection", 
	"animation-direction", "animationDuration", "animation-duration", 
	"animationFillMode", "animation-fill-mode", "animationIterationCount", 
	"animation-iteration-count", "animationName", "animation-name", 
	"animationPlayState", "animation-play-state", "animationTimingFunction", 
	"animation-timing-function", "background", "backgroundAttachment", 
	"background-attachment", "backgroundClip", "background-clip", 
	"backgroundColor", "background-color", "backgroundImage", 
	"background-image", "backgroundBlendMode", "background-blend-mode", 
	"backgroundOrigin", "background-origin", "backgroundPosition", 
	"background-position", "backgroundRepeat", "background-repeat", 
	"backgroundSize", "background-size", "MozBinding", "border", 
	"borderBottom", "border-bottom", "borderBottomColor", 
	"border-bottom-color", "MozBorderBottomColors", "borderBottomStyle", 
	"border-bottom-style", "borderBottomWidth", "border-bottom-width", 
	"borderCollapse", "border-collapse", "borderColor", "border-color", 
	"borderImage", "border-image", "borderImageSource", 
	"border-image-source", "borderImageSlice", "border-image-slice", 
	"borderImageWidth", "border-image-width", "borderImageOutset", 
	"border-image-outset", "borderImageRepeat", "border-image-repeat", 
	"MozBorderEnd", "MozBorderEndColor", "MozBorderEndStyle", 
	"MozBorderEndWidth", "MozBorderStart", "MozBorderStartColor", 
	"MozBorderStartStyle", "MozBorderStartWidth", "borderLeft", 
	"border-left", "borderLeftColor", "border-left-color", 
	"MozBorderLeftColors", "borderLeftStyle", "border-left-style", 
	"borderLeftWidth", "border-left-width", "borderRight", "border-right", 
	"borderRightColor", "border-right-color", "MozBorderRightColors", 
	"borderRightStyle", "border-right-style", "borderRightWidth", 
	"border-right-width", "borderSpacing", "border-spacing", "borderStyle", 
	"border-style", "borderTop", "border-top", "borderTopColor", 
	"border-top-color", "MozBorderTopColors", "borderTopStyle", 
	"border-top-style", "borderTopWidth", "border-top-width", "borderWidth", 
	"border-width", "borderRadius", "border-radius", "borderTopLeftRadius", 
	"border-top-left-radius", "borderTopRightRadius", 
	"border-top-right-radius", "borderBottomRightRadius", 
	"border-bottom-right-radius", "borderBottomLeftRadius", 
	"border-bottom-left-radius", "bottom", "boxDecorationBreak", 
	"box-decoration-break", "boxShadow", "box-shadow", "boxSizing", 
	"box-sizing", "captionSide", "caption-side", "clear", "clip", "color", 
	"MozColumns", "MozColumnCount", "MozColumnFill", "MozColumnWidth", 
	"MozColumnGap", "MozColumnRule", "MozColumnRuleColor", 
	"MozColumnRuleStyle", "MozColumnRuleWidth", "content", 
	"counterIncrement", "counter-increment", "counterReset", "counter-reset", 
	"cursor", "direction", "display", "emptyCells", "empty-cells", 
	"alignContent", "align-content", "alignItems", "align-items", 
	"alignSelf", "align-self", "flex", "flexBasis", "flex-basis", 
	"flexDirection", "flex-direction", "flexFlow", "flex-flow", "flexGrow", 
	"flex-grow", "flexShrink", "flex-shrink", "flexWrap", "flex-wrap", 
	"order", "justifyContent", "justify-content", "cssFloat", "float", 
	"MozFloatEdge", "font", "fontFamily", "font-family", 
	"fontFeatureSettings", "font-feature-settings", "fontKerning", 
	"font-kerning", "fontLanguageOverride", "font-language-override", 
	"fontSize", "font-size", "fontSizeAdjust", "font-size-adjust", 
	"fontStretch", "font-stretch", "fontStyle", "font-style", 
	"fontSynthesis", "font-synthesis", "fontVariant", "font-variant", 
	"fontVariantAlternates", "font-variant-alternates", "fontVariantCaps", 
	"font-variant-caps", "fontVariantEastAsian", "font-variant-east-asian", 
	"fontVariantLigatures", "font-variant-ligatures", "fontVariantNumeric", 
	"font-variant-numeric", "fontVariantPosition", "font-variant-position", 
	"fontWeight", "font-weight", "MozForceBrokenImageIcon", "height", 
	"imageOrientation", "image-orientation", "MozImageRegion", "imeMode", 
	"ime-mode", "left", "letterSpacing", "letter-spacing", "lineHeight", 
	"line-height", "listStyle", "list-style", "listStyleImage", 
	"list-style-image", "listStylePosition", "list-style-position", 
	"listStyleType", "list-style-type", "margin", "marginBottom", 
	"margin-bottom", "MozMarginEnd", "MozMarginStart", "marginLeft", 
	"margin-left", "marginRight", "margin-right", "marginTop", "margin-top", 
	"markerOffset", "marker-offset", "marks", "maxHeight", "max-height", 
	"maxWidth", "max-width", "minHeight", "min-height", "minWidth", 
	"min-width", "mixBlendMode", "mix-blend-mode", "isolation", "objectFit", 
	"object-fit", "objectPosition", "object-position", "opacity", 
	"MozOrient", "orphans", "outline", "outlineColor", "outline-color", 
	"outlineStyle", "outline-style", "outlineWidth", "outline-width", 
	"outlineOffset", "outline-offset", "overflow", "overflowX", "overflow-x", 
	"overflowY", "overflow-y", "padding", "paddingBottom", "padding-bottom", 
	"MozPaddingEnd", "MozPaddingStart", "paddingLeft", "padding-left", 
	"paddingRight", "padding-right", "paddingTop", "padding-top", "page", 
	"pageBreakAfter", "page-break-after", "pageBreakBefore", 
	"page-break-before", "pageBreakInside", "page-break-inside", 
	"paintOrder", "paint-order", "pointerEvents", "pointer-events", 
	"position", "quotes", "resize", "right", "rubyAlign", "ruby-align", 
	"rubyPosition", "ruby-position", "scrollBehavior", "scroll-behavior", 
	"size", "tableLayout", "table-layout", "textAlign", "text-align", 
	"MozTextAlignLast", "textDecoration", "text-decoration", 
	"textDecorationColor", "text-decoration-color", "textDecorationLine", 
	"text-decoration-line", "textDecorationStyle", "text-decoration-style", 
	"textIndent", "text-indent", "textOverflow", "text-overflow", 
	"textShadow", "text-shadow", "MozTextSizeAdjust", "textTransform", 
	"text-transform", "transform", "transformOrigin", "transform-origin", 
	"perspectiveOrigin", "perspective-origin", "perspective", 
	"transformStyle", "transform-style", "backfaceVisibility", 
	"backface-visibility", "top", "transition", "transitionDelay", 
	"transition-delay", "transitionDuration", "transition-duration", 
	"transitionProperty", "transition-property", "transitionTimingFunction", 
	"transition-timing-function", "unicodeBidi", "unicode-bidi", 
	"MozUserFocus", "MozUserInput", "MozUserModify", "MozUserSelect", 
	"verticalAlign", "vertical-align", "visibility", "whiteSpace", 
	"white-space", "widows", "width", "MozWindowDragging", "MozWindowShadow", 
	"wordBreak", "word-break", "wordSpacing", "word-spacing", "wordWrap", 
	"word-wrap", "MozHyphens", "zIndex", "z-index", "MozBoxAlign", 
	"MozBoxDirection", "MozBoxFlex", "MozBoxOrient", "MozBoxPack", 
	"MozBoxOrdinalGroup", "MozStackSizing", "clipPath", "clip-path", 
	"clipRule", "clip-rule", "colorInterpolation", "color-interpolation", 
	"colorInterpolationFilters", "color-interpolation-filters", 
	"dominantBaseline", "dominant-baseline", "fill", "fillOpacity", 
	"fill-opacity", "fillRule", "fill-rule", "filter", "floodColor", 
	"flood-color", "floodOpacity", "flood-opacity", "imageRendering", 
	"image-rendering", "lightingColor", "lighting-color", "marker", 
	"markerEnd", "marker-end", "markerMid", "marker-mid", "markerStart", 
	"marker-start", "mask", "maskType", "mask-type", "shapeRendering", 
	"shape-rendering", "stopColor", "stop-color", "stopOpacity", 
	"stop-opacity", "stroke", "strokeDasharray", "stroke-dasharray", 
	"strokeDashoffset", "stroke-dashoffset", "strokeLinecap", 
	"stroke-linecap", "strokeLinejoin", "stroke-linejoin", 
	"strokeMiterlimit", "stroke-miterlimit", "strokeOpacity", 
	"stroke-opacity", "strokeWidth", "stroke-width", "textAnchor", 
	"text-anchor", "textRendering", "text-rendering", "vectorEffect", 
	"vector-effect", "willChange", "will-change", "MozTransform", 
	"MozTransformOrigin", "MozPerspectiveOrigin", "MozPerspective", 
	"MozTransformStyle", "MozBackfaceVisibility", "MozBorderImage", 
	"MozTransition", "MozTransitionDelay", "MozTransitionDuration", 
	"MozTransitionProperty", "MozTransitionTimingFunction", "MozAnimation", 
	"MozAnimationDelay", "MozAnimationDirection", "MozAnimationDuration", 
	"MozAnimationFillMode", "MozAnimationIterationCount", "MozAnimationName", 
	"MozAnimationPlayState", "MozAnimationTimingFunction", "MozBoxSizing", 
	"MozFontFeatureSettings", "MozFontLanguageOverride", 
	"MozTextDecorationColor", "MozTextDecorationLine", 
	"MozTextDecorationStyle", "item", "getPropertyValue", 
	"getPropertyCSSValue", "getPropertyPriority", "setProperty", 
	"removeProperty", "cssText", "length", "parentRule",


	#Backbone
	"Backbone", "events", "Events", "render", "on", "off", "trigger", "once", 
	"listenTo", "stopListening", "listenToOnce", "add", "remove", "update", 
	"reset", "sort", "change", "destroy", "request", "sync", "error", 
	"invalid", "route", "all",
	"Model", "extend", "constructor", "initialize", "get", "set", "escape", 
	"has", "unset", "clear", "id", "idAttribute", "cid", "attributes", 
	"changed", "defaults", "toJSON", "sync", "fetch", "save", "destroy", 
	"validate", "validationError", "isValid", "url", "urlRoot", "parse", 
	"clone", "isNew", "hasChanged", "changedAttributes", "previous", 
	"previousAttributes",
	"Collection", "extend", "model", "modelId", "constructor / initialize", 
	"models", "toJSON", "sync", "add", "remove", "reset", "set", "get", "at", 
	"push", "pop", "unshift", "shift", "slice", "length", "comparator", 
	"sort", "pluck", "where", "findWhere", "url", "parse", "clone", "fetch", 
	"create",
	"Router", "extend", "routes", "constructor / initialize", "route", 
	"navigate", "execute",
	"History", "start",
	"Sync", "Backbone.sync", "Backbone.ajax", "Backbone.emulateHTTP", 
	"Backbone.emulateJSON",
	"View", "extend", "constructor / initialize", "el", "$el", "setElement", 
	"attributes", "$ (jQuery)", "template", "render", "remove", 
	"delegateEvents", "undelegateEvents", "tagName", "className", "id", 
	"model", "collection", "el", "id", "$el",
	"on", "listenTo", "off", "stopListening", "once", "listenToOnce", 
	"trigger", "bind", "unbind", "tagName", "$", "initialize", "render", 
	"remove", "_removeElement", "setElement", "_setElement", 
	"delegateEvents", "delegate", "undelegateEvents", "undelegate", 
	"_createElement", "_ensureElement", "_setAttributes", "extend", 
	"on", "listenTo", "off", "stopListening", "once", "listenToOnce", 
	"trigger", "bind", "unbind", "model", "initialize", "toJSON", "sync", 
	"add", "remove", "set", "reset", "push", "pop", "unshift", "shift", 
	"slice", "get", "at", "where", "findWhere", "sort", "pluck", "fetch", 
	"create", "parse", "clone", "modelId", "_reset", "_prepareModel", 
	"_removeModels", "_isModel", "_addReference", "_removeReference", 
	"_onModelEvent", "forEach", "each", "map", "collect", "reduce", "foldl", 
	"inject", "reduceRight", "foldr", "find", "detect", "filter", "select", 
	"reject", "every", "all", "some", "any", "include", "contains", "invoke", 
	"max", "min", "toArray", "size", "first", "head", "take", "initial", 
	"rest", "tail", "drop", "last", "without", "difference", "indexOf", 
	"shuffle", "lastIndexOf", "isEmpty", "chain", "sample", "partition", 
	"groupBy", "countBy", "sortBy", "indexBy", 
	"on", "listenTo", "off", "stopListening", "once", "listenToOnce", 
	"trigger", "bind", "unbind", "initialize", "route", "execute", 
	"navigate", "_bindRoutes", "_routeToRegExp", "_extractParameters", 
	"on", "listenTo", "off", "stopListening", "once", "listenToOnce", 
	"trigger", "bind", "unbind",
	"on", "listenTo", "off", "stopListening", "once", "listenToOnce", 
	"trigger", "bind", "unbind", "changed", "validationError", "idAttribute", 
	"cidPrefix", "initialize", "toJSON", "sync", "get", "escape", "has", 
	"matches", "set", "unset", "clear", "hasChanged", "changedAttributes", 
	"previous", "previousAttributes", "fetch", "save", "destroy", "url", 
	"parse", "clone", "isNew", "isValid", "_validate", "keys", "values", 
	"pairs", "invert", "pick", "omit", "chain", "isEmpty", 
	"VERSION", "$", "noConflict", "emulateHTTP", "emulateJSON", "Events", 
	"on", "listenTo", "off", "stopListening", "once", "listenToOnce", 
	"trigger", "bind", "unbind", "Model", "Collection", "View", "sync", 
	"ajax", "Router", "History", "history", "LocalStorage", "localSync", 
	"ajaxSync", "getSyncMethod",
	#Underscore
	"_", "after", "all", "allKeys", "any", "assign", "before", "bind", 
	"bindAll", "chain", "clone", "collect", "compact", "compose", "constant", 
	"contains", "countBy", "create", "debounce", "defaults", "defer", 
	"delay", "detect", "difference", "drop", "each", "escape", "every", 
	"extend", "extendOwn", "filter", "find", "findIndex", "findKey", 
	"findLastIndex", "findWhere", "first", "flatten", "foldl", "foldr", 
	"forEach", "functions", "groupBy", "has", "head", "identity", "include", 
	"includes", "indexBy", "indexOf", "initial", "inject", "intersection", 
	"invert", "invoke", "isArguments", "isArray", "isBoolean", "isDate", 
	"isElement", "isEmpty", "isEqual", "isError", "isFinite", "isFunction", 
	"isMatch", "isNaN", "isNull", "isNumber", "isObject", "isRegExp", 
	"isString", "isUndefined", "iteratee", "keys", "last", "lastIndexOf", 
	"map", "mapObject", "matcher", "matches", "max", "memoize", "methods", 
	"min", "mixin", "negate", "noConflict", "noop", "now", "object", "omit", 
	"once", "pairs", "partial", "partition", "pick", "pluck", "property", 
	"propertyOf", "random", "range", "reduce", "reduceRight", "reject", 
	"rest", "result", "sample", "select", "shuffle", "size", "some", 
	"sortBy", "sortedIndex", "tail", "take", "tap", "template", "throttle", 
	"times", "toArray", "unescape", "union", "uniq", "unique", "uniqueId", 
	"unzip", "values", "where", "without", "wrap", "zip", "pop", "push", 
	"reverse", "shift", "sort", "splice", "unshift", "concat", "join", 
	"slice", "value", "toJSON", "valueOf", "toString", "VERSION", "iteratee", 
	"forEach", "each", "collect", "map", "inject", "foldl", "reduce", 
	"foldr", "reduceRight", "detect", "find", "select", "filter", "reject", 
	"all", "every", "any", "some", "include", "includes", "contains", 
	"invoke", "pluck", "where", "findWhere", "max", "min", "shuffle", 
	"sample", "sortBy", "groupBy", "indexBy", "countBy", "toArray", "size", 
	"partition", "take", "head", "first", "initial", "last", "drop", "tail", 
	"rest", "compact", "flatten", "without", "unique", "uniq", "union", 
	"intersection", "difference", "zip", "unzip", "object", "findIndex", 
	"findLastIndex", "sortedIndex", "indexOf", "lastIndexOf", "range", 
	"bind", "partial", "bindAll", "memoize", "delay", "defer", "throttle", 
	"debounce", "wrap", "negate", "compose", "after", "before", "once", 
	"keys", "allKeys", "values", "mapObject", "pairs", "invert", "methods", 
	"functions", "extend", "assign", "extendOwn", "findKey", "pick", "omit", 
	"defaults", "create", "clone", "tap", "isMatch", "isEqual", "isEmpty", 
	"isElement", "isArray", "isObject", "isArguments", "isFunction", 
	"isString", "isNumber", "isDate", "isRegExp", "isError", "isFinite", 
	"isNaN", "isBoolean", "isNull", "isUndefined", "has", "noConflict", 
	"identity", "constant", "noop", "property", "propertyOf", "matches", 
	"matcher", "times", "random", "now", "escape", "unescape", "result", 
	"uniqueId", "templateSettings", "template", "chain", "mixin",	
	#Animation events
	"animationend", "animationiteration", "animationstart", "beginEvent", 
	"endEvent", "repeatEvent",
	#Battery events
	"chargingchange chargingtimechange", "dischargingtimechange levelchange",
	#Call events
	"alerting", "busy", "callschanged cfstatechange", "connected", 
	"connecting", "dialing", "disconnected", "disconnecting", "error", 
	"held", "holding", "incoming", "resuming", "statechange", "voicechange",
	#CSS events
	"CssRuleViewRefreshed", "CssRuleViewChanged", 
	"CssRuleViewCSSLinkClicked", "transitionend",
	#Database events
	"abort", "blocked", "complete", "error", "success", "upgradeneeded", 
	"versionchange",
	#Document events
	"DOMLinkAdded", "DOMLinkRemoved", "DOMMetaAdded", "DOMMetaRemoved", 
	"DOMWillOpenModalDialog", "DOMModalDialogClosed", "unload",
	#DOM mutation events
	"DOMAttributeNameChanged", "DOMAttrModified", "DOMCharacterDataModified", 
	"DOMContentLoaded", "DOMElementNameChanged", "DOMNodeInserted", 
	"DOMNodeInsertedIntoDocument", "DOMNodeRemoved", 
	"DOMNodeRemovedFromDocument", "DOMSubtreeModified",
	#Drag events
	"drag", "dragdrop", "dragend", "dragenter", "dragexit", "draggesture", 
	"dragleave", "dragover", "dragstart", "drop",
	#Element events
	"invalid", "overflow", "underflow", "DOMAutoComplete", "command", 
	"commandupdate",
	#Focus events
	"blur", "change", "DOMFocusIn", "DOMFocusOut", "focus", "focusin", 
	"focusout",
	#Form events
	"reset", "submit",
	#Frame events
	"mozbrowserclose", "mozbrowsercontextmenu", "mozbrowsererror", 
	"mozbrowsericonchange", "mozbrowserlocationchange", "mozbrowserloadend", 
	"mozbrowserloadstart", "mozbrowseropenwindow", 
	"mozbrowsersecuritychange", "mozbrowsershowmodalprompt", 
	"mozbrowsertitlechange", "DOMFrameContentLoaded",
	#Input device events
	"click", "contextmenu", "DOMMouseScroll", "dblclick", "gamepadconnected", 
	"gamepaddisconnected", "keydown", "keypress", "keyup", 
	"MozGamepadButtonDown", "MozGamepadButtonUp", "mousedown", "mouseenter", 
	"mouseleave", "mousemove", "mouseout", "mouseover", "mouseup", 
	"mousewheel", "MozMousePixelScroll", "pointerlockchange", 
	"pointerlockerror,wheel",
	#Media events
	"audioprocess", "canplay", "canplaythrough", "durationchange", "emptied", 
	"ended", "ended", "loadeddata", "loadedmetadata", "MozAudioAvailable", 
	"pause", "play", "playing", "ratechange", "seeked", "seeking", "stalled", 
	"suspend", "timeupdate", "volumechange", "waiting", "complete",
	#Menu events
	"DOMMenuItemActive", "DOMMenuItemInactive",
	#Network events
	"datachange", "dataerror", "disabled", "enabled", "offline", "online", 
	"statuschange", "connectionInfoUpdate,",
	#Notification events
	"AlertActive", "AlertClose",
	#Popup events
	"popuphidden", "popuphiding", "popupshowing", "popupshown", 
	"DOMPopupBlocked",
	#Printing events
	"afterprint", "beforeprint",
	#Progress events
	"abort", "error", "load", "loadend", "loadstart", "progress", "progress", 
	"timeout", "uploadprogress",
	#Resource events
	"abort", "cached", "error", "load",
	#Script events
	"afterscriptexecute", "beforescriptexecute",
	#Sensor events
	"compassneedscalibration", "devicelight", "devicemotion", 
	"deviceorientation", "deviceproximity", "MozOrientation", 
	"orientationchange", "userproximity",
	#Session history events
	"pagehide", "pageshow", "popstate",
	#Smartcard events
	"icccardlockerror", "iccinfochange", "smartcard-insert", 
	"smartcard-remove", "stkcommand", "stksessionend", "cardstatechange",
	#SMS and USSD events
	"delivered", "received", "sent", "ussdreceived",
	#Storage events
	"change (see Non-standard events)", "storage",
	#SVG events
	"SVGAbort", "SVGError", "SVGLoad", "SVGResize", "SVGScroll", "SVGUnload", 
	"SVGZoom",
	#Tab events
	"tabviewsearchenabled", "tabviewsearchdisabled", 
	"tabviewframeinitialized", "tabviewshown", "tabviewhidden", "TabOpen", 
	"TabClose", "TabSelect", "TabShow", "TabHide", "TabPinned", 
	"TabUnpinned", "SSTabClosing", "SSTabRestoring", "SSTabRestored", 
	"visibilitychange",
	#Text events
	"compositionend", "compositionstart", "compositionupdate", "copy", 
	"cut", "paste", "select", "text",
	#Touch events
	"MozEdgeUIGesture", "MozMagnifyGesture", "MozMagnifyGestureStart", 
	"MozMagnifyGestureUpdate", "MozPressTapGesture", "MozRotateGesture", 
	"MozRotateGestureStart", "MozRotateGestureUpdate", "MozSwipeGesture", 
	"MozTapGesture", "MozTouchDown", "MozTouchMove", "MozTouchUp", 
	"touchcancel", "touchend", "touchenter", "touchleave", "touchmove", 
	"touchstart",
	#Update events
	"checking", "downloading", "error", "noupdate", "obsolete", "updateready",
	#Value change events
	"broadcast", "CheckboxStateChange", "hashchange", "input", 
	"RadioStateChange", "readystatechange", "ValueChange",
	#View events
	"fullscreen", "fullscreenchange", "fullscreenerror", 
	"MozEnteredDomFullscreen", "MozScrolledAreaChanged", "resize", 
	"scroll", "sizemodechange",
	#Websocket events
	"close", "error", "message", "open",
	#Window events
	"DOMWindowCreated", "DOMWindowClose", "DOMTitleChanged", 
	"MozBeforeResize", "SSWindowClosing", "SSWindowStateReady", 
	"SSWindowStateBusy", "close",
	#Uncategorized events
	"beforeunload", "localized", "message", "message", "message", 
	"MozAfterPaint", "moztimechange", "open", "show"
)
	
def etsi_kasiteltavat_tiedostot(
		hakemistosta, ohitettavat=['vendor'], kevytKasiteltavat=[], 
		rekursio=True, haettavat_tiedostotyypit=['js','css','html','phtml']): 
	palautus = []
	listaus = os.listdir(hakemistosta)
	for t in listaus:
		t_pointer = hakemistosta + '/' + t
		if t not in ohitettavat and t_pointer not in ohitettavat:
			if os.path.isdir(t_pointer) and rekursio:
				palautus.extend( etsi_kasiteltavat_tiedostot(t_pointer, 
					ohitettavat, kevytKasiteltavat, rekursio, 
					haettavat_tiedostotyypit))
			elif os.path.isfile(t_pointer):
				if (len(t.split(".")) > 1 and 
					t.split(".")[-1] in haettavat_tiedostotyypit):
					palautus.append(t_pointer)
	return palautus	
	
def tallennaTiedostoUuteenHakemistopuuhun(
			tiedostonimi, hakemisto="mungled", 
			juurikansio=os.path.abspath('.')):
	loppuosa = tiedostonimi.split(juurikansio)[-1]
	polku = juurikansio + "/mungled"
	for hakemisto in loppuosa.split("/"):
		if not os.path.exists(polku):
			os.mkdir(polku, 0775)
		polku = polku + "/" + hakemisto			
	return polku
	
# Tutkii komentoriviparametreja -- TODO: argparse.add_argument
def sisaltaaArgumentin(argumentti):
	haettavat = argumentti if isinstance(argumentti, list) else [argumentti]
	paikka = None
	for i in sys.argv:
		if i in haettavat:
			paikka = sys.argv.index(i)+1
	return paikka

# Tutkii komentoriviparametreja	TODO: argparse.add_argument
def seuraavaArgumentti(paikka):
	seuraavanPaikka = None
	if paikka:
		for i in sys.argv[paikka:]:
			if not seuraavanPaikka and i.startswith("-"): #i.find("-") == 0:
				seuraavanPaikka = sys.argv.index(i)
				break
	return seuraavanPaikka

def komentoriviParametrit(arvolle):
	if isinstance(arvolle, list):
		haettavat = arvolle
	else:
		haettavat = [arvolle]
	argumentinPaikka =  sisaltaaArgumentin(haettavat) 
	parametrit = sys.argv[argumentinPaikka:seuraavaArgumentti(
		argumentinPaikka)] if argumentinPaikka else []
	return parametrit

def eiKomentoriviparametreja():
	return len(sys.argv) == 1
	
def kayttoohjeet():
	print "USAGE:python javascriptMungler.py [filenames] [options [arguments]]\n\
	Mungler for js, php, (p)html and css -files. \n\
	\nOptions:\n\
	-R, --recursive\t\tScans for files recursively starting from current path. \n\
	-i, --skipped \t\tList of files to be skipped. \n\
		\"-i vendor\"\t\tSkips every file and subfolders that are located under a \"vendor\"-dir. \n\
	-r, --reverse \t\tRevert changes. Needs a mapfile which is generated as the default output. \n\
		\"-r -m mapfile.txt\"\tRolls back changes (not fully implemented yet). \n\
	-m, --map \t\tUse a mapfile from a previous run. \n\
		\"singlepage.html -m mapfileOfBigProject.txt\"\n\
	-s, --soft \t\tDo not search for new variables from given files. \n\
		\"jsclient.js -s serverpage.php\"Mungles php-file softly for ajax-interoperability.\n"
		
# SUORITUS:
#	-otetaan sotkettava tiedosto komentoriviltä argumenttina. 
#	-haetaan sen muuttujien määritellyt nimet. 
#	-luodaan niille hakemisto, joissa uudet nimet.
NIMIKEKARTTA = {}
def suoritus(): 
	global NIMIKEKARTTA
	pwd = os.path.abspath(".")
	aikaisempiMuunnoskartta = komentoriviParametrit(["--map", "-m"])
	
	NIMIKEKARTTA = lue_muunnoskartta(aikaisempiMuunnoskartta[-1]) if (
		aikaisempiMuunnoskartta and 
		os.path.isfile(aikaisempiMuunnoskartta[-1])) else {}
	
	ohitettavatTiedostot = komentoriviParametrit(["--skipped", 
		"-i", "--ignore"])
	ohitettavatTiedostot = map(lambda t: pwd +"/" + t if (
		t.find(pwd) < 0 and t.find("/") > -1) else t, ohitettavatTiedostot) 

	kevytKasiteltavat = komentoriviParametrit(["--soft", "-s"])  
	kevytKasiteltavat = map(lambda t: pwd +"/" + t if t.find(pwd) < 0 else 
		t, kevytKasiteltavat) 
	ohitettavatTiedostot.extend(kevytKasiteltavat)

	rekursiivisesti = sisaltaaArgumentin(["--recursive", "-R"])
	
	ohitettaviaSanoja = sisaltaaArgumentin(["--reserved"])


	tiedostotKomentorivilta = sys.argv[1:seuraavaArgumentti(1)]
	for i, t in enumerate(tiedostotKomentorivilta):
		if t is ".":
			tiedostotKomentorivilta[i] = pwd
	tiedostotKomentorivilta = map(lambda t: pwd +"/" + t if (
		t.find(pwd) < 0) else t, tiedostotKomentorivilta) 

	if not tiedostotKomentorivilta:
			quit(kayttoohjeet())

	tiedostot = []
	for t in tiedostotKomentorivilta:
		if os.path.isfile(t):
			tiedostot.push(t)
		if os.path.isdir(t):
			tiedostot.extend(etsi_kasiteltavat_tiedostot(
				t, ohitettavatTiedostot, kevytKasiteltavat, rekursiivisesti))

	for tiedostonimi in tiedostot:
		if os.path.isfile(tiedostonimi):
			tekstitiedosto = open(tiedostonimi, 'r')
			sisalto = tekstitiedosto.read()
			tekstitiedosto.close()
			if onTyyppia(tiedostonimi, "html"): 
				sisalto = etsi_ja_korvaa_muuttujat_htmlsta(sisalto)
			elif onTyyppia(tiedostonimi, "css"):
				sisalto = etsi_ja_korvaa_muuttujat_csssta(sisalto)
			elif onTyyppia(tiedostonimi, "php"): 
				sisalto = etsi_ja_korvaa_muuttujat_phpsta(sisalto)
			else: # ei sisällä htmlaa
				sisalto = poista_kommentit(sisalto)
				#sisalto =  poista_konsolirivit(sisalto);
				sisalto = etsi_muuttujat(sisalto)
				#sisalto = korvaa_loydetyt_muuttujat(sisalto)
		vientitiedosto = open(
			tallennaTiedostoUuteenHakemistopuuhun(tiedostonimi), 'w+')
		vientitiedosto.write(sisalto)
		vientitiedosto.close()
			
	for t in kevytKasiteltavat: 
		if os.path.isfile(t):
			tekstitiedosto = open(t, 'r')
			sisalto = tekstitiedosto.read()
			sisalto = etsi_muuttujat(sisalto, True)
			vientitiedosto = open(
				tallennaTiedostoUuteenHakemistopuuhun(t), 'w+')
			vientitiedosto.write(sisalto)

			vientitiedosto.close()			
		

if (eiKomentoriviparametreja()):
	quit(kayttoohjeet())
else:		
	suoritus()

#print etsi_kasiteltavat_tiedostot(tiedostot[0])
#os.listdir(os.path.abspath('.') + "/" + tiedostot[0])

for n, m in NIMIKEKARTTA.iteritems():
	print n +": "+m


