


class Main:
    """
    * This class is responsible for all file validation operations
    """

    allowed_img_type = (
        "image/jpeg",
        "image/webp",
        "image/png",
        "image/jpg",
        "image/svg",
    )

    default_file_size = 2 * 1024 * 1024
    allowed_unit = ("MB", "GB", "KB")

    def to_byte(self, value):
        """
        * This method convert a value from either mb unit to byte
        * The default unit is mb
        * Value must not be zero
        """
        product = 1024 * 1024 * value
        return product

    def to_mb(self, value):
        """
        * This method convert a value from either mb unit to byte
        * The default unit is mb
        * Value must not be zero
        """

        product = value / 1024 / 1024
        # product = round(value / 1024 / 1024)
        return product
        # return f"{product}mb"

    def validate_img_type(self, content_type):
        """
        * This method receive a content_type parameter and check if it is part of allowed img type
        * if yes, retur True else return False
        """
        if not content_type in self.allowed_img_type:
            return False
        return True

    def validate_file_size(self, file_size, limit=2):
        """
        * This method check if the file_size(bytes) param is below or within the limit
        * The default limit is 2MB
        """
        limit_b = self.to_byte(limit)
        if file_size < limit_b or file_size == limit_b:
            return True
        return False

    def validate_multimedia_type(self, content_type):
        if "audio" in content_type or "video" in content_type:
            return True
        return False

    def validate_allowed_types(self, content_type):
        is_img = self.validate_img_type(content_type)
        is_multimedia = self.validate_multimedia_type(content_type)

        if not is_img and not is_multimedia:
            return False
        return True

    def multiple_validate_allowed_types(self, content_types):
        result = True
        for content_type in content_types:
            state = self.validate_allowed_types(content_type)
            if not state:
                result = state
                break
            else:
                continue
        return result
