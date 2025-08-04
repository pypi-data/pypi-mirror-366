assets2 = "https://github.com/kamangir/assets2/blob/main/bluer-fire"

dict_of_images = {}

items = [
    "[![image]({})]({})".format(image, url if url else image)
    for image, url in dict_of_images.items()
]
