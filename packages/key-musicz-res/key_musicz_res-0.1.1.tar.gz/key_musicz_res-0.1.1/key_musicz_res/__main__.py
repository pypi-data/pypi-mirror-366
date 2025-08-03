#
import sys,os
from buildz import argx,xf
dp = os.path.dirname(__file__)
sfile = os.path.join(dp,'res', 'piano1_from_TimGM6mb.sf2')
libpath = os.path.join(dp, 'win_lib')
fetch = argx.Fetch(*xf.loads("[fp,sfile,libpath,default,help],{f:fp,s:sfile,l:libpath,t:default,h:help}"))
conf = fetch(sys.argv[1:])
if 'sfile' not in conf:
    conf['sfile'] = sfile
if 'libpath' not in conf:
    conf['libpath'] = libpath
if 'default' not in conf:
    conf['default'] = 'playrb.js'
kvs = [f"--{k}={v}" for k,v in conf.items()]
sys.argv = sys.argv[:1]+kvs
print("params after key_musicz_res changes:", sys.argv[1:])
from key_musicz import conf
conf.test()

'''
python -m key_musicz_res
'''