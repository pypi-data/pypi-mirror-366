assets2 = "https://github.com/kamangir/assets2/blob/main/bluer-eagle"

dict_of_images = {
    f"{assets2}/file_0000000007986246b45343b0c06325dd.png?raw=true": "",
    f"{assets2}/20250727_182113.jpg?raw=true": "",
    f"{assets2}/20250726_171953.jpg?raw=true": "",
}

items = [
    "[![image]({})]({})".format(image, url if url else image)
    for image, url in dict_of_images.items()
]
