import xml.etree.cElementTree as ET
import os
import pickle
import numpy as np
import platform
import json
import sys
import time
import inspect
from subprocess import Popen, PIPE
from sklearn.metrics import f1_score, accuracy_score
# sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+os.sep+'libs64')
# import vhmsg_python
'''
The method to send NPCEditor a question/list of questions and get answers is as follows:
Create an xml file like this:

<requests ID="QUESTION_LIST_ID" agentName="">
 <request target="All" ID="QUESTION_ID" source="bar"><field name="text">Hello</field></request>
 <request target="All" ID="QUESTION_ID2" source="bar"><field name="text">Hello</field></request>
</requests>
 
Returned xml will be like this:
 
<responses ID="QUESTION_LIST_ID">
 <response target="All" ID="QUESTION_ID" source="bar">
  <answers>
   <utterance score="0.000">
    <field name="text">Hi</field>
    <field name="id">RESPONSE_ID</field>
   </utterance>
  </answers>
 </response>
...
</responses>
 
 
Before you can send it to the editor, you need to create a batch account in NPCEditor.
Make sure the agentName in the xml message is the same as the agent name on the batch account.
The source field in the request must be same as the "Scores for: " field in NPCEditor, on the question side. 
The "Scores for: " field on the answer side must be the name of the account. For a clearer understanding, 
please see the image in the README file.
 
Send the xml like this:
java -cp /absolute/path/to/npceditor.jar:absolute/path/to/plugins/batch_plugin.jar edu.usc.ict.npc.server.net.ipc.BatchModule --stdin file-name.xml
Check code below on how to send the request.
'''

class NPCEditor(object):
    def __init__(self):
        self.requests=ET.Element('requests', ID='L1', agentName='clintanderson')
        self.response=""
        self.y_pred=[]
        self.test_data=None
        self.x_test=None
        self.y_test=None
        self.test_questions=None
        self.train_questions=[]
        self.answered_question=False

    def load_test_data(self):
        self.test_data=json.load(open(os.path.join("test_data","lr_test_data.json"),'r'))
        self.x_test=[self.test_data[i][1] for i in range(len(self.test_data))]
        self.y_test=[self.test_data[i][3] for i in range(len(self.test_data))]
        [self.test_data[i][0] for i in range(len(self.test_data))]
    '''
    This method is used to create xml file for a set of questions. This is used only when testing out the classifier with the 
    entire test set. This big xml file is sent to NPCEditor.
    '''
    def create_full_xml(self):
        i=0
        for question in self.test_questions:
            request=ET.SubElement(self.requests,'request', target="All", ID="question_"+str(i), source="Anybody")
            ET.SubElement(request, "field", name="text").text = question
            i+=1
            #self.train_questions.append("question_"+str(i))
        tree=ET.ElementTree(self.requests)
        tree.write(os.path.join("xml_messages","npceditor_request.xml"))
    
    '''
    When a question is asked, this method creates an xml file for that one question only. This xml is sent to NPCEditor.
    '''
    def create_single_xml(self, question):
        request=ET.SubElement(self.requests,'request', target="All", ID="question_1", source="Anybody")
        ET.SubElement(request, "field", name="text").text = question
        tree=ET.ElementTree(self.requests)
        tree.write(os.path.join("xml_messages","npceditor_request.xml")) 

    # def PrintResult(self, result):
    #     print("SUCCESS" if result==0 else "FAILURE")

    # def vhmsg_callback(self, str):
    #     print(str)
    #     #send xml for parsing
    #     self.answered_question=True

    # def listen(self):
    #     update_interval=0.25
    #     while not self.answered_question:
    #         time.sleep(update_interval)
    #         vhmsg_python.poll()

    # def setup_vhmsg(self):
    #     vhmsg_python.connect("localhost", "DEFAULT_SCOPE", "61616")
    #     vhmsg_python.subscribe("vrExpress")
    #     vhmsg_python.setListener(self.vhmsg_callback)

    # def close_vhmsg(self):
    #     vhmsg_python.wait(1)
    #     vhmsg_python.close()
    '''
    Send an xml file as a request to NPCEditor.
    '''
    def send_request(self, question):
        # vhmsg_python.send("vrSpeech start test1 user")
        # vhmsg_python.send("vrSpeech finished-speaking test1 user")
        # vhmsg_python.send("vrSpeech interp test1 1 1.0 normal "+question)
        # vhmsg_python.send("vrSpeech asr-complete test1")
        # listen()

        os_name=platform.system()
        if os_name=='Darwin' or os_name=='Linux':
            cmd=Popen(["java", "-cp", os.path.join("..","NPCEditor.app","npceditor.jar")+":"+os.path.join("..","NPCEditor.app","plugins","batch_plugin.jar"),"edu.usc.ict.npc.server.net.ipc.BatchModule","--stdin", os.path.join("xml_messages","npceditor_request.xml")], stdout=PIPE)
            cmd_out, cmd_err=cmd.communicate()
            output=cmd_out.decode("utf-8").split('\n')
            self.response=output[-2][55:]
            
        elif os_name=='Windows':
            cmd=Popen(["java", "-cp", os.path.join("..","NPCEditor.app","npceditor.jar")+";"+os.path.join("..","NPCEditor.app","plugins","batch_plugin.jar"),"edu.usc.ict.npc.server.net.ipc.BatchModule","--stdin", os.path.join("xml_messages","npceditor_request.xml")], stdout=PIPE)
            cmd_out, cmd_err=cmd.communicate()
            output=cmd_out.decode("cp437").split('\n')
            self.response=output[-2][55:]

    '''
    Parse the xml file that is returned when the big xml file with a set of questions is sent to NPCEditor.
    This method is used only when testing the performance of the system.
    '''
    def parse_full_xml(self):
        responses=ET.fromstring(self.response)
        for response in responses:
            for answer in response:
                try:
                    score=answer[0].attrib['score']
                    id=answer[0][0].text
                    ans=answer[0][1].text
                    self.y_pred.append((score, id))
                except:
                    self.y_pred.append((-100.0,"answer_none"))
        preds=[item[1] for item in self.y_pred]
        print("Accuracy: "+str(accuracy_score(self.y_test, preds)))
        print("F-1: "+str(f1_score(self.y_test, preds, average='micro')))
        return self.y_test, self.y_pred

    '''
    Parse the xml file that is returned when the xml file with a single question is sent to NPCEditor.
    This method is used whenever the user asks a new question. This method returns the answer to the ensemble classifier.
    '''
    def parse_single_xml(self):
        responses=ET.fromstring(self.response)
        answer=""
        id=None
        score=-100.0
        for response in responses:
            for answer in response:
                try:
                    score=answer[0].attrib['score']
                    id=answer[0][0].text
                    answer=answer[0][1].text
                except:
                    answer="answer_none"
        return id, score, answer