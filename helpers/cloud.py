"""
> This module has been deprecated as we have shifted our storage to Amazon s3 bucket but left for legacy purpose
"""

import cloudinary


class Cloud:
    permitted_img_mimetype = (
        "image/jpeg",
        "image/webp",
        "image/png",
        "image/jpg",
        "image/svg",
    )

    def __init__(self, folder):
        self.folder = f"ruffle/{folder}"

    def validate_mimetype(self, value, media_type="img"):
        """
        * method to validate mimemtype
        """
        state = False
        if media_type == "img" and value in self.permitted_img_mimetype:
            state = True
        return state

    def validate_size(self, value, limit=2):
        """
        * method to check if the file size value is within the limit range and the default limit is 2MB
        """
        limit_b = limit * 1024 * 1024
        state = True
        if value > limit_b:
            state = False
        return state

    def img_validate(self, mimetype, size):
        """
        * method for overall img validation
        """
        size_state = self.validate_size(size)
        mimetype_state = self.validate_mimetype(mimetype)
        return {"mimetype": mimetype_state, "size": size_state}

    def get_upload_result(self, upload):
        """
        * method for destructuring the upload response gotten from cloudinary
        * Returned data:
            > public_id
            > resource_type
            > url
            > format
        """

        result = {
            "secure_url": upload["secure_url"],
            "public_id": upload["public_id"],
            "resource_type": upload["resource_type"],
            "format": upload["format"],
        }
        return result

    def img_upload(self, file):
        """
        * method to upload single image
        * this method returns the output of self.get_upload_result
        """
        # cloudinary.uploader.up
        upload = cloudinary.uploader.upload(file, folder=self.folder)
        return self.get_upload_result(upload)

    def other_upload(self, file):
        """
        * method to upload single video/audio
        * this method returns the output of self.get_upload_result
        """
        upload = cloudinary.uploader.upload_large(
            file, resource_type="auto", folder=self.folder
        )
        return self.get_upload_result(upload)

    def validate_other_mimetype(self, mimetype):
        """
        * method for validating mimetype for audio and video
        """
        if "audio" in mimetype:
            return True
        elif "video" in mimetype:
            return True
        else:
            return False

    def multiple_upload(self, media_list):
        """
        * method to upload multiple multimedia files at once
        * this method returns a list containing the output of self.get_upload_result
        * if there is an image file there, it is validated and parsed or rejected
        """
        result = []
        others = []
        imgs = []
        err = None
        for media in media_list:
            mimetype = media.content_type
            if "image" in mimetype and self.validate_mimetype(mimetype):
                imgs.append(media)
            elif "audio" in mimetype and self.validate_other_mimetype(mimetype):
                others.append(media)
            elif "video" in mimetype and self.validate_other_mimetype(mimetype):
                others.append(media)
            else:
                err = f"{mimetype} format is invalid"

        if err:
            return {"err": err, result: None}
        # img uploads
        if len(imgs):
            for img in imgs:
                print("I am called (multiple_upload)")
                first = self.img_upload(img)

                second = self.get_upload_result(first)
                result.append(second)
        if len(others):
            for other in others:
                first = self.img_upload(other)
                print("I am the first", first)
                second = self.get_upload_result(first)
                result.append(second)

        return {"err": None, "result": result}

    def destroy(self, public_id):
        """
        methof to delete a file from cloudinary
        """
        cloudinary.uploader.destroy(public_id)

    def multiple_destroy(self, media_list):
        for media in media_list:
            self.destroy(media["public_id"])
