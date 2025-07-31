# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging


def migrate(cr, version):
    if not version:
        return
    logger = logging.getLogger(__name__)
    logger.info("Updating purchase_order...")
    cr.execute(
        """
    UPDATE
        purchase_order po
    SET
        type_id = t.id
    FROM
        purchase_order_type t
    WHERE
        t.code = 'T0001'
        AND po.type_id IS NULL;
    """
    )
    logger.info("Successfully updated purchase_order tables")
