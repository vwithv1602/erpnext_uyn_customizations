import datetime
def vwrite(contenttowrite):
    file_name = "vuyncustomizationslogfile_%s.txt" % datetime.datetime.now().date()
    target = open(file_name, 'a+')
    target.write("\n==========================="+str(datetime.datetime.now())+"===========================\n")
    target.write("\n"+str(contenttowrite)+"\n")
    target.close()

def uyndebug(contenttowrite):
    target = open("debuguyncustomizations.txt", 'a+')
    target.write("\n===========================" + str(datetime.datetime.now()) + "===========================\n")
    target.write("\n" + str(contenttowrite) + "\n")
    target.close()
