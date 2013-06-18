from Data.dataAccess import DataAccess
from config import siena_config
import json

class Login(object):
    exposed = True
    
    def __init__(self):
        self._dao = DataAccess()
        
    def GET(self, unick=''):

        sql= 'SELECT userId, languageId FROM Users WHERE nickname=%(nickname)s'
        args = {'nickname': unick}

        result = self._dao.sql.getSingle(sql, args, {'userId':-1, 'languageId': -1})
        
        ret = "%(userId)s,%(languageId)s" % result
        return ret

class Options(object):
    exposed = True
    
    def __init__(self):
        self._dao = DataAccess()
        
    def GET(self, ulang='-1', pid='-1'):

        sql="SELECT \
                a.idActionPossibilityOptions AS id, \
                a.OptionName AS name, \
                a.PossibleValues AS 'values', \
                a.DefaultValue AS 'default' \
            FROM \
                ActionPossibilityOptions a INNER JOIN\
                ActionPossibility_APOptions o ON a.idActionPossibilityOptions = o.idOpt \
            WHERE \
                o.idAP = %(sonid)s"
        args = {'sonid': pid }

        results = self._dao.sql.getData(sql, args)
        return json.dumps(results)

class Command(object):
    exposed = True
    
    def __init__(self):
        self._dao = DataAccess()
        
    def GET(self, cmd_id='-1'):

        sql = "UPDATE `Sensors` SET `value`='1' WHERE `sensorId`=%(cmd)s"
        args = {'cmd': cmd_id }

        self._dao.sql.saveData(sql, args)
        return "OK"
        
class ExpressionRequest(object):
    exposed = True
    
    def __init__(self):
        self._dao = DataAccess()
        
    def GET(self, cmd_id='-1'):

        sql="SELECT expression FROM GUIexpression WHERE ison='1' limit 1;"

        result = self._dao.sql.getSingle(sql)
        if result == None:
            return "error"
        else:
            return result['expression']

class FullActionList(object):
    exposed = True
    
    def __init__(self):
        self._dao = DataAccess()
        self._likelihood = siena_config['likelihood']
        
    def GET(self):

        sql="SELECT label_text, phrase, type_description, likelihood, apId, location_name, precondId FROM \
             (SELECT (SELECT message FROM Messages WHERE messageId=a.ap_text and languageId=1) AS label_text, \
             ActionPossibilityType.text AS type_description,a.parentId,a.apId AS apId,(SELECT message FROM Messages WHERE messageId=a.ap_phrase and languageId=1) AS phrase, \
             a.likelihood, a.precondId, Locations.name as location_name, Locations.locationId FROM ActionPossibilities a, ActionPossibilityType, Locations WHERE \
             a.apTypeId = ActionPossibilityType.apTypeId AND parentId IS null AND Locations.locationId = a.locationId AND a.likelihood > %(threshold)s ) AS pinco"
        args = {'threshold': self._likelihood }

        results = self._dao.sql.getData(sql, args)
        return json.dumps(results)

class RobotActions(object):
    exposed = True
    
    def __init__(self):
        self._dao = DataAccess()
        self._likelihood = siena_config['likelihood']
        
    def GET(self, ulang='1', robot='Care-O-Bot 3.6'):

        sql="SELECT label_text, phrase, type_description, likelihood, apId, precondId FROM \
             (SELECT (SELECT message FROM Messages WHERE messageId=a.ap_text and languageId=%(lang)s) AS label_text, \
             ActionPossibilityType.text AS type_description,a.parentId,a.apId AS apId,(Select message FROM Messages WHERE messageId=a.ap_phrase AND languageId=%(lang)s) AS phrase, \
             a.likelihood, a.precondId from ActionPossibilities a, ActionPossibilityType, Locations WHERE \
             a.apTypeId = ActionPossibilityType.apTypeId AND parentId IS null AND Locations.locationId = a.locationId AND Locations.locationId=(SELECT locationId FROM Robot WHERE robotName=%(robot)s) AND a.likelihood > %(threshold)s ) AS pinco ORDER BY likelihood DESC"
        
        args = {'threshold': self._likelihood, 'lang': ulang, 'robot': robot }

        results = self._dao.sql.getData(sql, args)
        return json.dumps(results)

class SonsActions(object):
    exposed = True
    
    def __init__(self):
        self._dao = DataAccess()
        self._likelihood = siena_config['likelihood']
        
    def GET(self, ulang='-1', pid='-1'):

        sql="SELECT label_text, phrase, type_description, precondId, likelihood, apId FROM \
             (SELECT (SELECT message FROM Messages WHERE messageId=a.ap_text and languageId=%(lang)s) AS label_text, \
             ActionPossibilityType.text AS type_description,a.parentId,a.apId AS apId,(SELECT message FROM Messages where messageId=a.ap_phrase AND languageId=%(lang)s) AS phrase, \
             a.likelihood, a.precondId FROM ActionPossibilities a, ActionPossibilityType WHERE \
             a.apTypeId = ActionPossibilityType.apTypeId AND parentId = %(parent)s AND a.likelihood > %(threshold)s) AS pinco"
        
        args = {'threshold': self._likelihood, 'lang': ulang, 'parent': pid }

        results = self._dao.sql.getData(sql, args)
        return json.dumps(results)

class UserActions(object):
    exposed = True
    
    def __init__(self):
        self._dao = DataAccess()
        self._likelihood = siena_config['likelihood']
        
    def GET(self, uid='-1', ulang='-1'):

        sql="SELECT label_text, phrase, type_description, likelihood, apId, precondId FROM \
             (SELECT (SELECT message FROM Messages WHERE messageId=a.ap_text and languageId=%(lang)s) AS label_text, \
             ActionPossibilityType.text AS type_description,a.parentId,a.apId AS apId,(SELECT message FROM Messages where messageId=a.ap_phrase and languageId=1) AS phrase, \
             a.likelihood, a.precondId FROM ActionPossibilities a, ActionPossibilityType, Locations WHERE \
             a.apTypeId = ActionPossibilityType.apTypeId AND parentId IS null AND Locations.locationId = a.locationId AND Locations.locationId=(SELECT locationId FROM Users WHERE userId=%(user)s) AND a.likelihood > %(threshold)s ) AS pinco ORDER BY likelihood DESC"
        
        args = {'threshold': self._likelihood, 'lang': ulang, 'user': uid }

        results = self._dao.sql.getData(sql, args)
        return json.dumps(results)

class SetParameter(object):
    exposed = True
    
    def __init__(self):
        self._dao = DataAccess()
        
    def GET(self, opt_id='-1', val='-1'):

        sql = 'UPDATE ActionPossibilityOptions SET SelectedValue=%(value)s WHERE idActionPossibilityOptions=%(optId)s'
        args = {'value': val, 'optId': opt_id }

        self._dao.sql.saveData(sql, args)
        return "OK"
