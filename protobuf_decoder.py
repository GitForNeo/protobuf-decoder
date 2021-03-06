from burp import IBurpExtender
from burp import IMessageEditorTabFactory
from burp import IMessageEditorTab
from burp import IParameter
from java.io import PrintWriter
import sys
from javax.crypto import Cipher
from javax.crypto.spec import SecretKeySpec
from javax.crypto.spec import IvParameterSpec
from java.util import Base64
import traceback
import subprocess
import base64
import array
import ast
import json

#sys.path.append('/usr/local/lib/python2.7/site-packages')
#sys.path.append('/Library/Python/2.7/site-packages')


class BurpExtender(IBurpExtender, IMessageEditorTabFactory):
    
    def registerExtenderCallbacks(self, callbacks):
        sys.stdout = callbacks.getStdout()
        sys.stderr = callbacks.getStderr()
        # keep a reference to our callbacks object
        self.callbacks = callbacks
        self.stdout = PrintWriter(callbacks.getStdout(), True)
        self.stderr = PrintWriter(callbacks.getStderr(), True)      
        # obtain an extension helpers object
        self.helpers = callbacks.getHelpers()
        
        # set our extension name
        callbacks.setExtensionName("Protobuf Decoder")
        
        # register ourselves as a message editor tab factory
        callbacks.registerMessageEditorTabFactory(self)

        return
    
    def createNewInstance(self, controller, editable):
        
        # create a new instance of our custom editor tab
        return AESHelperTab(self, controller, editable)
        

# 
# class implementing IMessageEditorTab
#

class AESHelperTab(IMessageEditorTab):

    def __init__(self, extender, controller, editable):
        self.extender = extender
        self.editable = editable
        self.controller = controller

        # create an instance of Burp's text editor, to display our deserialized data
        self.txtInput = extender.callbacks.createTextEditor()
        self.txtInput.setEditable(editable)

        self.httpHeaders = None
        self.body = None
        self.content = None

        return

    def getTabCaption(self):
        return "Protobuf Plain Text"
        
    def getUiComponent(self):
        return self.txtInput.getComponent()
    
    def isEnabled(self, content, isRequest):

        return True
        #if isRequest:
        #    req = self.extender.helpers.analyzeRequest(content)
        #    headers = req.getHeaders()

        #    if "Host: smpsjlgpp.linegame.jp:10010" in headers:
        #        self.key = pokopang_key
        #        return not self.extender.helpers.getRequestParameter(content, "q") is None

        #    elif "Host: lgpkpk-game.linegame.jp:10010" in headers:
        #        self.key = pokopoko_key
        #        return not self.extender.helpers.getRequestParameter(content, "q") is None

        #    else:
        #        return False
        #else:

        #    return True

                

    def isModified(self):
        return self.txtInput.isTextModified()

    def getSelectedData(self):
        return self.txtInput.getSelectedText()

    def setMessage(self, content, isRequest):
 
        host = self.controller.getHttpService().getHost()

        if (content is None):
            # clear our display
            self.txtInput.setText(None)
            self.txtInput.setEditable(False)

        if host == "pgorelease.nianticlabs.com" or True:
            res = self.extender.helpers.analyzeResponse(content)
            self.httpHeaders = res.getHeaders() #remember headers

            data = content[res.getBodyOffset():]

            f = open('tmp.pb', 'wb')
            f.write(bytearray(data))
            f.close()

            parsedJson = ''
            try:
                #proc = subprocess.Popen(['python', '/Users/nevermoe/Documents/git_code/protobuf_test/parse.py',\
                #        'dec'],\
                #        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc = subprocess.Popen(['python', 'parse.py','dec'],\
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc.wait()
                #f = open('tmp.json', 'r')
                ##parsedJson = json.load(f)
                #parsedJson = f.read()
                #f.close()
            except:
                print traceback.format_exc()

            output = proc.stdout.read()
            errors = proc.stderr.read()
            print "output: %s" % (output)
            print "errors: %s" % (errors)

            try:
                f = open('tmp.json', 'r')
                parsedJson = json.load(f)
                f.close()
                pretty = json.dumps(parsedJson, indent=4, sort_keys=True) 
                self.txtInput.setText(pretty)
                text = self.txtInput.getText()
                self.txtInput.setEditable(True)
            except:
                print traceback.format_exc()


        self.currentMessage = content

        return

    def getMessage(self):

        if (self.txtInput.isTextModified()):

            try:
                text = self.txtInput.getText()
                f = open('tmp.json', 'w')
                jsonFormat = json.loads(text.tostring())
                json.dump(jsonFormat, f, indent=4, sort_keys = True)
                f.close()
            except:
                print traceback.format_exc()

                
            try:
                #proc = subprocess.Popen(['python', '/Users/nevermoe/Documents/git_code/protobuf_test/parse.py',\
                #        'enc'],\
                #        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc = subprocess.Popen(['python', 'parse.py', 'enc'],\
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc.wait()
                output = proc.stdout.read()
                errors = proc.stderr.read()
            except:
                print traceback.format_exc()

            print "output: %s" % (output)
            print "error: %s" % (errors)
            try:
                f = open('tmp.pb', 'rb')
                message = f.read()
                f.close()
                content = self.extender.helpers.buildHttpMessage(self.httpHeaders, message)
            except:
                print traceback.format_exc()
            return content

        else:
            return self.currentMessage

