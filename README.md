# Notability Notes To SVG
A simple to tool to convert your Notability note strokes into an SVG wrapped in HTML file.

## Requirements
- Python 3

## Usage
```
$ python main.py example.note
```
The script will output an HTML file.

## Why
I often find my self viewing my notes on my iPad, but sometimes I'd rather view it on my desktop. But there was no simple way to view it outside of my iPad.

## Why don't you export it as a PDF or use Mac OS?
I don't have a Mac. \
You could try to export it to an PDF file, but then you need to either sync it to your cloud storage or send it to yourself via email. \
In my case, I had notability synced up to my Nextcloud instance via WebDAV. \
This means I had direct access to my notes in Nextcloud which allows me to easily convert my notes on Windows.

## Where is this useful?
- View your notes outside of Mac OS or iOS.
- Host your notes online so non-notability users can view it.
- Archiving your notes in an open format so that you can convert it into another format in the future.

## Sources
- Thanks to Julia Evans blog post `Reverse engineering the Notability file format` (https://jvns.ca/blog/2018/03/31/reverse-engineering-notability-format/), I was able to quickly understand how the Notability notes work.
- Thanks to `corpnewt` tool (https://github.com/corpnewt/ProperTree) to view Notability notes I was able to build a quick understanding of the layout of the Apple plist file.
