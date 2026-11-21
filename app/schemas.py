
import re

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ValidationError,
    TypeAdapter,
    field_validator
)


URL_PATTERN = re.compile(
    r"""https?://[^\s<>"']+""",
    re.IGNORECASE
)

url_adapter = TypeAdapter(HttpUrl)


class PostingRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Message containing exactly one CTA link"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):

        # Find HTTP and HTTPS URL candidates
        urls = URL_PATTERN.findall(value)

        if len(urls) == 0:
            if re.search(r"https?://", value, re.IGNORECASE):
                raise ValueError("Invalid URL provided")

            raise ValueError(
                "Message must contain exactly one CTA link"
            )

        if len(urls) > 1:
            raise ValueError(
                "Message must contain exactly one CTA link"
            )

        # Remove punctuation following the URL
        url = urls[0].rstrip(".,!?;:)]}")

        # Validate URL structure
        try:
            url_adapter.validate_python(url)
        except ValidationError:
            raise ValueError("Invalid URL provided")

        return value
