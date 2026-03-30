ALTER TABLE pharmacy
  ADD COLUMN latitude DECIMAL(9,6) NULL AFTER pincode,
  ADD COLUMN longitude DECIMAL(9,6) NULL AFTER latitude;
