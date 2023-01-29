from collections import defaultdict
import logging

from typing import Any, Dict, List, Optional, Set, Type  # noqa
from offers import implements, AWSOffer

import six

from .constants import (
    REGION_SHORTS,
    EBS_PRODUCT_FAMILY,
    EBS_VOLUME_API_NAME
)


OFFER_CLASS_MAP = {}


logger = logging.getLogger(__name__)


@implements('AmazonEC2')
class EBSOffer(AWSOffer):

    HOURS_IN_YEAR = 24 * 365

    def __init__(self, *args, **kwargs):
        super(EBSOffer, self).__init__(*args, **kwargs)

        self.default_volume_type = None
        self.default_iops = None
        self.default_product_family = 'Storage'
        self.default_storage_media = 'SSD-backed'

        self._reverse_sku = self._generate_reverse_sku_mapping(
            'volumeType', 'storageMedia', 'maxVolumeSize', 'maxIopsvolume',
            'maxThroughputvolume',
            # Both families are queried assuming that instance names will never clash between
            # them. This should be true given metal instance naming conventions thus far (instance
            # size is 'metal').
            product_families=['Storage']
        )

    def get_sku(self,
                volume_type,               # type: str
                product_family=None,       # type: Optional[str]
                storage_media=None,        # type: Optional[str]
                region=None                # type: Optional[str]
                ):
        # type: (...) -> str
        region = self._normalize_region(region)
        if product_family is not None:
            product_family = EBS_PRODUCT_FAMILY[product_family]
        else:
            product_family = self.default_product_family
        storage_media = storage_media or self.default_storage_media

        attributes = [volume_type, product_family, storage_media, region]
        if not all(attributes):
            raise ValueError("All attributes are required: {}"
                             .format(attributes))

        sku = self._reverse_sku.get(self.hash_attributes(*attributes))
        if sku is None:
            raise ValueError("Unable to lookup SKU for attributes: {}"
                             .format(attributes))
        return sku

    def hourly(self,
               volume_type,               # type: str
               product_family=None,       # type: Optional[str]
               storage_media=None,        # type: Optional[str]
               region=None                # type: Optional[str]
               ):
        # type: (...) -> float
        sku = self.get_sku(
            volume_type,
            product_family=product_family,
            storage_media=storage_media,
            region=region
        )
        term = self._offer_data['terms']['OnDemand'][sku]
        price_dimensions = next(six.itervalues(term))['priceDimensions']
        price_dimension = next(six.itervalues(price_dimensions))
        raw_price = price_dimension['pricePerUnit']['USD']
        return float(raw_price)
