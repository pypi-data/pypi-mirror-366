# -*- coding: utf-8 -*-
"""
"""

from getpycomic.imagehandler import ImagesHandler
from getpycomic.requests_data import RequestsData
from getpycomic.pathclass import PathClass

from threading import Thread, Lock

import io

from typing import (
    Literal,
    List,
    Union,
    TypeVar
)


ImageChapter = TypeVar("ImageChapter")
Chapter = TypeVar("Chapter")


class Downloader(Thread):

    def __init__(
        self,
        chunk_chapters: list,
        header: dict,
        sizeImage: Literal["original", "small", "medium", "large"] = "original",
        is_webcomic: bool = False,
        debug: bool = False,
        daemon: bool = True,
        lock: Lock = None,
        index_image: list = None,
        total_images: int = 1,
    ) -> None:
        """
        """
        Thread.__init__(self, daemon=daemon)
        self.imagehandler = ImagesHandler()
        self.chunk_chapters = chunk_chapters
        self.is_webcomic = is_webcomic
        self.sizeImage = sizeImage
        self.header = header
        self.debug = debug

        self.lock = lock
        self.index_image = index_image
        self.total_images = total_images

    def run(self) -> None:
        """
        Gets the images from the URL and saves them.
        """
        if self.debug:
            print(self)

        for chapter in self.chunk_chapters:

            new_images_chapters = []

            for image in chapter.images:
                # image.id
                # image.name
                # image.extension
                # image.link
                # print(image.name, image.extension)

                image.extension = '.jpg'

                if image.path is None:
                    image_path_ = PathClass.join(
                                                chapter.path,
                                                image.get_name()
                                            )
                    image.path = image_path_

                if PathClass.exists(image.path) is False:

                    # get image data from url - io.BytesIO
                    data = RequestsData.request_data(
                                                    header=self.header,
                                                    link=image.link
                                                )

                    if data is not None:

                        if self.is_webcomic:

                            if self.sizeImage == 'original':
                                self.resize_and_save_image(
                                                        data=data,
                                                        imagepath=image.path
                                                    )

                            else:
                                chunks_images = self.crop_images_handler(
                                                    data=data,
                                                    chapterInstance=chapter,
                                                    imageInstance=image,
                                                )
                                # print(image.name)
                                # print(len(chunks_images))
                                # new_images_chapters = []
                                new_images_chapters += chunks_images

                        else:
                            self.resize_and_save_image(
                                                    data=data,
                                                    imagepath=image.path
                                                )

                if self.lock:
                    with self.lock:
                        self.index_image[0] = self.index_image[0] + 1

            # sort images of chapter IF is_webcomic.
            if self.is_webcomic and new_images_chapters != []:
                # print(len(chapter.images), len(new_images_chapters))
                new_images_chapters.sort()
                chapter.update_list_images(images_list=new_images_chapters)
                # print(len(chapter.images), len(new_images_chapters))


    def resize_and_save_image(
        self,
        data: Union[bytes, io.BytesIO],
        imagepath: str,
    ) -> None:
        """
        Resize and save image.

        Args
            data: bytes or io.BytesIO with data of image.
            imagepath: path of image.
        """
        new_image_data_ = self.imagehandler.new_image(
                                    currentImage=data,
                                    extension="jpeg",
                                    sizeImage=self.sizeImage
                                )

        self.imagehandler.save_image(
                                path_image=imagepath,
                                image=new_image_data_
                            )


    def crop_images_handler(
        self,
        data: bytes,
        chapterInstance: Chapter,
        imageInstance: ImageChapter,
    ) -> List[io.BytesIO]:
        """
        Crop large webtoon/webcomic images to the specified size.

        Args
            data: image bytes.
            chapter instance: `Chapter` instance of the current chapter.
            image instance: `ImageChapter` instance of the current image.

        Returns
            list: list of `io.BytesIO` with the resized and cropped image data.
        """
        results = []

        # [io.BytesIO]
        chunks = self.imagehandler.crop(
                            data=data,
                            sizeImage=self.sizeImage,
                        )

        name_, ext_ = PathClass.splitext(imageInstance.path)
        dirname_ = PathClass.dirname(imageInstance.path)

        for i in range(0, len(chunks)):

            if "-" in name_:
                name_, n_chunk = name_.split("-")
                id_ = int(f"{name_}{n_chunk}")
            else:
                id_ = int(f'{name_}{i+1}')

            new_path_image = PathClass.join(
                                dirname_,
                                f'{name_}-{i+1}{ext_}'
                            )

            self.imagehandler.save_image(
                                path_image=new_path_image,
                                image=chunks[i]
                            )

            img_ = chapterInstance.create_image(
                                id=id_,
                                name=imageInstance.name,
                                extension=imageInstance.extension,
                                link=imageInstance.link,
                                path=new_path_image,
                            )

            results.append(img_)
        return results
