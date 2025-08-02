# url-remote-python-package

# Usage:

`pip install url-remote`

```python
from url_local.url_circlez import UrlCirclez

UrlCirclez.endpoint_url(brand_name=BrandName, environment_name=EnvironmentName,
                        ComponentName.GENDER_DETECTION.value, EntityName.GENDER_DETECTION.value,
                        ANALYZE_FACIAL_IMAGE_API_VERSION[EnvironmentName],
                        ActionName.ANALYZE_FACIAL_IMAGE.value)
# >>> "https://353sstqmj5.execute-api.us-east-1.amazonaws.com/play1/api/v1/gender-detection/analyzeFacialImage"
```

Includes also domain related functions<br>
