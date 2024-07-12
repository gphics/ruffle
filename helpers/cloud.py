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
        method to validate mimemtype
        """
        state = False
        if media_type == "img" and value in self.permitted_img_mimetype:
            state = True
        return state

    def validate_size(self, value, limit=2):
        """
        method to check if the file size value is within the limit range
        """
        limit_b = limit * 1024 * 1024
        state = True
        if value > limit_b:
            state = False
        return state

    def img_validate(self, mimetype, size):
        """
        method for overall img validation
        """
        size_state = self.validate_size(size)
        mimetype_state = self.validate_mimetype(mimetype)
        return {"mimetype": mimetype_state, "size": size_state}

    def get_upload_result(self, upload):
        result = {
            "url": upload["secure_url"],
            "public_id": upload["public_id"],
            "resource_type": upload["resource_type"],
            "format": upload["format"],
        }
        return result

    def img_upload(self, file):
        """
        method to upload images
        """
        # cloudinary.uploader.up
        upload = cloudinary.uploader.upload(file, folder=self.folder)
        return self.get_upload_result(upload)

    def other_upload(self, file):
        upload = cloudinary.uploader.upload_large(
            file, resource_type="auto", folder=self.folder
        )
        return self.get_upload_result(upload)

    def multiple_upload(self, media_list):
        result = []
        for media in media_list:
            mimetype = media.content_type
            if "image" in mimetype:
                first = self.img_upload(media)
                second = self.get_upload_result(first)
                result.append(second)
            else:
                first = self.other_upload(media)
                second = self.get_upload_result(first)
                result.append(second)
        return result

    def destroy(self, public_id):
        """
        methof to delete a file from cloudinary
        """
        cloudinary.uploader.destroy(public_id)

    def multiple_destroy(self, media_list):
        for media in media_list:
            self.destroy(media["public_id"])
