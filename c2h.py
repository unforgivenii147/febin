#!/data/data/com.termux/files/usr/bin/env python
def main():
    with open("/sdcard/colors") as file:
        colors = file.readlines()
    colors = [color.strip() for color in colors if color.strip()]
    colors = sorted(set(colors), reverse=True)
    html_content = "<html>\n<head>\n<title>Color Display</title>\n</head>\n<body>\n"
    for color in colors:
        html_content += f'<div style="background-color: {color}; color: white; padding: 10px; margin: 5px; border-radius: 5px;">{color}</div>\n'
    html_content += "</body>\n</html>"
    with open("/sdcard/colors.html", "w") as html_file:
        html_file.write(html_content)
    print("/sdcard/colors.html created")


if __name__ == "__main__":
    main()
