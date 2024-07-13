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

    def to_byte(self, value, unit=MB):
        """
        * This method convert a value from either mb | kb | gb unit to byte
        * The default unit is mb
        * Value must not be zero
        """
        product = 0
        if unit == "KB":
            product = 1024 * value
        elif unit == "MB":
            product = 1024 * 1024 * value
        else:
            product = 1024 * 1024 * 1024 * value
        return product

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
