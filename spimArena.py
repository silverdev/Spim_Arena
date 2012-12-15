from subprocess import Popen;
from subprocess import PIPE;
import sys
try:
    from collections import Counter
except ImportError:
    try:
        from recipe5766111 import Counter
    except ImportError:
        print "Counter not found"
        sys.exit(1)

import getopt
import time
import random
import signal
from math import log


class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

signal.signal(signal.SIGALRM, alarm_handler)


class Logger() :
    def __init__(self, log_file=None):
		self.log_file = log_file
                self.log = None
                if log_file != None :
                    self.log= open(log_file, "w")
                    
    def output(self,output) :
        if self.log == None :
            print output
        else :
            print output
            self.log.write(str(output))
            self.log.write("\n")
    def __del__(self):
		if self.log != None :
                    self.log.closed 
    
    

class game() :

    def __init__(self, roundsPerGame,logfile=None,time_out=0,seed=None):
         self.roundsPerGame =int(roundsPerGame)
         self.time_out= int(time_out)
         self.rand = random
         self.rand.seed(seed)
         self.logger=Logger(logfile)
         
    def manual_override(self,playerOne,playerTwo,gameSeed) :
        print ""
        print "manual override enabled"
        while(True):
            print "1) declare "+playerOne+" the winner \n" + \
                "2) declare "+playerTwo+" the winner\n" + \
                "3) reload game on the same map \n"+ \
                "4) reload game on new map \n" + \
                "q) quit spimArena"
            command=raw_input("--->")
            if command == "1" :
                return playerOne
            if command == "2" :
                return playerTwo
            if command == "3" :
                return self.runMatch(playerOne,playerTwo,gameSeed)
            if command == "4" :
                return self.runMatch(playerOne,playerTwo,str(self.rand.randint(1355029990,1355039990)))
            if command == "q" :
                sys.exit(0)
            print "invaled key"
  
        
    def runMatch(self,playerOne, playerTwo,gameSeed) :

       
        try :
            inline= Popen("./QtSpimbot -file "+playerOne+" -file2 "+playerTwo
                         + " -randomseed "+gameSeed+ " -randommap  -run -exit_when_done -maponly -quiet ",\
                              stdout=PIPE, shell=True).stdout
            string = "not"
            while(not (string == '')) :
                string = inline.readline()
                if string[:7] == "winner:"  :
                    return string[8:-1]

            print "\nerror, What? This should not be so? Did you quit qtSpim?"
            return self.manual_override(playerOne,playerTwo,gameSeed)

        except KeyboardInterrupt:
            return self.manual_override(playerOne,playerTwo,gameSeed)

        except Alarm:
            print "timeOut"
            killerror= Popen("killall QtSpimbot", stdout=PIPE, shell=True).stdout
            print killerror.read()
            time.sleep(1)
            return "#fail#" 
       
    def gameRunner(self,playerOne, playerTwo):
        count=Counter()
        if playerOne in ("#byeGame#", "#fail#") :
            self.logger.output(playerTwo+" wins from byegame")
            return playerTwo
        if playerTwo in ("#byeGame#", "#fail#") :
            self.logger.output(playerOne+" wins from byegame")
            return playerOne

        for x in xrange(0, self.roundsPerGame) :
            if self.time_out != 0 :
                print self.time_out
                print "using alarm"
                signal.alarm(self.time_out)
            mapSeed=str(self.rand.randint(1355029990,1355039990))
#use a random number that is simler to the output of C rand()
            self.logger.output(playerOne +" vs. "+playerTwo +" game "+str(x+1) +" out of "
                               +str(self.roundsPerGame) + " on map seed " + mapSeed)
            roundwinner=self.runMatch(playerOne, playerTwo, mapSeed)
            self.logger.output(roundwinner+" wins")
            count[roundwinner] +=1 
        self.logger.output( count.most_common())
        return count.most_common(1)[0][0]


class basicTree() :
    def __init__(self, game, teams):
         self.game= game
         self.bracket=teams
         self.round=0
         self.ranking = Counter()
         self.looserList =[]
         
    def winnerBracket(self) :
        self.game.logger.output(self.bracket)
        if len(self.bracket)==1 : #check for final round
            return self.finalRounds()
        self.round+=1
        self.game.logger.output("round "+str(self.round)+" start")
        winnerList =[]
        half_list=len(self.bracket)/2
        for x in xrange(0,half_list):
            winner=self.game.gameRunner(self.bracket[x],self.bracket[x+half_list])

            if winner == self.bracket[x] :
                winnerList.append(winner)
                self.looserList.append(self.bracket[x+half_list])
            elif winner == self.bracket[x+half_list] :
                winnerList.append(winner)
                self.looserList.append(self.bracket[x])
            else :
                print "error"
                sys.exit(1)
        
        self.bracket=winnerList
        return self.looserBracket()
        
        
        
    def looserBracket(self) :
        self.game.logger.output("looser Bracket")
        self.game.logger.output(self.looserList)
        keepList =[]
        half_list=len(self.looserList)/2
        for x in xrange(0,half_list):
            winner=self.game.gameRunner(self.looserList[x],self.looserList[x+half_list])
            if winner == self.looserList[x] :
                keepList.append(winner)
                self.ranking[self.looserList[x+half_list]]=self.round
            else :
                keepList.append(winner)
                self.ranking[self.looserList[x]]=self.round
        if len(self.looserList) ==3 :
            keepList.append(self.looserList[2]) #for semi-final lossermach to keep the thrird team.
        self.looserList=keepList
        return self.winnerBracket()
                
    def finalRounds(self) :
        if len(self.looserList)==2 :
            self.game.logger.output("looser bracket final")
            return self.looserBracket()
        self.game.logger.output("final Round")
        self.round+=1
        winner=self.game.gameRunner(self.bracket[0],self.looserList[0])
        if winner==self.looserList[0] :
             game.logger.output("tie breaker round")
             winner=self.game.gameRunner(self.bracket[0],self.looserList[0])
        self.game.logger.output("the winner is " + winner)
        if winner==self.looserList[0] :
             self.ranking[self.bracket[0]]=self.round
             self.ranking[winner]=(self.round+1)
             return self.ranking
        if winner==self.bracket[0] :
             self.ranking[self.looserList[0]]=self.round
             self.ranking[winner]=(self.round+1)
             return self.ranking
        return "error"

    def rungame(self) :
        playerCount =len(self.bracket)
        treesize= 2**(1+int(log(playerCount,2)))
        byrounds=treesize-playerCount
        for x in xrange(0,byrounds) :
            self.bracket.append("#byeGame#")
        random.shuffle(self.bracket)  #ensures fairness by randomizing the bracket
        self.game.logger.output(self.winnerBracket())
        return self.ranking

def teamReader(thefile) :
       teams = []
       with open (thefile) as t :
           while True :
               string=t.readline()
               if string == "" :
                   t.close()
                   return teams
               teams.append(string[:-1])
def usage() :
    print """ Spim Arena -a tournament runner for spimbot 
-Sam Laane

 usage: spimArena [-r rounds-per-game] [-t timeout] [-o output_file] file

 -r : number of rounds per game. defalt is 1
 -t : set a timeout on a match. 0 will disable it.  default is 0   
(dont use it!  if a match takes to long just override it and set a winner")
 -o : set the log file to save the outcome\

the input file shoud be a list the the teams competing 

*note don't chose an even number of rounds per game. 
If you do and there is a tie the winner with be chosen arbitrarily 
 """

def main() :
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hr:t:o:", ["help", "logfile=", 
                                                             "--timeout","--rounds-per-game"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output = None
    timeout=0
    match_num =1   
    for o, a in opts:
        if o in ("-r", "--rounds-per-game"):
            match_num=a
        elif o in ("-t", "--timeout") :
            timeout=a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--logfile"):
            output = a
        else:
            assert False, "unknown option"
    try :
        list_of_teams = args[0]
    except IndexError: 
        print "missing team list"
        sys.exit(1)
    theGame= game(match_num, output, timeout)
    theTeams=teamReader(list_of_teams)
    tournament=basicTree(theGame,theTeams)
    print tournament.rungame().most_common()

if __name__ == "__main__" :    
   main()
