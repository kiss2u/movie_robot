#!/bin/sh

if ! which docker >/dev/null; then
    echo "你没有安装Docker，请先完成Docker安装后再使用安装脚本！"
    exit 1
fi
if ! which docker-compose >/dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    docker-compose --version
fi
ifNotExistsThenCreate() {
  if [ ! -d "$1" ]; then
    sudo mkdir -p "$1"
  fi
}
echo "███╗   ███╗ ██████╗ ██╗   ██╗██╗███████╗    ██████╗  ██████╗ ████████╗
████╗ ████║██╔═══██╗██║   ██║██║██╔════╝    ██╔══██╗██╔═══██╗╚══██╔══╝
██╔████╔██║██║   ██║██║   ██║██║█████╗      ██████╔╝██║   ██║   ██║
██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██║██╔══╝      ██╔══██╗██║   ██║   ██║
██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ██║███████╗    ██████╔╝╚██████╔╝   ██║
╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚═╝╚══════╝    ╚═════╝  ╚═════╝    ╚═╝
欢迎选择使用Movie Bot，即将开始引导安装程序，请使用y/n来表示是或否"
PUID=0
PGID=0
dockerDataDir=""
while true; do
  read -p "提供一个你存放Docker配置文件的目录吧（这个目录磁盘性能要求较高，最好是SSD，尽量避免和高速下载的区域放在一起）: " dockerDataDir
  if [ -d "$dockerDataDir" ]; then
    break
  else
    echo "文件夹不存在：$dockerDataDir"
  fi
done

mediaDir=""
while true; do
  read -p "下载和整理好的影片你想存放在哪个文件夹？（提供一个空的，足够大的文件目录）: " mediaDir
  if [ -d "$mediaDir" ]; then
    break
  else
    echo "文件夹不存在：$mediaDir"
  fi
done
echo "version: \"3\"

services:" >docker-compose.yml
read -p "你曾经是否安装过种子下载工具qbittorrent: " hasDownloadClient

if [ "$hasDownloadClient" = "n" ]; then
  qbitConfigDir="$dockerDataDir/qbittorrent/config"
  dlDir="$mediaDir/downloads"
  dlTempDir="$mediaDir/downloads_temp"
  ifNotExistsThenCreate "$qbitConfigDir"
  ifNotExistsThenCreate "$dlDir"
  ifNotExistsThenCreate "$dlTempDir"
  echo "  qbittorrent:
    restart: always
    image: linuxserver/qbittorrent:14.3.9
    container_name: qbittorrent
    ports:
      - \"8080:8080\"
    environment:
      WEBUI_PORT: 8080
      PUID: $PUID
      PGID: $PGID
      TZ: Asia/Shanghai
      HOME: /config
      XDG_CONFIG_HOME: /config
      XDG_DATA_HOME: /config
    volumes:
      - $qbitConfigDir:/config
      - $dlDir:/downloads
      - $dlTempDir:/download_temp" >> docker-compose.yml
  echo "即将安装的Docker应用qbittorrent的主要配置如下
  Web访问端口：8080
  PGID: 0 PUID: 0
  配置文件目录为：$qbitConfigDir
  下载保存路径：$dlDir
  下载临时文件夹：$dlTempDir"
fi

read -p "你曾经是否安装过Emby: " hasMediaServer
embyConfigDir=""
if [ "$hasMediaServer" = "n" ]; then
  embyConfigDir="$dockerDataDir/emby_main"
  libraryDir="$mediaDir/library"
  ifNotExistsThenCreate "$embyConfigDir"
  ifNotExistsThenCreate "$libraryDir"
  echo "  emby:
    image: emby/embyserver
    container_name: embyserver
    environment:
      - UID=$PUID
      - GID=$PUID
    volumes:
      - $embyConfigDir:/config
      - $libraryDir:/media
    ports:
      - \"8000:8000\"
      - \"8920:8920\"" >> docker-compose.yml
  echo "即将安装的Docker应用Emby的主要配置如下
    Web访问端口：8000
    UID: 0 GID: 0
    配置文件目录为：$embyConfigDir
    媒体库路径（记住这个路径，配置Emby媒体库时需要）：$libraryDir"
else
  while true; do
    read -p "你的Emby配置文件所在目录是什么: " embyConfigDir
    if [ -d "$embyConfigDir" ]; then
      break
    else
      echo "文件夹不存在：$embyConfigDir"
    fi
  done
fi
read -p "你想要使用MovieBot的什么应用版本，请输入 latest 或 beta : " mbotTag
while true; do
  read -p "请输入你购买的激活码: " licenseKey
  if [ -n "$licenseKey" ]; then
    break
  fi
done
if [ -z "$mbotTag" ]; then
  mbotTag="latest"
fi
mbotDataDir="$dockerDataDir/mbot"
peopleMetaDir="$embyConfigDir/metadata/people"
ifNotExistsThenCreate "$mbotDataDir"
ifNotExistsThenCreate "$peopleMetaDir"
echo "  mbot:
    restart: always
    image: yipengfei/movie-robot:$mbotTag
    container_name: mbot
    ports:
      - 1329:1329
    environment:
      LICENSE_KEY: '$licenseKey'
      PUID: $PUID
      PGID: $PGID
    network_mode: bridge
    volumes:
      - $mbotDataDir:/data
      - $mediaDir:/media
      - $peopleMetaDir:/emby_person" >> docker-compose.yml
echo "即将安装的MovieBot主要配置如下
  Web访问端口：1329
  PUID: 0 PUID: 0
  配置文件目录为：$mbotDataDir
  媒体库路径）：$mediaDir"
sudo docker-compose up -d