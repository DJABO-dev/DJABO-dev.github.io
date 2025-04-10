# DJABO-dev.github.io
Denon Engine DJ App workaround to synchronize Playlists in LINUX

AppImage EngineSynchronize-x86_64.AppImage

First version is completed. Now it can transfer playlist from music folder of user to any USB drive, including STEMS and SOUNDSWITCH FILES. Or from one USB drive to another.

First of all, I’ve created a way to recognize USB drives. This can be made pushing a button. The USB drives then become selectionable from the combobox controls. When you do this, you get the content of Engine database in that drive.

Here is a short video to show it:

https://ant.japiworld.com:5443/WebRTCApp/streams/247758961056920249497381.mp4

The next thing is to create a empy database if you select a drive where there is no Engine Library folder. This database is a copy of Library folder when you just installed the software.

Again, here is a short video of this:

https://ant.japiworld.com:5443/WebRTCApp/streams/954139798241363817310321.mp4

Next, you have a origin database from a USB drive. And want to synchronize some Playlist to a USB stick. Or have a USB drive with Playlists and want to synchronize to user music folder of PC. You only need to select the desired Playlist from the left, push procesing button and then push Sinchronize button. You need to select some database on the right side (obviously). Remember, always LEFT TO RIGHT.

Video:

https://ant.japiworld.com:5443/WebRTCApp/streams/882780550710418896075422.mp4

And finaly, you have changed CUES and LOOPS from one USB drive (or any other drive), and want to send these changes to another performance USB drive previusly synchronized. When you select from the left the playlist changed, and have the same Playlist on the right, you can go in the same way to sync this Playlist and select it from the left. No need to select anything on the right. Proccess and Synchronize. The Playlist will be updated with the new performance data from the updated info on the left.

In this video I show you this process. First I set some CUES and LOOP to a track on “DJ_BACKUP” USB drive from Engine DJ software. Then you can see than these CUES and LOOP are not on “DENON_DJ” usb drive (Unmount DJ_BACKUP drive, and mount DENON_DJ drive) then, I open again Engine DJ. Once the units are both mounted, I put the changed library on the left (DJ_BACKUP) and unchanged library on the right (DENON_DJ) and sychronize them.

Now, library on DENON_DJ have the same CUES and LOOP. The library on the right has been updated with the info from the library on the left selected Playlist.

https://ant.japiworld.com:5443/WebRTCApp/streams/178193795903407661501845.mp4

Warnings:
You’ll never change anything of the left selected library. Only the right selection will be altered. This is a important tip if you want to test it.

This program only (by now) can add data to the right selected library. To delete a Playlist you can use Engine Dj directly on Linux (with wine).
