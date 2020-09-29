DELETE FROM sakshi.stock;
DELETE FROM sakshi.receipt;
ALTER SEQUENCE sakshi.receipt_receipt_id_seq RESTART WITH 1;
ALTER SEQUENCE sakshi.stock_stock_id_seq RESTART WITH 105;