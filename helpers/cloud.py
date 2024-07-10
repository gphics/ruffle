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

    def validate_size(self, value, limit=2):
        """
        method to check if the file size value is within the limit range
        """
        limit_b = limit * 1024 * 1024
        state = True
        if value > limit_b:
            state = False
        return state

    def validate_mimetype(self, value, media_type="img"):
        """
        method to validate mimemtype
        """
        state = False
        if media_type == "img" and value in self.permitted_img_mimetype:
            state = True
        return state

    def img_upload(self, file):
        """
        method to upload images
        """
        upload = cloudinary.uploader.upload(file, folder=self.folder)
        return {"url": upload["secure_url"], "public_id": upload["public_id"]}

    def destroy(self, public_id):
        """
        methof to delete a file from cloudinary
        """
        cloudinary.uploader.destroy(public_id)

    def img_validate(self, mimetype, size):
        """
        method for overall img validation
        """
        size_state = self.validate_size(size)
        mimetype_state = self.validate_mimetype(mimetype)
        return {"mimetype": mimetype_state, "size": size_state}
