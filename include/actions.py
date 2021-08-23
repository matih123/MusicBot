from time import sleep
import subprocess

def start():
    # Start TeamSpeak3 Client
    subprocess.Popen(['/opt/teamspeak3-client/ts3client_runscript.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    sleep(6)

    return True

def quit(song):
    # Stop VLC Player
    try: song.stop()
    except: pass

    # Stop TeamSpeak3 Client
    pgrep = subprocess.run(['pgrep', 'ts3client_linux'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    pid = int(pgrep.stdout)
    subprocess.run(['kill', f'{pid}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return False

def write(ts3conn, channel_id, msg):
    # Send channel message
    error_message = []
    error_message.append('[b][color=red]Nieznana komenda[/color][/b] - Użyj !help')
    error_message.append('[b][color=red]Youtube[/color][/b] - !yt <link>')
    error_message.append('[b][color=cornflowerblue]Głośność[/color][/b] - !volume <0-100>')
    error_message.append('[b][color=coral]Przewijanie[/color][/b] - !skip <0-5000>')

    if msg == 0:
        msg = error_message[0]
    elif msg == 1:
        msg = error_message[1]
    elif msg == 2:
        msg = error_message[2]
    elif msg == 3:
        msg = error_message[3]

    ts3conn.sendtextmessage(targetmode=2, target=channel_id, msg=msg)

def download(link):
    subprocess.run(['rm /tmp/ts3musicbot.mp3'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sleep(1)
    subprocess.run([f'ytdl {link} | ffmpeg -i pipe:0 -b:a 192K -vn /tmp/ts3musicbot.mp3'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    sleep(2)
