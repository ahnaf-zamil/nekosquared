#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Lorem ipsum text.
"""

# Provides us with a large enough quantity of text to generate reasonably large
# pagination examples.

lorem_ipsum = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec in condimentum 
elit. Donec aliquet tellus at nibh lobortis pulvinar. Morbi rhoncus dui sit 
amet auctor ornare. Donec ut fringilla magna. In in tellus vel metus 
convallis tincidunt eget eget leo. Praesent ante ante, maximus eu blandit in, 
malesuada quis lorem. Morbi at justo sed lectus lobortis porttitor. Fusce 
venenatis ipsum ipsum, eu consectetur magna lacinia vitae. Integer suscipit 
volutpat turpis sit amet semper. Duis eu mauris consequat, rutrum nulla eget, 
facilisis mauris. Nam commodo dui eu fermentum feugiat. Etiam molestie odio 
id quam tempus, quis gravida orci imperdiet. Integer porta, tortor non 
aliquam scelerisque, justo ex euismod lorem, sit amet lacinia urna nunc at 
lectus. Duis faucibus erat non fringilla mattis. Donec malesuada posuere purus.

Duis commodo ante dui, ac placerat lacus maximus eu. Morbi urna nisl, 
faucibus vitae aliquet id, scelerisque vel tortor. Curabitur a quam eget enim 
feugiat laoreet. Pellentesque viverra urna eu eros maximus tincidunt. In 
convallis diam tortor, sed vulputate urna imperdiet ac. Phasellus ac metus 
est. Sed ac condimentum urna, vitae consectetur orci. Quisque ut sem lectus. 
Orci varius natoque penatibus et magnis dis parturient montes, nascetur 
ridiculus mus. Sed eu dictum est, ut finibus nisl. Donec tempus lectus non 
quam ullamcorper, sit amet egestas massa condimentum.

Sed quis ante condimentum, consectetur justo nec, consequat sapien. Phasellus 
euismod erat id molestie tempor. Maecenas ante justo, porttitor id tempor a, 
lacinia sed enim. Nunc at sodales mi. Donec laoreet, magna eget euismod 
maximus, metus felis blandit urna, eget condimentum nisi tellus id metus. 
Donec at enim sit amet justo mattis porta et quis risus. Pellentesque 
bibendum sagittis nibh, quis laoreet nisi. Cras vel aliquam dolor. In hac 
habitasse platea dictumst.

Aenean at mollis elit, et cursus ex. Duis et erat a eros consequat ornare. 
Sed tincidunt aliquam diam, id molestie nulla porta eu. Lorem ipsum dolor sit 
amet, consectetur adipiscing elit. Vivamus et feugiat ante. Sed et ante 
vestibulum, pretium nisi sit amet, aliquam mi. Vivamus sed tortor luctus 
felis efficitur feugiat. Cras gravida pulvinar erat, vel sollicitudin magna 
dapibus eget. Curabitur id tempor nisi. Vestibulum ante ipsum primis in 
faucibus orci luctus et ultrices posuere cubilia Curae; Nam ac augue ac 
mauris vulputate mattis pretium eu quam. Aliquam non enim vitae eros sodales 
maximus. Fusce eget ex iaculis augue tincidunt porttitor sit amet vitae 
metus. Suspendisse potenti. Suspendisse vitae facilisis velit, dignissim 
mattis est. Duis mollis, tellus eget suscipit faucibus, nulla felis aliquet 
velit, sit amet pellentesque nunc dui vitae justo.

Quisque odio ipsum, aliquam et nibh et, vulputate sollicitudin turpis. Ut 
turpis nulla, auctor sed sagittis non, sodales eu tellus. Nullam ut justo non 
velit pulvinar dictum in at lectus. Nullam vulputate ante fermentum, blandit 
purus in, lacinia magna. Vivamus vitae mi eget eros dapibus vulputate a et 
dolor. Morbi sit amet neque a ante pellentesque porttitor vitae non risus. 
Nulla facilisi. Vivamus consectetur dui quis sapien rhoncus, sed viverra elit 
rutrum. Cras congue dolor sapien, in interdum massa ultrices at. Phasellus 
elit diam, vestibulum vel suscipit id, scelerisque quis ex. Proin blandit 
mauris non nunc iaculis laoreet. Maecenas sit amet magna ultrices, semper 
tortor eu, vestibulum nibh.

Etiam ut ante luctus enim ultricies dignissim. Praesent ac metus diam. Cras 
et bibendum ligula. Suspendisse ullamcorper erat dolor, dictum efficitur 
tortor hendrerit ut. Cras ac efficitur nunc. Ut hendrerit ultrices arcu ut 
condimentum. Proin vehicula, lorem sit amet pulvinar placerat, elit tortor 
iaculis sapien, vitae dapibus velit odio id lorem. Ut molestie ligula quam, 
in commodo nisl ultrices nec. Donec tellus ex, efficitur sit amet elit 
dictum, pellentesque placerat magna. Ut eget lorem quam. In id tristique 
velit. Vestibulum in dui elit.

Sed maximus a nisi ac ultricies. Phasellus lacinia ultrices arcu eu 
tristique. Phasellus a porttitor purus. Curabitur sapien purus, molestie non 
enim eget, condimentum rutrum justo. Nulla facilisi. Orci varius natoque 
penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vivamus 
malesuada, erat et ultricies ultricies, elit nisi venenatis turpis, 
in eleifend orci nisl at velit. Integer accumsan elit arcu, vehicula 
elementum tortor tempus ut. Vestibulum ante ipsum primis in faucibus orci 
luctus et ultrices posuere cubilia Curae; Pellentesque dui ipsum, cursus at 
orci eget, cursus volutpat est. Maecenas vel leo vitae augue sollicitudin 
lacinia. Proin at ante arcu. Sed vel felis ut felis tincidunt auctor. Vivamus 
hendrerit vulputate mauris sed sodales.

Nullam aliquet hendrerit justo, eu iaculis elit fermentum quis. Maecenas 
accumsan molestie vulputate. Donec egestas eleifend quam, eu ultrices lorem. 
Aliquam semper id lectus eu ullamcorper. Duis a malesuada neque. Nulla 
volutpat mi lacus, eget efficitur sem ultricies in. Donec sed rhoncus turpis. 
Etiam quis vehicula diam. In lacinia sit amet urna auctor rutrum. Vivamus 
gravida elementum vehicula. Sed sed justo ullamcorper, porttitor sem feugiat, 
gravida lorem.

Ut aliquam elementum eleifend. Donec lorem lorem, euismod vitae ornare id, 
mollis eu dolor. Aliquam semper tellus sit amet accumsan vestibulum. Donec mi 
enim, consequat sed euismod sed, bibendum id massa. Aenean interdum 
vestibulum metus, non congue odio volutpat vitae. Quisque cursus viverra 
tortor, ac tincidunt nunc lacinia vel. Aenean vestibulum ligula et lobortis 
tincidunt. Maecenas pellentesque commodo tellus a hendrerit. Vivamus quis 
pretium lacus.

Aenean interdum porta dapibus. Nam facilisis vehicula felis, at pretium leo 
feugiat et. Donec gravida dui ex, at finibus nulla auctor id. Sed sit amet 
nibh justo. Fusce nisl purus, fermentum a elit ut, dignissim imperdiet magna. 
Nulla massa mi, iaculis sed risus eu, fermentum gravida ante. Vivamus quis 
maximus felis. Nulla nec velit faucibus lorem vestibulum elementum non sed 
felis. Donec accumsan ligula et sapien iaculis semper. Donec porttitor ligula 
eu commodo porttitor. Vestibulum ante ipsum primis in faucibus orci luctus et 
ultrices posuere cubilia Curae; Curabitur elementum urna a velit viverra, 
eget placerat eros dapibus.

Phasellus pharetra leo quis facilisis ornare. In maximus elit et odio 
hendrerit, in interdum metus scelerisque. Morbi non mollis ex, eu auctor 
elit. Ut dictum tortor quis quam scelerisque, quis sagittis nisi accumsan. 
Nunc malesuada est mi, eget semper sem faucibus sed. Morbi porta id arcu 
vitae maximus. Cras faucibus, orci id sagittis commodo, metus risus dignissim 
ligula, vel consectetur sem purus id leo. Nulla luctus pellentesque congue.

Aenean lacinia rhoncus erat a volutpat. Vestibulum vestibulum eu dui quis 
convallis. Nullam scelerisque a dui nec malesuada. Morbi nec luctus eros, 
nec feugiat diam. Nunc sit amet mi massa. In iaculis dapibus leo, ut mollis 
urna vehicula ac. Donec ultrices nibh id est porta cursus.

Cras sollicitudin faucibus diam at viverra. Vestibulum posuere ornare leo 
eget fermentum. In id erat magna. Vivamus rhoncus nunc commodo condimentum 
lacinia. Aliquam viverra tincidunt est quis varius. Nulla in erat eget nibh 
dictum pellentesque at luctus lacus. Nulla eu ipsum egestas, scelerisque est 
vitae, eleifend nulla. Morbi mattis dolor leo, in volutpat turpis molestie 
at. Quisque pulvinar at erat vitae dignissim.

Etiam non tellus sed turpis feugiat laoreet. Cras gravida erat aliquet lacus 
condimentum facilisis. Vestibulum efficitur vel nunc non sollicitudin. Nunc 
accumsan lacinia ligula, eget egestas neque mollis id. Aliquam rhoncus a 
lectus porta imperdiet. Fusce sapien justo, sodales in lacus sed, viverra 
iaculis est. Nullam posuere velit quis metus tristique lobortis ut vitae 
lectus. Vestibulum vulputate est bibendum neque facilisis, et posuere nunc 
vulputate. Vivamus blandit mi non orci malesuada molestie. Pellentesque at 
arcu elementum, semper urna eu, ultricies ante. Donec imperdiet eleifend 
ante, ut elementum justo vulputate nec. Nam imperdiet lacinia pulvinar. 
Aenean congue eleifend odio non imperdiet. Cras ut erat non metus hendrerit 
commodo eget in nisl. Integer eu lacus suscipit, volutpat ante eleifend, 
hendrerit ante.

Etiam non turpis pretium, tempor odio vel, mattis tortor. Aliquam egestas 
blandit magna, quis laoreet libero hendrerit quis. Duis id hendrerit enim. 
Praesent consectetur, nisl non maximus egestas, mi massa feugiat enim, 
vitae fringilla ligula magna a urna. Morbi quis sagittis mi, sed faucibus 
quam. Etiam tristique consequat augue, in lobortis nisi lacinia eu. 
Suspendisse massa arcu, finibus ut dui convallis, vestibulum eleifend libero. 
Aenean turpis ipsum, ullamcorper quis metus nec, sollicitudin varius erat. 
Sed consectetur nisl quis mauris luctus suscipit. Nulla eleifend dui justo, 
dapibus aliquet arcu suscipit vel. Duis scelerisque in ex et tempor.

Etiam rhoncus egestas ligula rutrum feugiat. Nulla ligula magna, hendrerit id 
dictum eu, tempus et enim. Morbi sed vulputate risus. Nunc porttitor, 
nibh sed ornare porta, augue lacus molestie nulla, vitae venenatis diam risus 
id libero. Pellentesque nec vulputate ex, a gravida justo. Nam mattis aliquam 
interdum. Fusce eget dapibus magna. Fusce vel auctor nisi. Donec a vehicula 
ligula.

Maecenas laoreet libero ac scelerisque iaculis. Vivamus vel malesuada leo. 
Aenean tincidunt facilisis ante id vestibulum. Sed ac sem nibh. Maecenas 
purus tellus, maximus vitae mauris et, fermentum varius purus. Duis cursus 
aliquet mauris in ornare. Duis congue molestie dolor non commodo. Quisque 
tempor vel massa nec posuere. Praesent eu viverra ex, vel mollis sapien. 
Nulla cursus elementum ante eget lacinia.

Aliquam ut neque interdum, maximus eros quis, gravida eros. Pellentesque 
porttitor vehicula lobortis. Donec luctus, nulla at scelerisque vestibulum, 
nunc nibh varius justo, at faucibus ex felis nec sapien. Orci varius natoque 
penatibus et magnis dis parturient montes, nascetur ridiculus mus. Proin 
gravida ac enim sit amet sagittis. In hac habitasse platea dictumst. Nullam 
fringilla semper diam non vulputate. Mauris eros metus, euismod sed gravida 
et, luctus id nulla. Vestibulum ut libero quis orci tincidunt auctor. 
Praesent at mi tincidunt, porttitor justo et, porttitor justo. Integer 
sagittis, erat nec eleifend posuere, tellus nulla rhoncus purus, ut interdum 
turpis mi in ex. Maecenas congue a nisi quis egestas. Etiam nec dolor eu nisi 
pretium egestas sed dictum turpis. Sed scelerisque eleifend nibh, at euismod 
felis dapibus vitae. Phasellus justo massa, sollicitudin non elit ac, 
tincidunt egestas elit.

Donec vel neque quis ante rutrum condimentum. Donec at lacus vitae elit 
vehicula molestie sed sed velit. Nullam placerat cursus molestie. Ut ultrices 
fringilla hendrerit. Etiam auctor sem eu risus tempor, iaculis vehicula elit 
iaculis. Duis maximus quam a velit faucibus, cursus elementum libero 
tincidunt. Cras efficitur turpis ante, quis blandit neque bibendum sit amet. 
Aliquam et nisi quam. Maecenas in purus elementum, rutrum diam eget, iaculis 
nibh. Nam placerat pretium justo.

Etiam eleifend nunc sit amet consequat vestibulum. Vestibulum tempor blandit 
elit, nec tincidunt eros mollis sit amet. Etiam dictum diam nunc, sit amet 
varius mi consectetur quis. Donec vel sem sit amet leo porttitor egestas. 
Morbi sed odio non elit euismod consequat vitae non elit. Nullam lobortis 
feugiat nisl a tincidunt. Donec efficitur venenatis congue. Curabitur et 
tellus quam. Nam sit amet justo tortor. Donec ut egestas ex. Ut eu ante sit 
amet ante semper aliquam at id lacus. Curabitur sem ipsum, sodales fringilla 
velit non, vestibulum feugiat sapien.

Aliquam efficitur libero augue, vel semper libero aliquam ut. Quisque eu 
dolor orci. Vestibulum ac libero sed augue iaculis facilisis a id leo. 
Aliquam lectus lacus, blandit id quam id, lobortis bibendum lectus. Quisque 
semper dolor a ipsum imperdiet, vel consequat urna hendrerit. Suspendisse 
posuere vel sem at posuere. Nulla in lorem leo. Suspendisse bibendum quis 
magna quis aliquam. Praesent tincidunt finibus faucibus. Donec imperdiet 
lorem vitae nunc dapibus iaculis. Sed velit tortor, commodo non aliquet et, 
auctor eget nisi. Donec quis metus nibh. Aliquam volutpat mi eget massa 
scelerisque, et mollis tortor tempor.

Aenean semper velit urna, at feugiat elit bibendum sit amet. Praesent sit 
amet arcu nec nunc rhoncus malesuada ut eu felis. Vestibulum eu ipsum velit. 
Duis odio lacus, porta ac volutpat sit amet, rutrum vel odio. Aliquam 
scelerisque vulputate nisi sed ullamcorper. Donec a ultricies neque, 
vel sodales risus. Donec accumsan posuere vestibulum.

Cras fermentum nibh dictum mi auctor, et ornare turpis facilisis. Nullam vel 
fermentum mauris. Pellentesque scelerisque vel justo nec accumsan. Aenean 
ultricies diam a neque consequat dapibus. Suspendisse gravida, ex et faucibus 
vestibulum, enim erat imperdiet velit, at suscipit enim tortor a diam. Morbi 
ut tellus fringilla, luctus sapien non, posuere nibh. Sed dignissim tortor 
ligula, quis tristique mi consequat nec. Cras tempus aliquam ante, 
quis feugiat tortor laoreet ac. Integer venenatis neque eu mauris vestibulum, 
a semper est pretium. Duis ac ex vel mi commodo suscipit quis nec quam. 
Praesent pellentesque dui quis leo ultrices interdum.

Fusce id condimentum massa. Etiam venenatis libero lobortis sapien porttitor 
mattis. Cras sit amet velit lacus. Donec vel lacinia nisi, id pulvinar 
mauris. Vestibulum imperdiet mauris vel nibh tempus, vel cursus felis 
blandit. Integer efficitur orci diam. Etiam orci ligula, ornare vulputate 
arcu vel, dapibus aliquet diam. Morbi quis nibh id nibh dictum faucibus a non 
lorem. Nullam ultrices finibus est a consequat. Sed ultricies diam a 
ullamcorper iaculis. Integer pellentesque commodo pellentesque. Praesent id 
tincidunt est.

Cras id dignissim nunc. Fusce convallis sapien sed est congue, vitae pharetra 
nunc pretium. Sed lectus lectus, condimentum vel erat in, porttitor viverra 
diam. Nunc elementum odio nulla, eu fermentum nisl imperdiet vitae. Vivamus 
hendrerit eleifend orci id condimentum. Sed dictum nunc tortor, 
quis malesuada massa tincidunt ut. Donec rutrum mi est, a blandit risus 
vehicula sagittis. Fusce dapibus, magna eu dapibus cursus, dolor arcu luctus 
mi, id porta sem purus non purus. Nullam eu condimentum mi. In nisi ipsum, 
laoreet in ante id, fringilla gravida purus.

Morbi mauris augue, dictum in commodo et, varius ultricies dolor. Proin a 
turpis venenatis, rutrum justo a, porttitor lorem. Nunc ut diam et turpis 
congue hendrerit. Aliquam erat volutpat. Lorem ipsum dolor sit amet, 
consectetur adipiscing elit. Suspendisse sed mauris turpis. Suspendisse enim 
neque, congue et arcu eget, venenatis blandit lacus. Ut vitae neque ipsum. 
Morbi efficitur est quis quam vulputate placerat. Etiam rhoncus hendrerit 
consequat. Cras dapibus magna id leo lobortis, et dapibus augue mattis. 
Quisque venenatis sit amet tellus quis aliquam.

Cras hendrerit fringilla metus, vel aliquet felis ullamcorper nec. Vestibulum 
efficitur sem et congue imperdiet. Integer vulputate tempor eros, sed euismod 
magna maximus at. Integer maximus egestas elit sit amet aliquam. Curabitur 
scelerisque magna tempor, tristique quam ut, tincidunt mi. Phasellus sit amet 
iaculis nunc. Nullam mollis, dolor quis gravida facilisis, tellus metus 
ornare magna, at pulvinar quam erat a urna.

Morbi sollicitudin dictum sem fermentum gravida. Vestibulum quis commodo 
libero. Nulla mi lacus, placerat eu porttitor varius, tempus sit amet augue. 
Nunc est nulla, convallis eu scelerisque a, varius ac nibh. Sed dictum 
tincidunt lacus id faucibus. Vivamus lacinia tempus sodales. Aliquam pulvinar 
finibus sodales.

Nunc eleifend pharetra leo, at lobortis diam. Morbi ac mauris urna. Fusce ac 
nisl ac orci tincidunt ultrices. Fusce dignissim volutpat nibh id mattis. 
Curabitur ligula massa, egestas id odio at, interdum malesuada metus. Lorem 
ipsum dolor sit amet, consectetur adipiscing elit. Fusce egestas mauris ac mi 
malesuada, quis imperdiet erat rutrum. Fusce ut vestibulum quam. Aliquam 
vitae sem dictum, rhoncus magna semper, vulputate nulla. Etiam hendrerit 
suscipit sem, ultrices bibendum lectus venenatis non. Curabitur sed mollis 
nulla. Sed vitae tortor sagittis, feugiat justo sit amet, placerat nulla. 
Suspendisse ultrices diam id velit vestibulum, vel auctor eros bibendum. In 
congue nisi id ante finibus, eu venenatis nisi accumsan.

Nam malesuada augue a neque dictum, sit amet tempor est molestie. Etiam nec 
suscipit nunc, in ultrices ligula. Aenean blandit neque quis mi convallis, 
sed pharetra felis iaculis. Mauris sed lobortis neque, id ullamcorper orci. 
Fusce quis urna nulla. Curabitur sem dolor, sollicitudin vitae iaculis vel, 
auctor a lacus. Maecenas sed commodo odio. Maecenas convallis ex diam, 
id tempor nunc cursus et. Curabitur posuere in elit sed ultrices.

Sed blandit malesuada diam viverra hendrerit. Cras at sem id ante rhoncus 
bibendum ac sed nisi. Praesent quam est, molestie quis pellentesque vitae, 
mollis vitae ante. Curabitur malesuada sit amet lectus ac laoreet. 
Pellentesque porta tortor ligula, ut tempor massa tincidunt non. Praesent 
facilisis nisl nec velit dapibus ultricies. Mauris quis lectus ut lectus 
volutpat efficitur sed eget nisl. Vivamus vestibulum eleifend ipsum quis 
gravida. Etiam ac augue nec purus blandit imperdiet. Ut tincidunt, libero ut 
pellentesque gravida, nibh felis rhoncus augue, eu blandit magna orci sit 
amet nisl. Nam pharetra mauris at augue euismod, et dapibus nibh elementum.

Nam a viverra odio, faucibus posuere tellus. Cras eget sapien pharetra, 
sodales ex quis, convallis erat. Sed semper augue ac turpis iaculis, 
ut posuere orci volutpat. In consequat, mi eget vehicula convallis, lorem mi 
posuere neque, eget blandit orci nisl ut nunc. Cras sed lorem sed nibh mollis 
auctor. Suspendisse mauris sem, pulvinar ut tincidunt nec, finibus non 
libero. Sed vitae neque velit. Sed viverra velit et felis lacinia varius. 
Class aptent taciti sociosqu ad litora torquent per conubia nostra, 
per inceptos himenaeos. Donec maximus laoreet venenatis. Aenean nec nisi 
semper, commodo magna non, volutpat felis. Fusce volutpat convallis leo, 
vitae placerat turpis interdum vitae. Nulla et augue risus.

Ut facilisis nec lacus eleifend vehicula. Vestibulum elementum lectus in 
accumsan tincidunt. Fusce sed risus nec leo feugiat suscipit facilisis non 
turpis. Proin pulvinar porttitor ante, at porttitor turpis finibus at. Nunc 
sed ipsum ac arcu finibus sollicitudin. Suspendisse a tortor in eros egestas 
varius a vitae augue. Etiam lobortis urna diam, eget sollicitudin quam 
consequat et. Proin blandit, quam vel dapibus sagittis, elit orci pharetra 
tortor, fringilla interdum odio augue vel ante. Vestibulum ante ipsum primis 
in faucibus orci luctus et ultrices posuere cubilia Curae; Fusce bibendum 
justo et sapien sollicitudin, id facilisis urna ultrices. Fusce sodales 
turpis vitae ligula tincidunt interdum. Aliquam erat volutpat. Vestibulum 
vehicula elit tristique quam mattis, at faucibus libero tempus.

Quisque vulputate feugiat nunc in vehicula. Fusce a purus mauris. Aliquam eu 
purus ac justo imperdiet tempus. Mauris egestas pellentesque dapibus. Quisque 
nisl ligula, molestie in justo at, scelerisque dapibus mi. Nullam bibendum 
nibh ut lorem vestibulum, rutrum dignissim ex accumsan. Nam varius purus eget 
commodo mattis. Vivamus placerat tortor in erat auctor, eu egestas nulla 
eleifend. Vivamus convallis arcu vitae tristique efficitur. Sed quis odio non 
nisi fringilla commodo euismod id velit. Donec leo ex, commodo eget metus 
quis, consequat tristique purus.

Donec maximus accumsan purus, a ornare tortor tincidunt pharetra. Sed nec 
vestibulum enim. Donec et rhoncus diam. Integer lobortis lobortis urna eget 
accumsan. Cras suscipit eleifend posuere. Interdum et malesuada fames ac ante 
ipsum primis in faucibus. Sed eget mi quis tortor dictum ornare in eget 
metus. Etiam at nunc iaculis, pulvinar ipsum nec, auctor turpis.

Nunc bibendum convallis egestas. Duis rhoncus nisi id ipsum tempor, 
eu fringilla nunc varius. Proin semper justo sagittis justo tristique, 
ut luctus massa pharetra. Lorem ipsum dolor sit amet, consectetur adipiscing 
elit. Phasellus tincidunt et velit eget ultrices. Fusce auctor faucibus 
magna, eu maximus eros. Ut sed ultricies leo, porta sodales neque. Phasellus 
mollis, mi sed volutpat tincidunt, sapien nisi dignissim purus, vel gravida 
augue lectus sit amet purus. Pellentesque ut rutrum mi. Aliquam et elit vel 
ligula volutpat rhoncus nec lacinia nulla. Fusce est lorem, vehicula sit amet 
congue quis, viverra non dui. Proin at laoreet orci.

Nullam vitae hendrerit felis. Suspendisse est lacus, laoreet a sollicitudin 
quis, commodo ac est. Pellentesque lorem risus, pulvinar auctor erat 
sollicitudin, mattis tristique sem. Quisque viverra nibh eget tortor 
consectetur, sit amet ullamcorper tortor porta. Etiam consectetur 
sollicitudin mauris, et suscipit enim sagittis eu. Donec sollicitudin 
consequat orci ut faucibus. Integer turpis nibh, malesuada ac augue vitae, 
tristique rutrum urna. Nulla tincidunt porta enim, nec facilisis tellus 
ullamcorper nec. Sed sit amet nibh vitae ex rutrum bibendum ut quis lectus. 
Nam ac tincidunt ex. Vestibulum ante ipsum primis in faucibus orci luctus et 
ultrices posuere cubilia Curae;

Praesent mi lacus, molestie vitae ante vel, blandit porta tortor. Aenean 
sagittis blandit leo, eget finibus lectus mattis non. Curabitur elementum 
ultrices feugiat. Nam vehicula vestibulum est, vel dignissim orci gravida ac. 
Pellentesque vehicula ut magna at condimentum. Orci varius natoque penatibus 
et magnis dis parturient montes, nascetur ridiculus mus. Mauris ut facilisis 
diam, sed cursus mi. Ut sagittis vehicula dui vitae consectetur.

Vestibulum a euismod ante. Duis vel sodales lorem. Nunc erat nisl, cursus 
eget sem eget, sollicitudin gravida leo. Mauris tincidunt laoreet eleifend. 
Duis mattis porttitor arcu, ac porttitor diam sodales et. Donec vulputate 
lorem eu justo sodales iaculis. Morbi id tincidunt odio.

Fusce sit amet risus ac ante aliquam tempor. Quisque non euismod risus. 
Pellentesque sed aliquet justo. Vivamus vestibulum lectus quis urna gravida, 
quis fringilla nulla elementum. Praesent auctor mollis lacus a gravida. 
Praesent odio lorem, cursus finibus arcu ut, rutrum sodales dolor. Duis eget 
felis sit amet sapien lacinia euismod. Ut ut finibus lacus. Aliquam erat 
volutpat. Suspendisse sit amet neque non nisi aliquam elementum. Nulla a 
interdum eros, non porta eros. Donec bibendum sed nibh lacinia hendrerit. Nam 
at lobortis ante, et semper quam.

Nullam ornare suscipit mauris sed mattis. Integer tristique id nisl id 
aliquet. Etiam nec massa sit amet lacus ullamcorper bibendum quis ac ante. 
Nullam mattis felis nec lacus porttitor finibus. Suspendisse sem turpis, 
consectetur vel diam id, suscipit pellentesque lorem. Morbi consectetur arcu 
id ipsum pellentesque, nec iaculis lorem pretium. Vestibulum tincidunt nisi 
sem, ac dignissim leo vulputate sodales. Integer sollicitudin ligula augue, 
non gravida justo ullamcorper eu. Cras lorem arcu, sodales id tortor a, 
vulputate tristique erat. Duis justo dolor, bibendum non semper eu, lacinia 
et nisl. Vestibulum sed aliquet dolor, non ultricies ex. Duis a erat et 
ligula eleifend pretium ac sed mauris. Pellentesque habitant morbi tristique 
senectus et netus et malesuada fames ac turpis egestas. Sed commodo diam est, 
vitae rutrum justo tincidunt et. Praesent accumsan rutrum efficitur.

Nam et eros et orci porttitor faucibus vitae eget tortor. Donec quis ex ut 
dolor elementum semper. Phasellus sit amet tellus eu eros pharetra fermentum 
laoreet non sapien. Etiam non risus ac elit suscipit vulputate. Maecenas 
sagittis pulvinar ipsum, at aliquet dolor rhoncus at. Quisque pellentesque 
mattis urna, ut iaculis odio pulvinar sed. Proin eu tempor purus. Integer non 
maximus dui. Sed rutrum dignissim felis nec auctor. Fusce rhoncus, lectus 
eget faucibus congue, tortor magna luctus nisl, auctor luctus nisl lacus quis 
ex. Fusce diam augue, cursus a quam eu, sodales dignissim dui. Pellentesque 
non feugiat nisi. Ut porta imperdiet erat rhoncus faucibus. Nullam diam ante, 
blandit eget malesuada in, tincidunt ut nulla. Praesent ac lorem a ante 
hendrerit sagittis. Vivamus in nulla condimentum, semper risus a, suscipit 
augue.

Nam vitae lorem vestibulum, consequat ligula et, pulvinar nibh. Phasellus dui 
nisl, blandit eget congue eget, pulvinar sed tellus. Phasellus vel massa in 
quam tempor varius. Donec neque turpis, vehicula id felis a, lacinia 
venenatis ipsum. Aliquam a nunc lacinia, ultrices magna ornare, ullamcorper 
lectus. Aenean ipsum diam, maximus id tempor quis, facilisis eu turpis. Morbi 
rutrum eu quam eget vestibulum. Donec lacinia lacinia elit ut tincidunt. Sed 
vel consequat mi. Quisque rutrum, nisi non semper pharetra, nunc odio cursus 
purus, in posuere nibh neque ac diam. Proin congue congue nulla. Vestibulum 
at fermentum neque.

Maecenas fermentum, justo vitae finibus consequat, tellus odio mattis mi, 
eu sodales tortor mauris sed lectus. Nullam eleifend nibh et semper 
sollicitudin. Nullam cursus egestas mauris nec malesuada. Mauris malesuada 
feugiat enim et tincidunt. Sed a libero semper, commodo neque id, faucibus 
risus. Interdum et malesuada fames ac ante ipsum primis in faucibus. 
Curabitur scelerisque faucibus placerat. Mauris eget luctus sapien, 
vitae gravida diam. Cras ut augue non libero facilisis semper eu at felis. 
Aliquam tellus nunc, aliquet at pellentesque at, malesuada vitae massa. 
Vivamus mauris nunc, aliquam nec tincidunt non, sollicitudin a lectus. Sed 
venenatis nec turpis eget semper.

Nunc bibendum, leo nec imperdiet blandit, magna augue pulvinar neque, gravida 
tincidunt justo purus eget risus. Praesent nec hendrerit augue, nec consequat 
eros. Fusce vel interdum est, nec maximus sapien. Nullam vel enim sed lorem 
scelerisque molestie. Donec non sapien lacus. Proin ullamcorper sed dolor et 
cursus. Duis id justo at lectus dapibus venenatis a ac est.

Etiam vel arcu nisi. Morbi sagittis dolor vitae tristique feugiat. Morbi sed 
varius elit. Mauris nec lorem in sem vestibulum aliquam. Donec et mi egestas, 
tristique augue at, condimentum ex. Phasellus molestie urna arcu, in varius 
lectus tincidunt a. Pellentesque quis felis nunc. Curabitur viverra nibh sed 
urna ultricies egestas. Aenean nulla tortor, rhoncus vitae semper eu, mattis 
sit amet eros. Mauris convallis diam vel neque efficitur, eu tincidunt enim 
vulputate.

Morbi sit amet eleifend orci. Donec vestibulum, tortor non faucibus eleifend, 
dui magna elementum enim, ac scelerisque sapien velit eu ligula. Nunc 
interdum magna eu aliquet faucibus. Proin odio leo, tristique non purus ut, 
placerat pharetra lorem. Donec fermentum iaculis urna vitae aliquam. 
Vestibulum in sapien luctus, tempor lorem et, eleifend neque. Morbi cursus 
tortor ac velit dapibus, vel varius sapien vestibulum.

Donec non pretium quam. Nam ex turpis, tempus non interdum eget, sollicitudin 
ac dui. Donec tempor quam suscipit lacus tincidunt suscipit. Maecenas 
pellentesque luctus euismod. Nullam eu viverra neque, at scelerisque mauris. 
Duis a condimentum eros. Donec diam magna, commodo vel quam pulvinar, 
tristique tempor dolor. Sed quis augue interdum, eleifend tortor id, molestie 
erat.

Mauris purus orci, dapibus varius diam a, tempus porta velit. Mauris diam 
dui, convallis et dolor ut, pellentesque semper augue. Etiam turpis elit, 
mollis eget lobortis a, commodo in nibh. Vestibulum vulputate placerat diam 
ut lacinia. Nunc ac elit diam. Donec vitae maximus lorem. Aenean ultrices, 
est non varius rhoncus, nulla enim auctor lectus, at egestas neque est in 
diam. Praesent lorem leo, lobortis non venenatis nec, varius vel ante. Duis 
rutrum consectetur orci, nec cursus tortor aliquam vitae. Nunc pellentesque 
congue diam ac tristique.

Curabitur tempor tincidunt arcu ac pellentesque. Nullam tincidunt dui et 
turpis ullamcorper, nec pretium orci commodo. Phasellus eu turpis 
condimentum, luctus quam eget, sagittis augue. Nunc nunc ex, commodo id 
pretium vitae, placerat eu ipsum. Aenean at viverra arcu, vel pharetra mi. 
Nullam in cursus lorem. Mauris at lectus arcu. In hac habitasse platea 
dictumst. Vestibulum condimentum tellus lectus, egestas semper odio ultricies 
in. Curabitur fringilla eget augue sed convallis. Fusce tellus ipsum, pretium 
non velit at, porttitor gravida augue. Praesent et tellus sed massa commodo 
laoreet. Donec eu dignissim felis. Fusce elementum viverra metus, at tempor 
risus porta sit amet.
'''.lstrip()

# Gets around 500 chars.
lorem_about_500 = lorem_ipsum[:lorem_ipsum.find(' ', 500)]
