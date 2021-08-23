#!/srv/MusicBot/venv/bin/python3

# Imports
from youtube_api import YouTubeDataAPI, youtube_api_utils
import ts3
import re
import json
import urllib.request
import isodate

from include.Parse import Parse
from include.Song import Song
from include.actions import write, start, quit, download

# Config
login = ''
password = ''
channel_id = 1
user_id = 1
query_nickname = 'MusicBot'
api_key = ''


# Connect to TeamSpeak3 Server
with ts3.query.TS3Connection('localhost') as ts3conn:
    try:
        ts3conn.login(client_login_name=login, client_login_password=password)
    except ts3.query.TS3QueryError as e:
        print('Login failed: ', e.resp.error['msg'])
        exit(1)

    # Configure Query
    ts3conn.use(sid=1)
    ts3conn.clientupdate(client_nickname=query_nickname)

    # Move Query to channel_id
    q = ts3conn.whoami()
    query_id = q.parsed[0]['client_id']
    ts3conn.clientmove(clid=query_id, cid=channel_id)

    # Start Teamspeak3 Client
    client_running = start()

    # Start Youtube Api Connection
    yt = YouTubeDataAPI(api_key)

    # Listen to commands on channel with id channel_id
    ts3conn.servernotifyregister(event='textchannel', id_=channel_id)

    while True:
        ts3conn.send_keepalive()

        try:
            event = ts3conn.wait_for_event(timeout=60)
        except ts3.query.TS3TimeoutError:
            pass
        else:
            msg = event.parsed[0]['msg']

            if msg[0] == '!':
                c = Parse(msg)

                # !help 
                if c.args[0] == '!help' and c.args_num == 1:
                    write(ts3conn, channel_id, ' ')
                    write(ts3conn, channel_id, '[b][color=green]Komendy:[/color][/b]')
                    write(ts3conn, channel_id, '- !yt <link> / [i]Odtwarzaj z youtube[/i]')
                    write(ts3conn, channel_id, '- !pause / [i]Zatrzymaj / wznów odtwarzanie[/i]')
                    write(ts3conn, channel_id, '- !volume <0-100> / [i]Zmień głośność[/i]')
                    write(ts3conn, channel_id, '- !skip <0-5000> / [i]Przewiń o czas podany w sekundach[/i]')
                    write(ts3conn, channel_id, '- !start / [i]Uruchom bota[/i]')
                    write(ts3conn, channel_id, '- !quit / [i]Wyłącz bota[/i]')
                    write(ts3conn, channel_id, ' ')

                # !pause
                elif c.args[0] == '!pause' and c.args_num == 1:
                    write(ts3conn, channel_id, '[b]Zatrzymuje / wznawiam odtwarzanie ...[/b]')
                    try: song.pause()
                    except: pass

                # !yt
                elif c.args[0] == '!yt':
                    if c.args_num == 2:
                        pattern = '^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'
                        video_url = c.args[1]
                        result = re.match(pattern, video_url)

                        if result:
                            try: song.stop()
                            except: pass

                            # Get video title from Youtube Data Api v3
                            video_id = youtube_api_utils.strip_video_id_from_url(video_url)
                            video_metadata = yt.get_video_metadata(video_id)
                            video_title = video_metadata['video_title']

                            write(ts3conn, channel_id, f'[b][color=red]Youtube[/color][/b] - [url={video_url}]{video_title}[/url]')
                            try:
                                song = Song(url = c.args[1])
                                song.play()
                            except:
                                searchUrl=f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=contentDetails'
                                
                                with urllib.request.urlopen(searchUrl) as connection:
                                    response = connection.read()
                                
                                data = json.loads(response)
                                all_data = data['items']
                                contentDetails = all_data[0]['contentDetails']
                                duration = contentDetails['duration']
                                duration = isodate.parse_duration(duration)
                                video_duration = duration.total_seconds()

                                if(video_duration > 1800):
                                    write(ts3conn, channel_id, f'[b][color=red]Youtube[/color][/b] - Nie można odtwarzać filmów z ograniczeniem wiekowym, które są dłuższe niż 30 minut.')
                                else:
                                    write(ts3conn, channel_id, f'[b][color=red]Youtube[/color][/b] - nie można odtworzyć filmu, prawdopodobnie posiada on ograniczenie wiekowe, próbuję pobrać ...')
                                    download(video_url)
                                    song = Song(file = True)
                                    song.play()
                            
                        else:
                            write(ts3conn, channel_id, 1)
                    else:
                        write(ts3conn, channel_id, 1)

                # !volume
                elif c.args[0] == '!volume':
                    if c.args_num == 2:
                        try: volume = int(c.args[1])
                        except: write(ts3conn, channel_id, 2)
                        else:
                            if volume >= 0 and volume <= 100:
                                write(ts3conn, channel_id, f'[b][color=cornflowerblue]Głośność[/color][/b] - {c.args[1]}/100')
                                try:
                                    song.volume(volume)
                                    ts3conn.clientdbedit(cldbid = user_id, client_description=f'Głośność - {c.args[1]}/100')
                                except: pass
                            else:
                                write(ts3conn, channel_id, 2)
                    else:
                        write(ts3conn, channel_id, 2)

                # !skip
                elif c.args[0] == '!skip':
                    if c.args_num == 2:
                        try: forward = int(c.args[1])
                        except: write(ts3conn, channel_id, 3)
                        else:
                            if forward >= 0 and forward <= 5000:
                                write(ts3conn, channel_id, f'[b][color=coral]Przewijanie[/color][/b] - {c.args[1]} sekund')
                                try: song.skip(forward)
                                except: pass
                            else:
                                write(ts3conn, channel_id, 3)
                    else:
                        write(ts3conn, channel_id, 3)

                # !start
                elif c.args[0] == '!start' and c.args_num == 1:
                    if not client_running:
                        write(ts3conn, channel_id, '[b]Włączam bota ...[/b]')
                        client_running = start()
                    else:
                        write(ts3conn, channel_id, '[b]Bot jest już włączony.[/b]')

                # !quit
                elif c.args[0] == '!quit' and c.args_num == 1:
                    if client_running:
                        write(ts3conn, channel_id, '[b]Wyłączam bota ...[/b]')
                        try: client_running = quit(song)
                        except:
                            song = False
                            client_running = quit(song)
                    else:
                        write(ts3conn, channel_id, '[b]Bot nie jest włączony.[/b]')

                # cannot find command
                else:
                    write(ts3conn, channel_id, 0)

