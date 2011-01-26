create table Account (
"ACCOUNT_ID" TIMESTAMP default CURRENT_TIMESTAMP not null,
"ACCOUNT_NO" INTEGER not null,
"BALANCE" DECIMAL default 0.0 not null,
"BLOCKING" DECIMAL,
primary key ("ACCOUNT_ID")
);

