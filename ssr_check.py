#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: zwker
# mail: xiaoyu0720@gmail.com
# Created Time: 2018年03月24日 星期六 09时55分19秒
#########################################################################

import urllib

import sys
import re
import os
import ping

if __name__ == '__main__':
	import inspect
	file_path = os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe())))
	sys.path.insert(0, os.path.join(file_path, '../'))

import argparse
import atexit
import json
import base64
from urlparse import urlparse, parse_qs

ssr_prefix = "ssr://"
ssr_prefix_len = len(ssr_prefix)

def get_parser():
	parser = argparse.ArgumentParser(description = u"decode the ssr file and generate the valid ssr string for your shadowsocks client", epilog="this will help set the shadowsocks config.json faster.")
	parser.add_argument("ssr_file", nargs = '?' , default = './freessr.list', help = 'ssr_file' )
	return parser.parse_args()

def b64pading(enc):
	'''
	base64补充等号填充方法
	'''
	if (len(enc) % 4) != 0 :
		enc += '=' * (4 - (len(enc) % 4))
		#print("b64pading:[{0}]".format(enc))

	return enc

def decode_ssr_uri( ssr_uri_string ):
	'''
	decode shadowsocksR uri string , format like ssr://aldkfaldkfdlwofdfj...dfa=
	'''
	ssr_encode_string = ""
	ssr_decode_string = ""
	conf_json = dict()
	if( ssr_uri_string.startswith( ssr_prefix ) ):
		ssr_encode_string = ssr_uri_string[ssr_prefix_len:]
	ssr_split_array = ssr_encode_string.split('_')
	if len(ssr_split_array) == 2 :
		i1_ssr = base64.decodestring( b64pading( ssr_split_array[0] ) );
		i2_ssr = base64.decodestring( b64pading( ssr_split_array[1] ) );
		ssr_decode_string = "{0}?obfsparam={1}".format( i1_ssr , i2_ssr)
	else :
		ssr_decode_string = base64.decodestring( b64pading(ssr_encode_string) )

	ssr_decode_string = ssr_prefix + ssr_decode_string
	ssr_params=parse_qs(urlparse(ssr_decode_string).query)
	# print("urlparse.netloc:{0}".format(urlparse(ssr_decode_string)))
	result = urlparse(ssr_decode_string).netloc
	## SSR格式：ssr://server:server_port:method:protocol:obfs:base64-encode-password/?obfsparam=base64-encode-string&protoparam=base64-encode-string&remarks=base64-encode-string&group=base64-encode-string
	##服务端信息设置
	server_info = result.split(':')
	server_ip , server_port , protocol, method ,obfs  = server_info[0], server_info[1],server_info[2],server_info[3],server_info[4]

	try:
		delay = ping.do_one( server_ip , 1 , 60 )
		if delay != None :
			print("{0} {1} {2:.5}s {3}".format( server_ip , server_port , delay, ssr_uri_string ))
	except :
		pass
	server_port = int(server_port)
	return

def main_decode():
	'''
	功能： 解析输出IP：PORT ： ssr_uri_string
	'''
	args = get_parser()
	ssr_file = args.ssr_file

	with open( ssr_file , "r") as f:
		for ss_uri in f:
			## decode the ss-uri string
			if ss_uri.startswith(ssr_prefix) :
				decode_ssr_uri( ss_uri.strip() )

if __name__ == "__main__" :
	main_decode()
