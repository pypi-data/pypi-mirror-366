Bcolors = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bblack": "\033[90m",
    "bred": "\033[91m",
    "bgreen": "\033[92m",
    "byellow": "\033[93m",
    "blue": "\033[94m",
    "bmagenta": "\033[95m",
    "bcyan": "\033[96m",
    "bwhite": "\033[97m",
}

Fcolors ={
    "blak": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "manganete": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
    "bblack": "\033[100m",
    "bred": "\033[101m",
    "bgreen": "\033[102m",
    "byellow": "\033[103m",
    "bblue": "\033[104m",
    "bmagenta": "\033[105m",
    "bcyan": "\033[106m",
    "bwhite": "\033[107m",
}
"""
styles = {
    "bold": "\033[1m",
    "underline": "\033[4m",
    "reverse": "\033[7m",
    "dim": "\033[2m",
    "blink": "\033[5m",
    "hidden": "\033[8m",
    "normal": "\033[22m"
}
"""
styles = {
    "b": "\033[1m",
    "dim": "\033[2m",
    "i": "\033[3m",           # Not supported in all terminals
    "u": "\033[4m",
    "blink": "\033[5m",
    "fast_blink": "\033[6m",       # Not always supported
    "reverse": "\033[7m",
    "hidden": "\033[8m",
    "nor": "\033[22m",
}
reset="\033[0m"

def abuB(text,bgs):
    for listColor,v in Bcolors.items():
        if bgs == listColor:
            return v + text + "\033[0m"
def abuF(text,fgs):
    for listBcolor,v in Fcolors.items():
        if fgs == listBcolor:
            return v+text+"\033[0m"
def abuS(text,sty):
    for listStyle,v in styles.items():
        if listStyle == sty:
            return v+text+"\033[0m"
# version 0.1 this have logic complex
"""
def AbuAll(text,bg=None,fg=None,sty=None):
    values=[]
    if bg is not None and fg is None and sty is None:
        for li,v in Bcolors.items():
            if bg == li:
                values.append(text)
                break
        return v + ''.join(values)+reset
    elif (bg and fg) is not None:
        #return "Yes it is not none"
        pass
"""
def AbuAll(text,bg=None,fg=None,sty=None):
    colored = ""
    if bg in Bcolors:
        colored += Bcolors[bg]
    if fg in Bcolors:
        colored += Fcolors[fg]
    if sty != None: 
        if isinstance(sty,list):
            for stys in sty:
                if stys in styles:
                    colored += styles[stys]
        elif isinstance(sty,str):
            colored += styles[sty]
    return colored+text+reset
#print(AbuAll("Abujelal",fg="yellow",bg="white",sty=["u","b"]))
#print(AbuAll("AbexMan",bg="black",fg="green",sty=["bold","underline","italic"]))
#print(abuB("Abebaw","red"))
#print(abuF("Abujelal",f"green"))
#print(abuS("It is Bold","underline"))
#print("Not colored")