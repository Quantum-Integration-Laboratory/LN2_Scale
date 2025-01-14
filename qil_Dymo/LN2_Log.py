from . import scale

import os
from datetime import datetime,time
import sys
from slack_sdk import WebClient
import yaml
import glob

#Redudntant to do it here and in the class but want PATH in global scope
with open('./config.yml','r') as file:
    config=yaml.safe_load(file)
PATH=config['logging']['PATH']
PLOTNAME='TEMP/Latest.png'


class scaleLog:
    def __init__(self,TESTING=False) -> None:
        #import our config, save a few variables and put a few in global
        self.digestYAML()
        #Make sure we have the specified folder structure
        self.firstTimeSetup()
        if not TESTING:
            try:
                #connect to the scale and get the weight
                self.usb=scale.USB(vendor_id=self.config['scales']['VID'], product_id=self.config['scales']['PID'])
                self.weight=self.usb.get_weight()
                #Pass on scale errors
                if type(self.weight)==type(str):
                    raise ValueError("ERROR with Scale: ", +self.weight)
                #get the weight as a percentage of the max
                self.percent=(self.weight-self.config['weight']['DRY_WEIGHT'])/self.MAX
            except Exception as e:
                self.error(e)
                raise e
            
            #Write our weight to the latest file
            self.logToLatest()

            #Check if we haven't already sent a message
            with open('./flags.yml','r') as file:
                self.flags=yaml.safe_load(file)
                SEND_FLAG=self.flags['SEND_FLAG']
                ITERATOR=self.flags['ITERATOR']
            
            #If we are very low get the correct messages and send without an image, this will spam every update
            #unless we are in after hours
            if self.percent<=self.VERY_LOW and not self.isAfterHours() and self.isNHoursPassed(ITERATOR):
                message=self.config['slack']['VERY_LOW_MESSAGE']%round(self.percent*100,0)
                channel=self.config['slack']['VERY_LOW_CHANNEL']
                self.sendMessage(False,message,channel)
                #self.flipSendFlag()
            #if we are low and haven't sent a message get the correct message and send a message with an image, also generate a new log file
            elif self.percent<=self.LOW and SEND_FLAG:
                message=self.config['slack']['LOW_MESSAGE']%round(self.percent*100,0)
                channel=self.config['slack']['LOW_CHANNEL']
                self.sendMessage(self.PLOTTING,message,channel)
                self.newLogFile()
                self.flipSendFlag()
            #unflip the send flag once we refil
            elif self.percent>self.LOW and not SEND_FLAG:
                self.flipSendFlag()
    def digestYAML(self):
        with open('./config.yml','r') as file:
            config=yaml.safe_load(file)
        
        self.config=config
        
        #WEIGHT
        self.LOW=config['weight']['LOW']
        self.VERY_LOW=config['weight']['VERY_LOW']
        self.MAX=self.config['weight']['MAX_WEIGHT']-self.config['weight']['DRY_WEIGHT']
        
        #Logging
        global PATH
        PATH=config['logging']['PATH']
        self.LOGNAME=config['logging']['LOGNAME']

        #Slack
        self.PLOTTING=config['slack']['PLOTTING']
        self.REPEAT_HOURS=config['slack']['PLOTTING']

    def flipSendFlag(self):
        #read and flip the send flag and save 
        with open('./flags.yml','w') as file:
            self.flags['SEND_FLAG']^=True
            self.flags['ITERATOR']=0#reset the iterator as its only used in very low situations where this isn't called
            yaml.dump(self.flags,file)
            
    def sendMessage(self,plot,message,channel):
        #instantiate bluey
        bot=simpleSlackBotBluey(channel)
        if plot:
            return self.plotMessage(bot,message)
        else:
            return bot.sendMessage(message)
        
    def error(self,e):
        import traceback
        TS=datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        name=PATH+"TEMP/CrashLog-"+TS+".log"
        with open(name,'w') as f:
            f.write(str(e)+'\n')
            f.write(traceback.format_exc()) 
        
        #Extra level of logging that sends a message to the maintainer if there is a crash
        if self.config["logging"]["ALERT_CRASH"]:
            message="Error with scale, please go check on it.\n\t%s"%e
            try:
                maintainer=str(os.environ.get('MAINTAINER_SLACK_CHANNEL'))
            except:
                with open(name,'w') as f:
                    f.write("\n\nAssuming no maintianer set add an environment variable with the maintainers channel id\m")
                    f.write(str(e)+'\n')
                    f.write(traceback.format_exc()) 
        
            self.sendMessage(False,message,maintainer)
        
    def logToLatest(self):     
        #Find the most recent file, 
        logfile=findLatestFile(PATH)
        #Write time weight and percent to file
        with open(logfile,'a') as file:
            TS=datetime.now().isoformat()
            file.write("%s, %s, %s\n"%(TS,self.weight,self.percent*100))
    def plotMessage(self,bot,message):
        
        import pandas as pd
        import matplotlib.pyplot as plt
        
        latest= findLatestFile()
        #read our latest file to get its data
        data= pd.read_csv(latest,header=None,names=["TS","weight","Percent"])
        
        #generate a proper timestamp
        TS=[datetime.fromisoformat(x) for x in data["TS"]]
        
        #Plot said file
        plt.plot(TS,data["weight"],'*-')
        plt.xlabel("Timestamp")
        plt.ylabel("Weight (kg)")
        plt.xticks(rotation=45, ha='right')
        
        #Save plot
        plot_file=PATH+PLOTNAME
        plt.savefig(plot_file,bbox_inches='tight',dpi=300)

        #Send a message with the plot
        bot.sendFileMessage(message,plot_file)
        
        #delete the file it will be overwritten anyway
        if self.config['logging']['REMOVE_OLD']:
            os.remove(plot_file)

    def newLogFile(self):
        #Generate a new empty log file labeled by the current date and hour
        TS=datetime.now().strftime("%y-%m-%d-%H")
        with open(PATH+TS+self.LOGNAME+'.csv','w') as f:
            pass
    

    def firstTimeSetup(self):
        #Checks if our path structure exists and there are files in it
        if not os.path.exists(PATH):
            os.makedirs(PATH)
            os.makedirs(PATH+'/TEMP')
            self.newLogFile()
        elif not glob.glob(PATH+"/*.csv"):
            self.newLogFile()
    def isAfterHours(self):
        startTime=self.config['slack']['START_AFTER_HOURS']
        endTime=self.config['slack']['STOP_AFTER_HOURS']
        nowTime=datetime.now().hour

        if startTime < endTime:
            return startTime <= nowTime <= endTime
        else: #Over midnight
            return nowTime >= startTime or nowTime <= endTime
    def isNHoursPassed(self,ITERATOR):
        ret=ITERATOR%self.REPEAT_HOURS==0
        return ret
            
class simpleSlackBotBluey:
    def __init__(self,channel:str,id:bool=False):
        #Slackbot capable of sending messages
        self.token=str(os.environ.get('SLACK_BOT_TOKEN'))
        self.client = WebClient(self.token)
        if id:
            self.channel=channel
        else:
            self.channel=self.getChannelId(channel)    
    def sendMessage(self,message:str,channel=None):
       if channel==None:
           channel=self.channel
       
       return self.client.chat_postMessage(channel=channel,text=message)
    def sendFileMessage(self,message:str,imfile:str,channel=None):
        if channel==None:
           channel=self.channel
        return self.client.files_upload_v2(channel=channel,title="test",file=imfile,initial_comment=message)
    def getChannelId(self,channel:str):
        """
        Returns the id of the channel based on its name is probably longer than it needs to be but blame the API
        ______________
        
        Paramaters:
            channel (str): the channel name to search for 
        Return:
            id (str): the channels id
        """
        channelList=self.client.conversations_list()['channels']
        channel=next(item for item in channelList if item["name"] == channel)
        id=channel["id"]
        return id


def findLatestFile(path=PATH):
    #Gets all csv files in the loggin path and returns the last one
    files=glob.glob(path+'*.csv')
    return files[-1]
