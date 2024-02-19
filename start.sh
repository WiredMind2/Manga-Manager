#!/bin/bash

cd $HOME/Documents/Mangas
#screen -dmS manga_server bash "$HOME/Documents/Mangas/run_server.sh"
#screen -dmS ngrok bash "$HOME/Documents/Mangas/run_ngrok.sh"
screen -dmS manga_downloader bash "$HOME/Documents/Mangas/run_downloader.sh"
