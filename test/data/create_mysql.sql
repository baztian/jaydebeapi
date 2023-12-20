create table Account (
ACCOUNT_ID TIMESTAMP(6) default CURRENT_TIMESTAMP(6),
ACCOUNT_NO INTEGER not null,
BALANCE DECIMAL(10, 2)  not null default 0.0,
BLOCKING DECIMAL(10, 2),
DBL_COL DOUBLE,
OPENED_AT DATE,
OPENED_AT_TIME TIME,
VALID BOOLEAN,
PRODUCT_NAME VARCHAR(50),
STUFF BLOB,
primary key (ACCOUNT_ID)
);