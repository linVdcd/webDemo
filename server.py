#!/usr/bin/python
#coding=utf-8
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import query_rank_api as qapi

PORT_NUMBER = 8080

api = qapi.API()


#This class will handles any incoming request from
#the browser
class myHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"

        try:
            # Check the file extension required and
            # set the right mime type

            sendReply = False
            if self.path.endswith(".html"):
                mimetype = 'text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype = 'image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype = 'image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype = 'application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype = 'text/css'
                sendReply = True

            if sendReply == True:
                # Open the static file requested and send it
                f = open(curdir + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
            if self.path == "/segment":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                self.send_response(200)
                self.end_headers()
                post_data = post_data.decode('utf-8')

                try:

                    scores, resources, sentiment, sentence, sww,debuginfo = api.query(post_data)

                    self.wfile.write("句子处理结果：" + sentence + "---" + "句子情感类别：" + str(sentiment) + '(0:负面，1：正面)\n')

                    if len(scores) == 0:
                        self.wfile.write('句子：['+str(post_data.strip('\n'))+']'+"没有相应的元动作\n")
                        return
                    for score_item in scores:
                        res_id = score_item[0]
                        res_score = score_item[1]
                        self.wfile.write('\n')
                        re = "名称:" + resources[res_id]['name'] + "---得分:" + str(round(res_score, 3)) + "---情感：" + str(resources[res_id]['sentiment_type']) + "---关键字:" + sww[res_id] + '\n'
                        self.wfile.write(re)

                        for item in debuginfo[res_id]:
                            self.wfile.write('  '+item+'\n')
                except UnboundLocalError:
                    self.wfile.write('句子：['+str(post_data)+']'+'没有找到关键词')
            return


try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER

	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
