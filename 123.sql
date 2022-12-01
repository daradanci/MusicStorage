CREATE DATABASE `MusicStore` CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON `MusicStore`.* TO Qiqi@'localhost';
use MusicStore;
show tables;
select * from musicstorage_document;
delete from musicstorage_document where id>4;