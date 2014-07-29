#!/usr/bin/env python
#coding=utf-8
#author laoseng
#create 2014-04-25
#function is biasagent main file 
import os, sys, platform,re,json
import BaseHTTPServer
from SocketServer import ThreadingMixIn
import time,urllib,shutil
import utils
     
def modification_date(filename):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getmtime(filename)))
 
class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
            print self.path
            uri=self.path
            
            print self.path.find("?")
            if self.path.find("?")>=0:
                end_uri_num=self.path.index("?")
                uri=self.path[:end_uri_num]
                print uri
            if uri=="/" or uri=="/index.html" or uri=="/index":
                src_file = open(index_file, 'rb')
                index_file_str=""
                while True:
                  data=src_file.readline()
                  if not data:
                     break
                  index_file_str=index_file_str+data
                dir_list=utils.get_conf_dirlist(conf_file)
                dir_files_dict=utils.get_dir_files(dir_list[0])
                add_str=""
                l_files=dir_files_dict[dir_list[0]]
                for file_tmp in l_files:
                        add_str=add_str+"<option value='"+file_tmp+"'>"+file_tmp+"</option>"

                #find flag html
                flag_str="add_allow_file-->"
                num=index_file_str.index(flag_str)+len(flag_str)
                start_str=index_file_str[:num]
                end_str=index_file_str[num:]

                #add string
                index_file_str=start_str+add_str+end_str
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                self.wfile.write(index_file_str)
                src_file.close()
            elif re.match(r"^\/static\/.+",uri) and os.path.isfile(global_path+uri):
                src_file=open(global_path+uri)
                self.send_response(200)
                if re.match(r".*\.js$",uri):
                        print("----js")
                        self.send_header("Content-type", "application/x-javascript")
                elif re.match(r"\.jpg",uri):
                        self.send_response(200)
                        self.send_header("Content-type", "image/jpeg")
            
                self.end_headers()
                shutil.copyfileobj(src_file,self.wfile )
                src_file.close()
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("<html><title>log easy</title><body>404<body></html>")

    def do_POST(self):
            datas = self.rfile.read(int(self.headers['content-length']))
            datas = urllib.unquote(datas).decode("utf-8", 'ignore')
            datas = utils.transDicts(datas)
            if datas.has_key('data'):  
                content = "data:"+datas['data']+"\r\n" 
            cmd=datas['cmd']
            f=self.wfile
            if cmd=="taillog":
                filename=datas['allowfile']
                dir_tmp=os.path.split(filename)[0]
                dir_list=utils.get_conf_dirlist(global_path+"/config/bias.conf")
                if utils.is_path_allow(dir_list,dir_tmp)==0:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        data_buffer="<span style='color:red'>dir is forbidden</span>"
                        f.write(data_buffer)
                        return
            
                linenum=datas['linenum']
                if linenum=="" or linenum==0:
                        linenum=10
                if os.path.isfile(filename):
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        data_buffer=utils.tail(filename,linenum)
                        f.write(data_buffer)
                else:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        data_buffer="<span style='color:red'>filename  is dir ,please check!</span>"
                        f.write(data_buffer)
            
            elif cmd=="sysinfo":
                sysinfo=dict()
                sysinfo['meminfo']=utils.meminfo()
                sysinfo['loadinfo']=utils.loadinfo()
                sysinfo_json = json.dumps(sysinfo)
                self.send_response(200)
                self.send_header("Content-type", "application/Json")
                self.end_headers()
                f.write(sysinfo_json)
            elif cmd=="listlog":
                self.send_response(200)
                self.send_header("Content-type", "application/Json")
                self.end_headers()
                f.write(sysinfo)

    def do_HEAD(self):
            send_head(self)

    def send_head(self):
        path = self.path
        self.send_response(200)
        self.end_headers()
        return
 
class ThreadingServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass
     
if __name__ == '__main__':
    global_path="/home/work/app/biasagent"
    file_err='%s/deamon_err.log' %global_path
    file_out='%s/deamon_out.log' %global_path
    utils.daemon(global_path,file_out,file_err,"/dev/null")
    conf_file="%s/config/bias.conf" %global_path
    index_file="%s/index.html" %global_path
    serveraddr = ('', 9999)
    os.chdir(global_path)
    srvr = ThreadingServer(serveraddr, SimpleHTTPRequestHandler)
    srvr.serve_forever()
