#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Correct untranslated and cross-language fragments in localized site copy."""

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

CATALAN = {
    "App nativa de catálogo de vinilos - Record Picker": "App nativa per catalogar vinils - Record Picker",
    "Record Picker para Mac": "Record Picker per a Mac",
    "La forma tranquila y nativa de catalogar tus vinilos y decidir qué poner esta noche.": "La manera tranquil·la i nativa de catalogar els teus vinils i decidir què escoltar aquesta nit.",
    "Explorar las funciones actuales": "Explorar les funcions actuals",
    "Record Picker lleva tu colección de discos al Mac con un catálogo rápido, un motor de recomendaciones por ambiente y enriquecimiento automático con reseñas críticas, todo en una app SwiftUI nativa y limpia.": "Record Picker porta la teva col·lecció de discos al Mac amb un catàleg ràpid, recomanacions segons l’ambient i enriquiment automàtic amb ressenyes, tot en una app SwiftUI nativa i neta.",
    "Catalogar, con belleza": "Un catàleg ben presentat",
    "Explora tu colección como un mosaico de portadas con zoom o como una lista ordenable. Edita cualquier campo en línea: título, artista, géneros, etiquetas, año, formato, sello, país, notas y portadas propias.": "Explora la col·lecció com un mosaic de portades ampliables o com una llista ordenable. Edita directament qualsevol camp: títol, artista, gèneres, etiquetes, any, format, segell, país, notes i portades pròpies.",
    "Encuentra todo al instante": "Troba-ho tot a l’instant",
    "La búsqueda de texto completo incluye navegador de resultados en vivo, coincidencias resaltadas y navegación paso a paso. Ocho secciones se abren con Comando-1 a Comando-8, con una barra de herramientas totalmente personalizable.": "La cerca de text complet inclou resultats en directe, coincidències ressaltades i navegació pas a pas. Les vuit seccions s’obren amb Ordre-1 fins a Ordre-8 i la barra d’eines és totalment personalitzable.",
    "Elige un disco por ambiente": "Tria un disc segons l’ambient",
    "Escribe un momento, como domingo lluvioso, noche electro o Britpop. Mood Pick pondera géneros, fechas, palabras clave de reseñas e historial reciente, usando Apple Intelligence en el dispositivo con respaldo local.": "Descriu un moment —un diumenge plujós, una nit electrònica o Britpop— i Mood Pick ponderarà gèneres, dates, paraules clau de ressenyes i l’historial recent. En dispositius compatibles utilitza Apple Intelligence al mateix dispositiu, amb una alternativa local.",
    "Selección aleatoria en Mac": "Selecció aleatòria al Mac",
    "Destacados": "Funcions destacades",
    "Mantén limpia tu biblioteca.": "Mantén la biblioteca endreçada.",
    "Calidad de datos detecta diez tipos de carencias, incluidas portadas, pistas, año, sellos, géneros, formato, país, código de barras y reseñas, con índice de palabras clave y correcciones individuales o masivas.": "Qualitat de les dades detecta deu tipus de mancances, com ara portades, pistes, any, segells, gèneres, format, país, codi de barres i ressenyes, amb índex de paraules clau i correccions individuals o en bloc.",
    "Escucha en cualquier lugar.": "Escolta des de qualsevol servei.",
    "Abre cualquier álbum en Apple Music, Spotify, Deezer, Tidal, Qobuz, YouTube Music, Amazon Music o SoundCloud desde la ficha del disco.": "Obre qualsevol àlbum a Apple Music, Spotify, Deezer, Tidal, Qobuz, YouTube Music, Amazon Music o SoundCloud des de la fitxa del disc.",
    "Estadísticas e información.": "Estadístiques i informació.",
    "Consulta artistas, sellos, años y formatos principales, con análisis narrativo opcional mediante Apple Intelligence.": "Consulta els artistes, segells, anys i formats principals, amb una anàlisi narrativa opcional mitjançant Apple Intelligence.",
    "Privado por diseño.": "Privada des del disseny.",
    "SwiftData y CloudKit sincronizan colección, portadas propias e historial entre tus dispositivos sin cuenta ni servidor de terceros.": "SwiftData i CloudKit sincronitzen la col·lecció, les portades pròpies i l’historial entre els teus dispositius, sense compte ni servidor de tercers.",
    "Importación y copia de seguridad.": "Importació i còpia de seguretat.",
    "Importa CSV, incluidos archivos compatibles con Discogs, y guarda o restaura en JSON. La app Mac está localizada en inglés, francés, italiano, español, portugués de Brasil, neerlandés, sueco, japonés y coreano.": "Importa fitxers CSV, inclosos els compatibles amb Discogs, i desa o restaura còpies en JSON. L’app per a Mac està localitzada en anglès, francès, italià, castellà, portuguès del Brasil, neerlandès, suec, japonès i coreà.",
    "Requisitos": "Requisits",
    "macOS 26.0 o posterior en Apple silicon e Intel.": "macOS 26.0 o posterior en Macs amb Apple silicon o Intel.",
    "El enriquecimiento con Apple Music requiere suscripción y autorización de Apple Music.": "L’enriquiment amb Apple Music requereix una subscripció i l’autorització d’Apple Music.",
    "El enriquecimiento de Last.fm usa una clave API personal gratuita.": "L’enriquiment amb Last.fm utilitza una clau API personal gratuïta.",
}

HINDI = {
    "crate में तेज़ navigation": "रिकॉर्ड संग्रह में तेज़ नेविगेशन",
    "crate से अलग wishlist": "संग्रह से अलग इच्छा-सूची",
    "चुनें, pick करें और फिर से खोजें": "चुनें, सुनें और फिर से खोजें",
    "तीन focused guides common collector questions का जवाब देती हैं: अभी क्या बजाएं, useful रैंडम पिकर कैसे use करें और collection को alive कैसे रखें।": "तीन संक्षिप्त मार्गदर्शिकाएँ आम सवालों का जवाब देती हैं: अभी क्या सुनें, उपयोगी यादृच्छिक चयन कैसे करें और संग्रह को जीवंत कैसे रखें।",
    "अगला कौन सा vinyl record चलाएं": "अगला कौन-सा विनाइल रिकॉर्ड चलाएँ",
    "शेल्फ़ को बहुत देर तक देखे बिना अगला vinyl record चुनने की व्यावहारिक guide.": "अलमारी के सामने देर तक उलझे बिना अगला विनाइल रिकॉर्ड चुनने की व्यावहारिक मार्गदर्शिका।",
    "Random vinyl record picker सबसे अच्छा तब काम क्यों करता है जब वह filters, favorites, exclusions और listening context का सम्मान करता है।": "यादृच्छिक विनाइल चयन तब बेहतर काम करता है जब वह फ़िल्टर, पसंदीदा, बहिष्करण और सुनने के संदर्भ का सम्मान करे।",
    "विनाइल संग्रह को manage और rediscover करें": "विनाइल संग्रह को सँभालें और फिर से खोजें",
    "Record Picker के साथ विनाइल संग्रह को catalog, enrich, backup और rediscover करने की व्यावहारिक guide.": "Record Picker के साथ विनाइल संग्रह को सूचीबद्ध, समृद्ध, सुरक्षित और फिर से खोजने की व्यावहारिक मार्गदर्शिका।",
    "MusicBrainz और Discogs से metadata": "MusicBrainz और Discogs से मेटाडेटा",
    "कोई third-party AI provider नहीं, कोई cloud AI नहीं; Apple Intelligence डिवाइस पर रहता है": "कोई तृतीय-पक्ष AI प्रदाता या क्लाउड AI नहीं; Apple Intelligence डिवाइस पर ही काम करता है",
    "इंटरनेट reviews कभी अपने-आप नहीं निकाले जाते": "इंटरनेट से समीक्षाएँ कभी अपने-आप प्राप्त नहीं की जातीं",
    "कवर धुंधली पृष्ठभूमि बनता है, पसंदीदा, अंतिम चयन रद्द और अगला चयन बटन के साथ, हर क्रिया के अपने haptic feedback सहित।": "कवर धुँधली पृष्ठभूमि बनाता है; पसंदीदा, पिछला चयन वापस लेने और अगला चयन करने के बटन हर क्रिया पर अलग हैप्टिक प्रतिक्रिया देते हैं।",
    "Record Picker विज्ञापन ट्रैकिंग का उपयोग नहीं करता और तृतीय-पक्ष विज्ञापन SDK शामिल नहीं करता.": "Record Picker विज्ञापन ट्रैकिंग का उपयोग नहीं करता और इसमें कोई तृतीय-पक्ष विज्ञापन SDK शामिल नहीं है।",
    "एक उपयोगी collection सिर्फ व्यवस्थित नहीं होता। वह जीवित रहता है।": "एक उपयोगी संग्रह केवल व्यवस्थित नहीं होता; वह जीवंत भी रहता है।",
    "Screenshots देखें": "स्क्रीनशॉट देखें",
    "विनाइल संग्रह को catalog करना केवल यह जानना नहीं है कि आपके पास क्या है। यह records को ढूंढना, चुनना, सुधारना, backup करना और फिर से खोज लेना है, वरना वे shelf पर खो सकते हैं।": "विनाइल संग्रह सूचीबद्ध करना केवल यह जानना नहीं है कि आपके पास क्या है। इसका अर्थ रिकॉर्ड ढूँढना, चुनना, सुधारना, सुरक्षित रखना और उन्हें अलमारी में खो जाने से पहले फिर खोज लेना भी है।",
    "Record Picker readable record bin, editable data, metadata lookups, artwork, statistics और smart picking को मिलाकर collection को active रखता है।": "Record Picker पठनीय रिकॉर्ड संग्रह, संपादन योग्य डेटा, मेटाडेटा खोज, कवर चित्र, आँकड़े और समझदार चयन को मिलाकर संग्रह को सक्रिय रखता है।",
    "Editable record sheets आपको dates, formats, genres, styles, labels, tracks और notes पूरा करने देते हैं।": "संपादन योग्य रिकॉर्ड विवरण में तारीखें, फ़ॉर्मैट, शैलियाँ, लेबल, ट्रैक और टिप्पणियाँ पूरी की जा सकती हैं।",
    "Control खोए बिना enrich करें": "नियंत्रण खोए बिना जानकारी समृद्ध करें",
    "MusicBrainz, Discogs और Cover Art Archive lookups केवल तब चलते हैं जब आप उन्हें शुरू करते हैं। Artwork को Photos, Files या web से manually भी चुना जा सकता है।": "MusicBrainz, Discogs और Cover Art Archive की खोज केवल आपके शुरू करने पर चलती है। कवर चित्र Photos, Files या वेब से स्वयं भी चुना जा सकता है।",
    "यह collection को local रखता है और समय के साथ data quality सुधारने के tools देता है।": "इससे संग्रह डिवाइस पर रहता है और समय के साथ डेटा की गुणवत्ता सुधारने के साधन मिलते हैं।",
    "Statistics और picking से rediscover करें": "आँकड़ों और चयन से फिर खोजें",
    "Statistics favorites, draws, exclusions और missing data दिखाते हैं। वे collection को पढ़ने का दूसरा तरीका देते हैं।": "आँकड़े पसंदीदा रिकॉर्ड, चयन, बहिष्करण और अधूरा डेटा दिखाते हैं। वे संग्रह को समझने का एक और तरीका देते हैं।",
    "Random picks, moods और history records को फिर circulation में लाते हैं, खासकर वे जिन्हें आप बिना ध्यान दिए भूल जाते हैं।": "यादृच्छिक चयन, मूड और इतिहास भूले हुए रिकॉर्ड को फिर सुनने की सूची में लाते हैं।",
    "Collection import या enter करें.": "संग्रह आयात करें या स्वयं दर्ज करें।",
    "Metadata और artwork पूरा करें.": "मेटाडेटा और कवर चित्र पूरा करें।",
    "नियमित रूप से backup और export करें.": "नियमित रूप से बैकअप और निर्यात करें।",
    "Albums को rediscover करने के लिए filters, statistics और draws का उपयोग करें।": "एल्बम फिर खोजने के लिए फ़िल्टर, आँकड़े और चयन का उपयोग करें।",
    "नियंत्रण बनाए रखते हुए अगला रिकॉर्ड चुनें, ऐसी randomness के साथ जो संग्रह को जीवित रखती है।": "नियंत्रण बनाए रखते हुए ऐसे यादृच्छिक चयन से अगला रिकॉर्ड चुनें जो संग्रह को जीवंत रखे।",
    "कम सुने गए रिकॉर्ड को प्राथमिकता देने वाला weighted draw": "कम सुने गए रिकॉर्ड को प्राथमिकता देने वाला वैकल्पिक भारित चयन",
    "साल, genre, format, speed और favorites के फ़िल्टर": "वर्ष, शैली, फ़ॉर्मैट, गति और पसंदीदा के फ़िल्टर",
    "छोटे सुधार: iPad cover picker बेहतर संतुलित, iPhone-Watch sync तेज़, और App Store review request अधिक discreet.": "छोटे सुधार: iPad पर बेहतर संतुलित कवर चयन, तेज़ iPhone–Watch समन्वयन और App Store समीक्षा का विनम्र अनुरोध।",
    "एकीकृत Liquid Glass buttons": "एकीकृत Liquid Glass बटन",
    "पढ़ने योग्य iPad rows और covers से details तक सीधी पहुँच": "पठनीय iPad पंक्तियाँ और कवर से विवरण तक सीधी पहुँच",
    "जहाँ सचमुच मदद हो वहाँ iPad drag and drop": "जहाँ उपयोगी हो वहाँ iPad पर खींचें और छोड़ें",
    "बिना झंझट iCloud sync": "सरल iCloud समन्वयन",
    "crate, wishlist, resolved duplicates, exclusions, history, restorable deletions और custom covers आपके उपकरणों के साथ चलते हैं।": "संग्रह, इच्छा-सूची, सुलझे डुप्लिकेट, बहिष्करण, इतिहास, वापस लाए जा सकने वाले विलोपन और अपने कवर आपके उपकरणों के बीच बने रहते हैं।",
    "स्प्रेडशीट के लिए CSV और साफ़ JSON, crate और wishlist अलग-अलग": "स्प्रेडशीट के लिए CSV और साफ़ JSON; संग्रह और इच्छा-सूची अलग-अलग",
    "माँग पर पूरा backup": "माँग पर पूरा बैकअप",
    "Record Picker 32 भाषाओं में उपलब्ध है, नए variants और localizations के साथ: अरबी, कैटलन, कोरियाई, डेनिश, ऑस्ट्रेलिया/कनाडा/UK अंग्रेज़ी, फ़िनिश, कनाडाई फ़्रेंच, हिब्रू, हिंदी, इंडोनेशियाई, नॉर्वेजियन, पोलिश, पुर्तगाली, रूसी, स्वीडिश और तुर्की।": "Record Picker 32 भाषाओं और क्षेत्रीय रूपों में उपलब्ध है, जिनमें अरबी, कैटलन, कोरियाई, डेनिश, ऑस्ट्रेलियाई, कनाडाई और ब्रिटिश अंग्रेज़ी, फ़िनिश, कनाडाई फ़्रेंच, हिब्रू, हिंदी, इंडोनेशियाई, नॉर्वेजियन, पोलिश, पुर्तगाली, रूसी, स्वीडिश और तुर्की शामिल हैं।",
    "कस्टमाइज़ किया जा सकने वाला Random Pick, नए Apple Watch app, साफ़ record bin, 32 भाषाओं और collectors के import/export tools के साथ संग्रह को फिर खोजें।": "अनुकूलन योग्य Random Pick, नया Apple Watch ऐप, साफ़ रिकॉर्ड संग्रह, 32 भाषाएँ और संग्रहकर्ताओं के आयात-निर्यात साधन।",
    "कैटलॉग, स्मार्ट चयन और Apple Watch companion": "कैटलॉग, समझदार चयन और Apple Watch सहायक ऐप",
    "अपने कलेक्शन को ज़ूम होने वाले कवर मोज़ेक या sortable सूची के रूप में देखें। कोई भी फ़ील्ड सीधे संपादित करें: शीर्षक, कलाकार, शैली, टैग, वर्ष, फ़ॉर्मैट, लेबल, देश, नोट्स और कस्टम कवर।": "अपने संग्रह को ज़ूम किए जा सकने वाले कवर मोज़ेक या क्रमबद्ध सूची में देखें। शीर्षक, कलाकार, शैली, टैग, वर्ष, फ़ॉर्मैट, लेबल, देश, टिप्पणियाँ और अपने कवर सीधे संपादित करें।",
    "फुल-टेक्स्ट खोज में लाइव परिणाम नेविगेटर, हाइलाइट किए गए मैच और चरण-दर-चरण ब्राउज़िंग शामिल हैं। आठ सेक्शन Command-1 से Command-8 तक जुड़े हैं।": "पूर्ण-पाठ खोज में लाइव परिणाम, उभरे हुए मिलान और चरण-दर-चरण नेविगेशन शामिल हैं। आठ अनुभाग Command-1 से Command-8 तक खुलते हैं।",
    "कोई पल लिखें, जैसे rainy Sunday afternoon, electro night या Britpop. Mood Pick आपकी शेल्फ से सही एल्बम सुझाता है और दोहराव से बचता है।": "किसी पल का वर्णन करें, जैसे बरसाती रविवार, इलेक्ट्रॉनिक संगीत की शाम या Britpop। Mood Pick आपकी अलमारी से उपयुक्त एल्बम सुझाता है और दोहराव से बचता है।",
    "Data Quality पैनल डुप्लिकेट, गायब कवर, वर्ष, फ़ॉर्मैट, शैली, रिव्यू और अधिक को पहचानता है, एक-क्लिक और bulk fixes के साथ।": "डेटा गुणवत्ता पैनल डुप्लिकेट, गायब कवर, वर्ष, फ़ॉर्मैट, शैली और समीक्षाओं जैसी कमियाँ पहचानता है तथा एकल या सामूहिक सुधार देता है।",
    "SwiftData और CloudKit आपका कलेक्शन, कस्टम कवर और इतिहास आपके डिवाइसों में बिना खाते और बिना third-party सर्वर के सिंक रखते हैं।": "SwiftData और CloudKit बिना खाते या तृतीय-पक्ष सर्वर के आपके संग्रह, अपने कवर और इतिहास को उपकरणों के बीच समन्वित रखते हैं।",
    "CSV से इम्पोर्ट करें, Discogs-compatible फ़ाइलों सहित, फिर JSON के रूप में बैकअप और रिस्टोर करें। Record Picker 25+ भाषाओं में उपलब्ध है।": "Discogs-संगत फ़ाइलों सहित CSV आयात करें, फिर JSON में बैकअप लें या पुनर्स्थापित करें। Record Picker 32 भाषाओं और क्षेत्रीय रूपों में उपलब्ध है।",
    "Last.fm संवर्धन मुफ्त व्यक्तिगत API key का उपयोग करता है।": "Last.fm संवर्धन एक निःशुल्क व्यक्तिगत API कुंजी का उपयोग करता है।",
    "जब shelf पर सब कुछ tempting हो, तो best choice अक्सर वही होती है जिसे आप फिर से surface होने देते हैं।": "जब अलमारी का हर रिकॉर्ड लुभावना लगे, तो अच्छा चुनाव अक्सर वही होता है जिसे आप फिर सामने आने दें।",
    "Collection बढ़ने पर record चुनना अजीब तरह से कठिन हो सकता है। आप classic के बारे में सोचते हैं, फिर ऐसे album के बारे में जिसे कम बजाते हैं, फिर new addition के बारे में, और listening session दस मिनट की हिचकिचाहट से शुरू होता है।": "संग्रह बढ़ने पर रिकॉर्ड चुनना कठिन हो सकता है। कभी किसी पुराने पसंदीदा, कभी कम सुने एल्बम और कभी नई ख़रीद का विचार आता है, और सुनने का समय हिचकिचाहट में बीतने लगता है।",
    "Moment के mood से शुरू करें": "उस पल के मूड से शुरू करें",
    "किसी specific title को खोजने से पहले अक्सर यह तय करना बेहतर होता है कि आप कैसी listening चाहते हैं: focused, quiet, energetic, nostalgic या बस unexpected.": "किसी खास एल्बम को खोजने से पहले तय करें कि आप कैसा संगीत सुनना चाहते हैं: एकाग्र, शांत, ऊर्जावान, पुरानी यादों वाला या बस अप्रत्याशित।",
    "Record Picker mood से draw को steer कर सकता है, फिर genres, styles, tags और favorites से moment के लिए बेहतर record सुझा सकता है।": "Record Picker मूड के अनुसार चयन को दिशा देता है और शैली, टैग तथा पसंदीदा के आधार पर उस पल के लिए बेहतर रिकॉर्ड सुझाता है।",
    "सब कुछ तय किए बिना bin को narrow करें": "सब कुछ तय किए बिना विकल्प घटाएँ",
    "Filters तब सबसे उपयोगी होते हैं जब वे choice को frame करते हैं, आपके लिए फैसला नहीं करते। एक period, कुछ genres, available records या favorites अक्सर काफी होते हैं।": "फ़िल्टर तब उपयोगी होते हैं जब वे आपके बदले फैसला किए बिना विकल्प सीमित करें। कोई अवधि, कुछ शैलियाँ, उपलब्ध रिकॉर्ड या पसंदीदा अक्सर पर्याप्त होते हैं।",
    "Random selection फिर उपयोगी हो जाती है क्योंकि यह हमेशा वही records पहले चुनने की आदत के विरुद्ध काम करती है।": "यादृच्छिक चयन हमेशा उन्हीं रिकॉर्ड को पहले चुनने की आदत तोड़ता है।",
    "अच्छी randomness को no कहने का तरीका भी चाहिए। Same artist को exclude करना, किसी record को temporarily skip करना या favorites को favor करना control हटाए बिना variety बनाए रखता है।": "अच्छे यादृच्छिक चयन में मना करने का विकल्प भी होना चाहिए। एक ही कलाकार को रोकना, किसी रिकॉर्ड को अस्थायी रूप से छोड़ना या पसंदीदा को प्राथमिकता देना नियंत्रण बनाए रखते हुए विविधता देता है।",
    "Listening history दिखाती है कि क्या बार-बार लौटता है और क्या फिर से खोजे जाने लायक है।": "सुनने का इतिहास दिखाता है कि कौन-से रिकॉर्ड बार-बार लौटते हैं और किन्हें फिर खोजा जाना चाहिए।",
    "एक mood या simple constraint चुनें.": "कोई मूड या सरल सीमा चुनें।",
    "Year, genre, availability या favorites से filter करें.": "वर्ष, शैली, उपलब्धता या पसंदीदा से फ़िल्टर करें।",
    "Draw चलाएं और surprise को स्वीकार करें, अगर वह अभी भी सही लगे।": "चयन चलाएँ और परिणाम उस पल सही लगे तो उसे स्वीकार करें।",
    "Played records का track रखें ताकि collection चलता रहे.": "सुने गए रिकॉर्ड का हिसाब रखें ताकि संग्रह घूमता रहे।",
    "Random choice तब उपयोगी होती है जब वह आपकी collection को थोड़ा समझती है।": "यादृच्छिक चयन तब उपयोगी होता है जब वह आपके संग्रह को थोड़ा समझता हो।",
    "पूरी तरह random draw मजेदार हो सकता है, लेकिन अगर app unavailable record, कल वाला ही artist या moment से मेल न खाने वाला album सुझाए तो यह जल्दी परेशान कर सकता है।": "पूरी तरह यादृच्छिक चयन मज़ेदार हो सकता है, लेकिन अनुपलब्ध रिकॉर्ड, कल सुना वही कलाकार या उस पल से मेल न खाने वाला एल्बम जल्दी परेशान कर सकता है।",
    "एक अच्छा पिकर संयोग को सरल नियमों के साथ मिलाता है। Record Picker आश्चर्य का आनंद बनाए रखता है और exclusions, favorites, filters तथा collection की वास्तविक स्थिति का सम्मान करता है।": "अच्छा चयन संयोग को सरल नियमों से जोड़ता है। Record Picker आश्चर्य बनाए रखते हुए बहिष्करण, पसंदीदा, फ़िल्टर और संग्रह की वास्तविक उपलब्धता का सम्मान करता है।",
    "Draw years, genres, styles, favorites, availability और temporary exclusions को ध्यान में रख सकता है। आप सीधे record नहीं चुनते, बल्कि playing field चुनते हैं।": "चयन वर्ष, शैली, पसंदीदा, उपलब्धता और अस्थायी बहिष्करण को ध्यान में रख सकता है। आप सीधे रिकॉर्ड नहीं, बल्कि चयन की सीमा तय करते हैं।",
    "यह बड़े collections के लिए खास तौर पर उपयोगी है: chance भूले हुए albums को वापस लाता है बिना listening context से पूरी तरह बाहर निकले।": "यह बड़े संग्रहों में खास उपयोगी है: संयोग भूले हुए एल्बम वापस लाता है, पर सुनने के संदर्भ से बाहर नहीं जाता।",
    "Favorites, exclusions और artist variety": "पसंदीदा, बहिष्करण और कलाकारों की विविधता",
    "Record Picker favorites को favor कर सकता है, draw को favorites तक सीमित कर सकता है या same artist repeat होने से बचा सकता है। Temporary exclusions भी record या criterion को collection स्थायी रूप से बदले बिना अलग रखने देते हैं।": "Record Picker पसंदीदा को प्राथमिकता दे सकता है, चयन केवल पसंदीदा तक सीमित कर सकता है या एक ही कलाकार की पुनरावृत्ति रोक सकता है। अस्थायी बहिष्करण संग्रह बदले बिना किसी रिकॉर्ड या शर्त को अलग रखते हैं।",
    "Result सिर्फ random नहीं है। यह आपके असल listening तरीके के ज्यादा करीब है।": "परिणाम केवल यादृच्छिक नहीं रहता; वह आपके सुनने के वास्तविक तरीके के अधिक निकट होता है।",
    "Draw iPhone और iPad पर उपलब्ध है, record bin और filters देखने के लिए wider views के साथ। Apple Watch companion जरूरी चीजें wrist पर रखता है।": "चयन iPhone और iPad पर उपलब्ध है, जहाँ संग्रह और फ़िल्टर के लिए विस्तृत दृश्य मिलते हैं। Apple Watch सहायक ऐप ज़रूरी नियंत्रण कलाई पर रखता है।",
    "Goal सरल है: listening को database work बनाए बिना next record जल्दी चुनना।": "लक्ष्य सरल है: सुनने को डेटाबेस का काम बनाए बिना अगला रिकॉर्ड जल्दी चुनना।",
    "Available collection से animated draw.": "उपलब्ध संग्रह से एनिमेटेड चयन।",
    "Year, genre, style और favorites के filters.": "वर्ष, शैली और पसंदीदा के फ़िल्टर।",
    "Records या artists की temporary exclusion.": "रिकॉर्ड या कलाकारों का अस्थायी बहिष्करण।",
    "अदृश्य habits से बचने के लिए draw history.": "अनजानी आदतों से बचने के लिए चयन इतिहास।",
}

SMALL_FIXES = {
    "ar": {
        "Record Picker مترجم إلى أكثر من 25 لغة.": "يتوفر Record Picker بـ32 لغة ونسخة إقليمية.",
    },
    "ca": {
        "La app Mac está localizada en inglés, francés, italiano, español, portugués de Brasil, neerlandés, sueco, japonés y coreano.": "Record Picker està disponible en 32 llengües i variants regionals.",
        "L’app per a Mac està localitzada en anglès, francès, italià, castellà, portuguès del Brasil, neerlandès, suec, japonès i coreà.": "Record Picker està disponible en 32 llengües i variants regionals.",
    },
    "da": {
        "Record Picker er lokaliseret på mere end 25 sprog.": "Record Picker findes på 32 sprog og i regionale varianter.",
        "Siden nedenfor præsenterer hovedfunktionerne i version 1.8 og Mac 1.8-appen, fra gratis + Pro-samlinger til iCloud-synkronisering, duplikatstyring, anmeldelser og privatliv.": "Afsnittene nedenfor gennemgår Record Pickers aktuelle funktioner til katalogisering, valg, synkronisering, sikkerhedskopiering, datakvalitet og privatliv. Versionshistorikken er bevaret som reference.",
    },
    "de": {
        "Funktionswunsche": "Funktionswünsche",
        "Auf der folgenden Seite werden die Hauptfunktionen der Version 1.8 und der Mac 1.8-App vorgestellt, von Free + Pro-Sammlungen bis hin zu iCloud-Synchronisierung, Duplikatverwaltung, Überprüfungen und Datenschutz.": "Die folgenden Abschnitte beschreiben die aktuellen Funktionen von Record Picker für Katalogisierung, Auswahl, Synchronisierung, Sicherung, Datenqualität und Datenschutz. Der Versionsverlauf bleibt als Referenz erhalten.",
    },
    "el": {
        "Χωρίς τρίτους παρόχους AI και χωρίς cloud AI· το Apple Intelligence μένει στη συσκευή": "Χωρίς παρόχους τεχνητής νοημοσύνης τρίτων και χωρίς τεχνητή νοημοσύνη στο cloud· το Apple Intelligence παραμένει στη συσκευή",
        "Το Record Picker είναι τοπικοποιημένο σε πάνω από 25 γλώσσες.": "Το Record Picker διατίθεται σε 32 γλώσσες και τοπικές παραλλαγές.",
    },
    "en-au": {
        "The page below presents the main features in version 1.8 and the Mac 1.8 app, from Free + Pro collections to iCloud sync, duplicate management, reviews and privacy.": "The sections below cover Record Picker’s current cataloguing, choosing, sync, backup, data-quality and privacy features. The version history remains available for reference.",
    },
    "en-ca": {
        "The page below presents the main features in version 1.8 and the Mac 1.8 app, from Free + Pro collections to iCloud sync, duplicate management, reviews and privacy.": "The sections below cover Record Picker’s current cataloguing, choosing, sync, backup, data-quality and privacy features. The version history remains available for reference.",
    },
    "en-gb": {
        "The page below presents the main features in version 1.8 and the Mac 1.8 app, from Free + Pro collections to iCloud sync, duplicate management, reviews and privacy.": "The sections below cover Record Picker’s current cataloguing, choosing, sync, backup, data-quality and privacy features. The version history remains available for reference.",
    },
    "en-us": {
        "The page below presents the main features in version 1.8 and the Mac 1.8 app, from Free + Pro collections to iCloud sync, duplicate management, reviews and privacy.": "The sections below cover Record Picker’s current cataloging, choosing, sync, backup, data-quality and privacy features. The version history remains available for reference.",
    },
    "fi": {
        "Record Picker on lokalisoitu yli 25 kielelle.": "Record Picker on saatavilla 32 kieli- ja alueversiossa.",
        "Alla oleva sivu esittelee version 1.8 ja Mac 1.8 -sovelluksen tärkeimmät ominaisuudet Free + Pro -kokoelmista iCloud-synkronointiin, kopioiden hallintaan, arvosteluihin ja yksityisyyteen.": "Alla olevissa osioissa esitellään Record Pickerin nykyiset luettelointi-, valinta-, synkronointi-, varmuuskopiointi-, tietojen laatu- ja tietosuojaominaisuudet. Versiohistoria säilyy viitteenä.",
    },
    "fr": {
        "Relève le 3 Picks Challenge du 9 au 22 août 2026 et mets ta propre collection de disques en jeu.": "Participez au défi 3 Picks du 9 au 22 août 2026 et mettez votre propre collection de disques en jeu.",
        "Partage ton favori sur Instagram avec": "Partagez votre favori sur Instagram avec",
        "Une raison liée à l’actualité de redécouvrir un disque que tu possèdes déjà.": "Une suggestion liée à l’actualité pour redécouvrir un disque que vous possédez déjà.",
        "Record Picker 1.9 présente le Disque du jour : une raison actuelle et confidentielle de redécouvrir un disque que tu possèdes déjà.": "Record Picker 1.9 introduit le Disque du jour : une suggestion liée à l’actualité, privée, pour redécouvrir un disque que vous possédez déjà.",
        "L’actualité musicale vérifiée, les anniversaires marquants et, en option, les concerts proches sont rapprochés de ta collection uniquement sur ton appareil.": "Les actualités musicales vérifiées, les dates anniversaires marquantes et, si vous l’activez, les concerts à proximité sont mis en relation avec votre collection, uniquement sur votre appareil.",
        "Des rappels privés facultatifs, le retour de pertinence et le Disque du jour sur Apple Watch entretiennent la qualité des suggestions. Ta collection n’est jamais transmise au service d’actualité.": "Des rappels privés facultatifs, vos retours sur la pertinence et le Disque du jour sur Apple Watch améliorent les suggestions. Votre collection n’est jamais transmise au service d’actualité.",
        "Distingue les corrections fiables que l’app peut effectuer des choix qui exigent ta décision, avec la source et le niveau de confiance de chaque proposition.": "Distingue les corrections fiables que l’app peut effectuer des choix qui exigent votre décision, avec la source et le niveau de confiance de chaque proposition.",
    },
    "fr-ca": {
        "Relève le 3 Picks Challenge du 9 au 22 août 2026 et mets ta propre collection de disques en jeu.": "Participez au défi 3 Picks du 9 au 22 août 2026 et mettez votre propre collection de disques en jeu.",
        "Partage ton favori sur Instagram avec": "Partagez votre favori sur Instagram avec",
        "Une raison liée à l’actualité de redécouvrir un disque que tu possèdes déjà.": "Une suggestion liée à l’actualité pour redécouvrir un disque que vous possédez déjà.",
        "Record Picker 1.9 présente le Disque du jour : une raison actuelle et confidentielle de redécouvrir un disque que tu possèdes déjà.": "Record Picker 1.9 introduit le Disque du jour : une suggestion liée à l’actualité, privée, pour redécouvrir un disque que vous possédez déjà.",
        "Les nouvelles musicales vérifiées, les anniversaires marquants et, en option, les concerts à proximité sont rapprochés de ta collection uniquement sur ton appareil.": "Les actualités musicales vérifiées, les dates anniversaires marquantes et, si vous l’activez, les concerts à proximité sont mis en relation avec votre collection, uniquement sur votre appareil.",
        "Des rappels privés facultatifs, le retour de pertinence et le Disque du jour sur Apple Watch entretiennent la qualité des suggestions. Ta collection n’est jamais transmise au service d’actualité.": "Des rappels privés facultatifs, vos retours sur la pertinence et le Disque du jour sur Apple Watch améliorent les suggestions. Votre collection n’est jamais transmise au service d’actualité.",
        "Sépare les corrections fiables des décisions qui demandent ton attention.": "Sépare les corrections fiables des décisions qui demandent votre intervention.",
    },
    "he": {
        "Record Picker מקומית ביותר מ-25 שפות.": "Record Picker זמין ב-32 שפות ובגרסאות אזוריות.",
    },
    "id": {
        "Record Picker dilokalkan dalam 25+ bahasa.": "Record Picker tersedia dalam 32 bahasa dan varian regional.",
        "Navigasi cepat melalui crate": "Navigasi cepat dalam koleksi",
        "Wishlist terpisah dari crate": "Daftar keinginan terpisah dari koleksi",
        "Crate, wishlist, duplikat terselesaikan, pengecualian, riwayat, penghapusan yang bisa dipulihkan, dan sampul khusus mengikuti perangkat Anda.": "Koleksi, daftar keinginan, duplikat yang diselesaikan, pengecualian, riwayat, penghapusan yang dapat dipulihkan, dan sampul khusus tetap tersedia di perangkat Anda.",
        "CSV untuk spreadsheet dan JSON bersih, terpisah untuk crate dan wishlist": "CSV untuk lembar bentang dan JSON bersih, terpisah untuk koleksi dan daftar keinginan",
        "crate jelas": "koleksi yang jelas",
    },
    "it": {
        "fallback Discogs": "Discogs come alternativa",
        "Navigazione rapida nel crate": "Navigazione rapida nell’archivio",
        "Wishlist separata dal crate": "Lista dei desideri separata dall’archivio",
        "duplicati, esclusioni, wishlist e cronologia": "duplicati, esclusioni, lista dei desideri e cronologia",
        "Swipe per eliminare in wishlist e cronologia AI Mood": "Scorri per eliminare nella lista dei desideri e nella cronologia di Mood Pick",
        "Crate, wishlist, duplicati risolti, esclusioni, cronologia, eliminazioni ripristinabili e copertine personalizzate seguono i tuoi dispositivi.": "Archivio, lista dei desideri, duplicati risolti, esclusioni, cronologia, eliminazioni ripristinabili e copertine personalizzate restano disponibili sui tuoi dispositivi.",
        "CSV per fogli di calcolo e JSON pulito, separati per crate e wishlist": "CSV per fogli di calcolo e JSON pulito, separati per archivio e lista dei desideri",
        "sync iPhone-Watch": "sincronizzazione iPhone–Watch",
        "Drag and drop su iPad dove serve davvero": "Trascina e rilascia su iPad dove serve davvero",
        "privacy policy": "informativa sulla privacy",
    },
    "nb": {
        "CSV til regneark og ren JSON, adskilt for kasse og ønskeliste": "CSV for regneark og ren JSON, separat for kasse og ønskeliste",
        "Record Picker er lokalisert på mer enn 25 språk.": "Record Picker er tilgjengelig på 32 språk og i regionale varianter.",
    },
    "pl": {
        "Record Picker jest zlokalizowany w ponad 25 językach.": "Record Picker jest dostępny w 32 językach i wariantach regionalnych.",
    },
    "pt-br": {
        "fallback Discogs": "Discogs como alternativa",
        "exclusões, wishlist e histórico": "exclusões, lista de desejos e histórico",
        "Deslizar para apagar na wishlist e no histórico AI Mood": "Deslize para apagar na lista de desejos e no histórico do Mood Pick",
        "Swipe para apagar na wishlist e no histórico AI Mood": "Deslize para apagar na lista de desejos e no histórico do Mood Pick",
        "sync iPhone-Watch": "sincronização iPhone–Watch",
        "tile do iPad": "cartão do iPad",
        "politica de privacidade": "política de privacidade",
    },
    "pt-pt": {
        "O Record Picker está localizado em mais de 25 idiomas.": "O Record Picker está disponível em 32 idiomas e variantes regionais.",
    },
    "ru": {
        "Record Picker локализован на 25+ языков.": "Record Picker доступен на 32 языках и в региональных вариантах.",
    },
    "sv": {
        "dedikerat Sync Center": "särskilt synkroniseringscenter",
        "Sidan nedan presenterar huvudfunktionerna i version 1.8 och Mac 1.8-appen, från Free + Pro-samlingar till iCloud-synkronisering, dubbletthantering, recensioner och sekretess.": "Avsnitten nedan beskriver Record Pickers aktuella funktioner för katalogisering, val, synkronisering, säkerhetskopiering, datakvalitet och integritet. Versionshistoriken finns kvar som referens.",
    },
    "tr": {
        "Record Picker 25+ dilde yerelleştirilmiştir.": "Record Picker 32 dilde ve bölgesel varyantta kullanılabilir.",
    },
    "zh-hans": {
        "Record Picker 已本地化为 25+ 种语言。": "Record Picker 提供 32 种语言及地区变体。",
    },
    "zh-hant": {
        "Record Picker 已在 25+ 種語言中在地化。": "Record Picker 提供 32 種語言及地區版本。",
    },
}


def replace_tree(locale: str, replacements: dict[str, str]) -> None:
    for path in (ROOT / locale).rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


class MainText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_main = False
        self.skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "main":
            self.in_main = True
        elif tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "main":
            self.in_main = False
        elif tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if self.in_main and not self.skip:
            self.parts.append(data)


def main_text(locale: str) -> str:
    parser = MainText()
    for path in (ROOT / locale).rglob("*.html"):
        parser.feed(path.read_text(encoding="utf-8"))
    return unescape(" ".join(parser.parts))


def audit() -> None:
    catalan = main_text("ca")
    for stale in CATALAN:
        assert stale not in catalan, ("ca", stale)
    hindi = main_text("hi")
    for stale in HINDI:
        assert stale not in hindi, ("hi", stale)
    for locale, replacements in SMALL_FIXES.items():
        text = main_text(locale)
        for stale in replacements:
            assert stale not in text, (locale, stale)
    print("OK: audited localized copy contains no known cross-language, stale-version or language-count fragments.")


def main() -> None:
    replace_tree("ca", CATALAN)
    replace_tree("hi", HINDI)
    for locale, replacements in SMALL_FIXES.items():
        replace_tree(locale, replacements)
    audit()


if __name__ == "__main__":
    main()
