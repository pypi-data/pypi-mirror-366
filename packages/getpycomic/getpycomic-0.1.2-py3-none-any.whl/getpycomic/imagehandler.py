# -*- coding: utf-8 -*-
"""

Options for resize images.
* 'original' :  original size.
* 'small'     :  800 x 1200.
* 'medium'    :  1000 x 1500.
* 'large'     :  1200 x 1800.
"""

from PIL import Image
import io

from typing import (
        TypeVar,
        Union,
        List,
        Literal
    )

ImageInstancePIL = TypeVar("ImageInstancePIL")


class ImagesHandler:
    """
    Class dealing with image issues, such as resizing.
    """
    validFormats = {
        'JPEG': 'jpeg',
        'PNG': 'png',
        'JPG': 'jpg',
        'WEBP': 'webp',
    }
    sizeImageDict = {
        'original': None,
        'small': (800, 1200),
        'medium': (1000, 1500),
        'large': (1200, 1800),
    }

    @staticmethod
    def get_size(
        size: str = 'original'
    ) -> tuple:
        """
        Returns tuple of size.

        Args
            size: string indicating the new size of the image.

        Returns
            tuple: tuple of int.
        """
        try:
            return ImagesHandler.sizeImageDict[size]
        except KeyError:
            return ImagesHandler.sizeImageDict['small']

    @staticmethod
    def new_image(
        currentImage: bytes,
        extension: str = "jpeg",
        sizeImage: Literal["original", "small", "medium", "large"] = "original",
    ) -> io.BytesIO:
        """
        Resize image.

        Args:
            currentImage: bytes of image.
            extension: extension of new image.
            sizeImage: category of size to resize original image. Default is
                       'original'.

        Returns:
            io.BytesIO: instance io.BytesIO with data of new image.
        """
        size_tuple = ImagesHandler.get_size(size=sizeImage)
        newImageIO = io.BytesIO()

        with Image.open(currentImage) as image_:
            # force image color, RGB.
            image_rbg = image_.convert('RGB')

            if size_tuple is not None:
                imageResized = image_rbg.resize(
                                        size_tuple,
                                        resample=Image.Resampling.LANCZOS
                                    )
            else:
                imageResized = image_rbg

            imageResized.save(
                    newImageIO,
                    format=extension,
                    quality=100
                )

        return newImageIO

    @staticmethod
    def save_image(
        path_image: str,
        image: Union[io.BytesIO, bytes]
    ) -> bool:
        """
        """
        try:
            with open(path_image, 'wb') as file:
                if isinstance(image, io.BytesIO):
                    file.write(image.getvalue())
                elif isinstance(image, bytes):
                    file.write(image)
                return True
        except Exception as e:
            print("Error: ImagesHandler", e)
            return False


    @staticmethod
    def crop(
        data: bytes,
        sizeImage: Literal["original", "small", "medium", "large"] = "original",
    ) -> Union[List[io.BytesIO], list]:
        """
        Crop images to the supported size.

        Args
            data: image data on bytes.
            sizeImage: category of size to resize original image. Default is
                       'original'.
        Returns
            list: list of `io.BytesIO` o empty list.
        """
        if sizeImage == "original":
            return []

        images = []

        size_tuple_final = ImagesHandler.get_size(size=sizeImage)

        # default size to crop large image.
        width_size = size_tuple_final[0]#ImagesHandler.get_size(size='small')[0]
        height_size = size_tuple_final[1]#ImagesHandler.get_size(size='small')[1]

        with Image.open(data) as image_:
            image_ = image_.convert('RGB')

            current_img_width, current_img_height = image_.size

            image_ = image_.resize((width_size, current_img_height))

            sizes_array = [
                        i for i in range(0, current_img_height, height_size)
                    ]

            # print(sizes_array)

            for i in range(len(sizes_array)):
                newImageIO = io.BytesIO()
                try:
                    box = (0, sizes_array[i], width_size, sizes_array[i + 1])
                    chunk = image_.crop(box)

                except IndexError as e:
                    # fills with white background to complete image height size
                    box = (0, sizes_array[i], width_size, current_img_height)
                    chunk = Image.new(
                                    'RGB',
                                    (width_size, height_size),
                                    (255,255,255)
                                )
                    chunk.paste(image_.crop(box), (0, 0))

                # resize to the requested size
                chunk = chunk.resize(size_tuple_final)

                # chunk.show()
                # input()

                chunk.save(
                        newImageIO,
                        format="jpeg",
                        quality=100
                )

                images.append(newImageIO)

        return images
