@echo off

echo Deleting registry entries for Video Cutter...

for %%X in (mp4 avi) do (
    reg delete "HKCR\SystemFileAssociations\.%%X\shell\Cut Video" /f
)

echo All registry entries have been removed!
pause
