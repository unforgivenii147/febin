#!/data/data/com.termux/files/usr/bin/python
import pathlib


def main():
    with open("/sdcard/colors", encoding="utf-8") as file:
        colors = file.readlines()
    colors = [color.strip() for color in colors if color.strip()]
    colors = sorted(set(colors), reverse=True)
    html_content = "<html>\n<head>\n<title>Color Display</title>\n</head>\n<body>\n"
    for color in colors:
        html_content += f'<div style="background-color: {color}; color: white; padding: 10px; margin: 5px; border-radius: 5px;">{color}</div>\n'
    html_content += "</body>\n</html>"
    pathlib.Path("/sdcard/colors.html").write_text(html_content, encoding="utf-8")
    print("/sdcard/colors.html created")


if __name__ == "__main__":
    main()
