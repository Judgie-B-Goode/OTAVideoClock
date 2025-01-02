#V1.1 - fixed bug caused by people leaving playlists open at the forefront when a scheduled show starts.
import requests
import tkinter as tk
import tkinter.font as tkFont
import datetime

f = open("ip.txt")
ipinfo = f.read().splitlines()
f.close()
endpoint = "http://"+ ipinfo[1]+":" + ipinfo[3] + "/"
formatted_time = ""
next_live = ""


def otavplaystatus(endpoint):
    try:
        playbackpoint = "playback/playing"
        status = requests.get(endpoint + playbackpoint)
        statusjson = status.json()
    except:
        return ['STOPPED', '']
    else:
        if statusjson['playback_status'] != 'Stopped' and statusjson['playback_status'] != 'Closed':
            if 'item_display_name' in statusjson:
                return [statusjson['item_display_name'],statusjson['item_remaining']]
            else:
                try:
                    return[statusjson['item_filename'],statusjson['item_remaining']]
                except:
                    return ['STOPPED', '']
        else:
            return['STOPPED', '']


def update_playing():
    current_time = datetime.datetime.now()
    hours = current_time.strftime("%H")
    minutes = current_time.strftime('%M')
    current_formatted_time = hours + ':' + minutes
    global next_live
    global formatted_time
    updatetime = otavplaystatus(endpoint)
    if updatetime[0] != "STOPPED":
        formatted_time = "0" + str(datetime.timedelta(seconds=int(updatetime[1])))
    else:
        timer1["fg"] = 'white'
        timer1["text"] = current_formatted_time
    otavgetplaylist(endpoint)
    root.after(300, update_playing)


def otavgetplaylist(endpoint):
    global next_live
    global formatted_time
    try:
        playbackpoint = "playback/playing"
        currentplayback = requests.get(endpoint + playbackpoint)
        currentplaybackjson = currentplayback.json()
    except:
        pass
    else:
        if 'playlist_unique_id' in currentplaybackjson:
            uniqueid = currentplaybackjson['playlist_unique_id']
        else:
            uniqueid = 'STOPPED'
        if 'item_unique_id' in currentplaybackjson:
            playuniqueid = currentplaybackjson['item_unique_id']
        else: playuniqueid = 'STOPPED'
        playlistitems = endpoint + "playlists/" + uniqueid + "/items"
        status = requests.get(playlistitems)
        statusjson = status.json()
        for x in statusjson:
            if playuniqueid != 'STOPPED':
                if playuniqueid == x['unique_id']:
                    if x['clip_type'] == 4:
                        timer1["fg"] = "red"
                        timer1["text"] = formatted_time
                    else:
                        timer1["fg"] = "white"
                        if "remaining_time_until_next_live" in currentplaybackjson:
                            timer1.configure(justify="left")
                            next_live = "NEXT LIVE IN: " + "0" + \
                                        str(datetime.timedelta(
                                            seconds=int(currentplaybackjson['remaining_time_until_next_live'])))
                            timer1["text"] = next_live
                        else:
                            next_live = "NO LIVE LEFT IN SHOW"
                            timer1["text"] = next_live



root = tk.Tk()
# setting title
# setting window size
width = 1280
height = 720
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(alignstr)
root.resizable(width=True, height=True)
root.configure(bg='black')
root.overrideredirect(1)

timer1 = tk.Label(root)
ft = tkFont.Font(family='Proxima', size=70)
timer1["font"] = ft
timer1["fg"] = "red"
timer1["bg"] = "black"
timer1["text"] = "00:00:00"
timer1["justify"] = "center"
timer1.place(x=10, y=10, width=1280, height=80)

update_playing()
root.mainloop()
