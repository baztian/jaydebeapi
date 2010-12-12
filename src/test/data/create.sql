create table konto (
"KONTO_ID" TIMESTAMP default CURRENT_TIMESTAMP not null,
"KONTO_NR" INTEGER not null,
"SALDO" DECIMAL default 0.0 not null,
"SPERRE" DECIMAL,
primary key ("KONTO_ID")
);

