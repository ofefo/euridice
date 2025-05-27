from __future__ import unicode_literals
import youtube_dl, argparse

parser = argparse.ArgumentParser(description='euridice: Extract music scores from videos')
parser.add_argument('link', metavar='LINK', type=str, help='link to the score')
args = parser.parse_args()

ydl_opts = {
         }
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([args.link])
