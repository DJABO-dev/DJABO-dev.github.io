# DJABO-dev.github.io
Denon Engine DJ App workaround to synchronize Playlists in LINUX

All work is done!

This program is designed to sync playlists, smartlists, tracks files, stem files and SoundSwitch files between internal or external drives and performance decks with internal storage to work with Engine Library properly in Linux environment.

Engine DJ software run well with wine in Linux, but it can't sync anything. USB drives are not present on the interface and them can't be used to sync.

This program is an external tool that allows the synchronization of libraries between external and internal drives so that Engine DJ can be used in Linux environment in a complete way.

This is the final version 1.1

News:

1 - Added synchronize from and to any mounted drives. USB and hard disk drives. To anybody who has his library in a secondary internal disk.

2 - Added a system to find real route to track when it's marked as red in Engine DJ. This can update path info in the db file by file or all files at same time. This only search inside the same drive of original path. This can't find tracks with filename changed. This is a speedy way to update path. No search by metadata. Procedure: Select playlist and clic on see tracks button. You will see a window with the playlist selected. Open it and you will see the list of tracks. If some of them are red you can clic button repair reds on the upper right corner. Otherwise the button will be disabled. You will be asked if you want repair one by one or all at the same time.

3 - Added a system to synchronize SmartList. SmartList only can be read by Engine DJ from home music folder of user, but now you can transfer it to any drive and then transfer it to home library music folder in any other PC.

4 - Updated system to synchronize home music folder from external drives. When you use a external drive and open Engine Dj, the database is copied to home music library folder, but these playlists are marked as not persisted  and they won't be visible on Engine DJ software. Now, if you synchronize from external drive to internal library, these playlists are marked as persisted in database to make them accesible when you don't have external drive connected. Tracks, stem files and SoundSwitch files will be transfered. In the GUI, the playlists than have been transfered to home user library but they won´t be visible by Engine DJ software are marked with forbiden simbol 📛. This only work when destination of sync is home music library folder. (Stay in right side of GUI)

5 - Playlists are marked with 📀 simbol when not selected, and those selected to sync are marked with ✅. You don't need to mark anything in right side to sync. Righ side marking is to see list of tracks of every playlist selected and repair red ones in case. You can see track list on both, left side and right side and repair them in case with the same procedure.

5 - Solved some issues with buttons activations.

If anyone finds any errors, please let me know. If anyone can improve the code, please share it with everyone.

That's all. I sincerely hope that this tool will be useful to people who are having problems with the database, playlist synchronization and annoying red files. And if I encourage anyone to use Linux, I'll be happy to hear about it.

Thank you very much.
Regards.



