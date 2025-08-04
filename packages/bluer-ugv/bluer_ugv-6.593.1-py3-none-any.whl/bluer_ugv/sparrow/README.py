assets2 = "https://github.com/kamangir/assets2/blob/main/bluer-sparrow"

dict_of_images = {
    f"{assets2}/20250722_174115-2.jpg?raw=true": "",
    f"{assets2}/20250729_234927.jpg?raw=true": "",
}

items = [
    "[![image]({})]({})".format(image, url if url else image)
    for image, url in dict_of_images.items()
]
